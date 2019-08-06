class RakutenLiveApiRequestFailed(Exception):
    """Base Exception for Rakuten Live API exceptions."""
    pass


class RakutenLiveApiInternalServerError(RakutenLiveApiRequestFailed):
    """Rakuten Live API returned Internal server error code."""
    pass


class RakutenLiveApiAccessTokenInvalid(RakutenLiveApiRequestFailed):
    """Rakuten Live API returned AccessTokenInvalid code."""
    pass
