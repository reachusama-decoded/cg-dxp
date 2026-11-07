import os
import pytest

pytestmark = pytest.mark.integration


@pytest.mark.skipif(os.environ.get("CERT_INTEGRATION_TESTS") != "1",
                    reason="live challenge checks require CERT_INTEGRATION_TESTS=1")
def test_live_suite_is_gated() -> None:
    # Placeholder that only runs under the live gate; real live checks land in Tasks 7,8,10,11.
    assert os.environ["CERT_INTEGRATION_TESTS"] == "1"
