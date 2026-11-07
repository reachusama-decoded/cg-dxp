"""Exception hierarchy for the marketplace client."""


class MarketplaceError(Exception):
    """Base for all marketplace-client errors."""


class MarketplaceAuthError(MarketplaceError):
    """Auth-related failures (missing, expired, invalid token)."""


class TokenMissingError(MarketplaceAuthError):
    """No token cached — user must run `marketplace login`."""


class TokenExpiredError(MarketplaceAuthError):
    """Cached token rejected by the API as expired."""


class UnsupportedPlatformError(MarketplaceError):
    """Entity uses a platform whose access endpoint isn't yet implemented."""

    def __init__(self, platform: str) -> None:
        self.platform = platform
        super().__init__(
            f"Marketplace platform {platform!r} is not yet supported. "
            "A targeted sniff of its access endpoint is needed; "
            "see spike/marketplace/findings.md for the procedure."
        )
