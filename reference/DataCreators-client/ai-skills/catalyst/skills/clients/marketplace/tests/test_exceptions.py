from skills.clients.marketplace import exceptions as exc


def test_marketplace_error_is_base():
    e = exc.MarketplaceError("boom")
    assert str(e) == "boom"


def test_auth_error_is_marketplace_error():
    assert issubclass(exc.MarketplaceAuthError, exc.MarketplaceError)


def test_unsupported_platform_error_carries_platform_code():
    e = exc.UnsupportedPlatformError("SNOWFLAKE")
    assert e.platform == "SNOWFLAKE"
    assert "SNOWFLAKE" in str(e)


def test_token_missing_error_is_auth_error():
    assert issubclass(exc.TokenMissingError, exc.MarketplaceAuthError)


def test_token_expired_error_is_auth_error():
    assert issubclass(exc.TokenExpiredError, exc.MarketplaceAuthError)
