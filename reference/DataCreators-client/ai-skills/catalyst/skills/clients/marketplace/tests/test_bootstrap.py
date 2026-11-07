import json
from unittest.mock import MagicMock, patch

import pytest

from skills.clients.marketplace import bootstrap, exceptions as exc

# Fixture policy: helpers that build localStorage payloads should explicitly
# state whether the token is fresh or stale. The legacy `_fake_localstorage`
# helper exists for back-compat and assumes a far-future expiry, but new
# tests should use `_fresh_localstorage` or `_stale_localstorage` so the
# token's freshness state is visible at the call site. This is to prevent
# repeating the bug where every mock token was implicitly "fresh forever"
# and stale-token paths went untested.


def _fake_localstorage(token_value):
    """Build a fake localStorage dict with the OIDC token client-storage shape."""
    return {
        "okta-token-storage": json.dumps({
            "accessToken": {
                "accessToken": token_value,
                "expiresAt": 9999999999,
                "tokenType": "Bearer",
            }
        }),
    }


def test_extract_bearer_from_localstorage_known_key():
    storage = _fake_localstorage("eyXXXXX")
    bearer = bootstrap.extract_bearer(storage)
    assert bearer == "Bearer eyXXXXX"


def test_extract_bearer_missing_key_raises_helpful():
    with pytest.raises(exc.MarketplaceAuthError) as ei:
        bootstrap.extract_bearer({})
    assert "okta-token-storage" in str(ei.value)


def test_extract_bearer_malformed_storage_raises():
    with pytest.raises(exc.MarketplaceAuthError):
        bootstrap.extract_bearer({"okta-token-storage": "not-json"})


def test_extract_api_base_url_from_env_vars_response():
    body = (
        'window.__ENV__={"REACT_APP_EAST_BASE_URL":"https://api.example.com",'
        '"REACT_APP_ENV":"prod"}'
    )
    url = bootstrap.extract_api_base_url(body)
    assert url == "https://api.example.com"


def test_extract_api_base_url_missing_falls_back_to_default():
    body = "window.__ENV__={\"REACT_APP_ENV\":\"prod\"}"
    url = bootstrap.extract_api_base_url(body)
    assert url == bootstrap.DEFAULT_API_BASE_URL


@patch("skills.clients.marketplace.bootstrap.sync_playwright")
def test_login_writes_token_after_extraction(mock_sync_pw, isolated_config_dir):
    """End-to-end mock: Playwright is fully stubbed; assert save_token is called."""
    fake_ctx = MagicMock()
    fake_page = MagicMock()
    fake_ctx.new_page.return_value = fake_page

    fake_page.evaluate.return_value = _fake_localstorage("eyTOKEN")
    fake_response = MagicMock()
    fake_response.text = lambda: 'window.__ENV__={"REACT_APP_EAST_BASE_URL":"https://api.example.com"}'
    fake_page.goto.return_value = fake_response

    fake_pw = MagicMock()
    fake_pw.chromium.launch_persistent_context.return_value = fake_ctx
    mock_sync_pw.return_value.__enter__.return_value = fake_pw

    bootstrap.login(wait_for_close=False)

    from skills.clients.marketplace import auth
    tok = auth.load_token()
    assert tok is not None
    assert tok.bearer == "Bearer eyTOKEN"
    assert tok.api_base_url == "https://api.example.com"


def test_poll_for_bearer_returns_token_when_available():
    """If localStorage already has the token, _poll_for_bearer returns immediately."""
    fake_page = MagicMock()
    fake_page.evaluate.return_value = _fake_localstorage("eyREADY")
    bearer = bootstrap._poll_for_bearer(fake_page, interval=0.01, timeout=2.0)
    assert bearer == "Bearer eyREADY"


def test_poll_for_bearer_waits_then_returns():
    """If token appears later, _poll_for_bearer waits for it."""
    fake_page = MagicMock()
    # First two calls return empty storage; third call returns the token.
    fake_page.evaluate.side_effect = [
        {},
        {},
        _fake_localstorage("eyLATE"),
    ]
    bearer = bootstrap._poll_for_bearer(fake_page, interval=0.01, timeout=2.0)
    assert bearer == "Bearer eyLATE"


def test_poll_for_bearer_times_out():
    """If token never appears, _poll_for_bearer raises MarketplaceAuthError."""
    fake_page = MagicMock()
    fake_page.evaluate.return_value = {}  # always empty
    with pytest.raises(exc.MarketplaceAuthError) as ei:
        bootstrap._poll_for_bearer(fake_page, interval=0.01, timeout=0.05)
    assert "Timed out" in str(ei.value)


