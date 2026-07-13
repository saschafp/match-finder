class MatchcenterError(RuntimeError):
    """Base exception for Matchcenter operations."""


class MatchcenterFetchError(MatchcenterError):
    """Raised when a Matchcenter page cannot be fetched."""


class MatchcenterDiscoveryError(MatchcenterError):
    """Raised when schedule pages cannot be discovered."""


class MatchcenterParserError(MatchcenterError):
    """Raised when schedule HTML cannot be parsed."""


class MatchcenterExportError(MatchcenterError):
    """Raised when games cannot be exported."""