def test_poll_for_bearer_tolerates_navigation_error():
    """If page.evaluate raises during navigation, polling continues until success."""
    import sys
    import types

    fake_page = MagicMock()

    # Inject a fake playwright.sync_api module so _poll_for_bearer's local import
    # resolves to a class we control (avoids requiring playwright to be installed).
    class FakePlaywrightError(Exception):
        pass

    fake_pw_module = types.ModuleType("playwright.sync_api")
    fake_pw_module.Error = FakePlaywrightError

    # evaluate raises twice (mid-navigation), succeeds on the third call.
    fake_page.evaluate.side_effect = [
        FakePlaywrightError("Execution context was destroyed"),
        FakePlaywrightError("Execution context was destroyed"),
        _fake_localstorage("eyAFTERNAV"),
    ]

    with patch.dict(sys.modules, {"playwright.sync_api": fake_pw_module}):
        bearer = bootstrap._poll_for_bearer(fake_page, interval=0.01, timeout=2.0)

    assert bearer == "Bearer eyAFTERNAV"


def _fake_localstorage_with_expiry(token_value, expires_at):
    """localStorage shape with explicit expiresAt."""
    return {
        "okta-token-storage": json.dumps({
            "accessToken": {
                "accessToken": token_value,
                "expiresAt": expires_at,
                "tokenType": "Bearer",
            }
        }),
    }


def test_extract_bearer_rejects_expired_token():
    """Tokens whose expiresAt is in the past should raise (so poller keeps waiting)."""
    import time
    expired_at = int(time.time()) - 3600  # 1h ago
    storage = _fake_localstorage_with_expiry("eyOLD", expired_at)
    with pytest.raises(exc.MarketplaceAuthError) as ei:
        bootstrap.extract_bearer(storage)
    assert "expired" in str(ei.value).lower()


def test_extract_bearer_accepts_fresh_token():
    """Tokens with future expiresAt should be returned."""
    import time
    fresh_exp = int(time.time()) + 3600  # 1h from now
    storage = _fake_localstorage_with_expiry("eyFRESH", fresh_exp)
    bearer = bootstrap.extract_bearer(storage)
    assert bearer == "Bearer eyFRESH"


def test_extract_bearer_falls_back_to_jwt_exp_when_bundle_missing_expiresAt():
    """When the bundle has no expiresAt field, decode the JWT's exp claim."""
    import time
    import base64
    # Build a fake JWT with an exp claim 1h in the future.
    fresh_exp = int(time.time()) + 3600
    header = base64.urlsafe_b64encode(b'{"alg":"RS256"}').rstrip(b"=").decode()
    payload = base64.urlsafe_b64encode(
        json.dumps({"exp": fresh_exp, "sub": "x"}).encode()
    ).rstrip(b"=").decode()
    jwt = f"ey{header[2:]}.{payload}.fakesig"  # ensure starts with "ey"
    # Build storage with no expiresAt
    storage = {
        "okta-token-storage": json.dumps({
            "accessToken": {"accessToken": jwt, "tokenType": "Bearer"}
        }),
    }
    bearer = bootstrap.extract_bearer(storage)
    assert bearer == f"Bearer {jwt}"


def test_jwt_exp_returns_none_on_garbage():
    """_jwt_exp must not blow up on non-JWT input."""
    assert bootstrap._jwt_exp("not.a.jwt") is None
    assert bootstrap._jwt_exp("only-one-part") is None
    assert bootstrap._jwt_exp("a.b.c.d") is None


def _fresh_localstorage(token_value="eyFRESH", expires_in_seconds=3600):
    """localStorage with a token that expires in the future (default 1h)."""
    import time
    return {
        "okta-token-storage": json.dumps({
            "accessToken": {
                "accessToken": token_value,
                "expiresAt": int(time.time()) + expires_in_seconds,
                "tokenType": "Bearer",
            }
        }),
    }


def _stale_localstorage(token_value="eySTALE", expired_seconds_ago=3600):
    """localStorage with a token that expired in the past (default 1h ago)."""
    import time
    return {
        "okta-token-storage": json.dumps({
            "accessToken": {
                "accessToken": token_value,
                "expiresAt": int(time.time()) - expired_seconds_ago,
                "tokenType": "Bearer",
            }
        }),
    }


# ===== state-space tests: persistent localStorage in unexpected shapes =====

@patch("skills.clients.marketplace.bootstrap.sync_playwright")
def test_login_clears_stale_localstorage_before_polling(mock_sync_pw, isolated_config_dir):
    """login() must call removeItem + reload BEFORE polling — otherwise it
    captures stale tokens left over from a prior session.
    """
    fake_ctx = MagicMock()
    fake_page = MagicMock()
    fake_ctx.new_page.return_value = fake_page
    fake_page.evaluate.side_effect = [
        None,  # removeItem call
        _fresh_localstorage("eyAFTERCLEAR"),  # poll #1
    ]
    fake_response = MagicMock()
    fake_response.text = lambda: 'window.__ENV__={"REACT_APP_EAST_BASE_URL":"https://api.example.com"}'
    fake_page.goto.return_value = fake_response
    fake_pw = MagicMock()
    fake_pw.chromium.launch_persistent_context.return_value = fake_ctx
    mock_sync_pw.return_value.__enter__.return_value = fake_pw

    bootstrap.login(poll_interval=0.01, poll_timeout=2.0)

    first_call = fake_page.evaluate.call_args_list[0]
    assert "removeItem" in first_call.args[0], (
        f"Expected first evaluate to clear localStorage, got: {first_call.args[0][:80]}"
    )
    assert fake_page.reload.called, "login should reload the page after clearing localStorage"


@patch("skills.clients.marketplace.bootstrap.sync_playwright")
def test_login_rejects_stale_token_keeps_polling_until_fresh(mock_sync_pw, isolated_config_dir):
    """If the SPA hands us a stale token first, the poller must reject it and wait."""
    fake_ctx = MagicMock()
    fake_page = MagicMock()
    fake_ctx.new_page.return_value = fake_page
    fake_page.evaluate.side_effect = [
        None,                                   # removeItem
        _stale_localstorage("eyOLDONE"),        # poll #1: stale
        _stale_localstorage("eyOLDTWO"),        # poll #2: still stale
        _fresh_localstorage("eyFINALLYFRESH"),  # poll #3: fresh
    ]
    fake_response = MagicMock()
    fake_response.text = lambda: 'window.__ENV__={"REACT_APP_EAST_BASE_URL":"https://api.example.com"}'
    fake_page.goto.return_value = fake_response
    fake_pw = MagicMock()
    fake_pw.chromium.launch_persistent_context.return_value = fake_ctx
    mock_sync_pw.return_value.__enter__.return_value = fake_pw

    bootstrap.login(poll_interval=0.01, poll_timeout=2.0)

    from skills.clients.marketplace import auth
    tok = auth.load_token()
    assert tok is not None
    assert tok.bearer == "Bearer eyFINALLYFRESH", (
        f"Expected the FRESH token to be saved, got: {tok.bearer[:30]}"
    )


def test_extract_bearer_handles_missing_accesstoken_subobject():
    """Bundle exists but `accessToken` key is missing entirely."""
    storage = {"okta-token-storage": json.dumps({"someOtherKey": "value"})}
    with pytest.raises(exc.MarketplaceAuthError):
        bootstrap.extract_bearer(storage)


def test_extract_bearer_handles_accesstoken_with_no_inner_token():
    """`accessToken` subobject exists but inner `accessToken` field missing."""
    storage = {"okta-token-storage": json.dumps({"accessToken": {"tokenType": "Bearer"}})}
    with pytest.raises(exc.MarketplaceAuthError):
        bootstrap.extract_bearer(storage)


def test_extract_bearer_handles_token_not_starting_with_ey():
    """Defensive: any non-JWT-shaped value should raise."""
    storage = {"okta-token-storage": json.dumps({
        "accessToken": {"accessToken": "obviously-not-a-jwt", "expiresAt": 9999999999}
    })}
    with pytest.raises(exc.MarketplaceAuthError):
        bootstrap.extract_bearer(storage)


def test_extract_bearer_token_expiring_in_one_second_still_passes():
    """Boundary: token with exp == now+1 should pass."""
    import time
    storage = {"okta-token-storage": json.dumps({
        "accessToken": {"accessToken": "eyVALID", "expiresAt": int(time.time()) + 1}
    })}
    bearer = bootstrap.extract_bearer(storage)
    assert bearer == "Bearer eyVALID"


def test_extract_bearer_token_at_exact_current_time_is_rejected():
    """Boundary: token with exp <= now should be rejected."""
    import time
    storage = {"okta-token-storage": json.dumps({
        "accessToken": {"accessToken": "eyEXPIRED", "expiresAt": int(time.time())}
    })}
    with pytest.raises(exc.MarketplaceAuthError):
        bootstrap.extract_bearer(storage)
