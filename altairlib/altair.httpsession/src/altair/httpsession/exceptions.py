__all__ = [
    'HTTPSessionError',
    'NoSuchSession',
    'SessionAlreadyExists',
    'SessionExpired',
    ]

class HTTPSessionError(Exception):
    pass


class NoSuchSession(HTTPSessionError):
    pass


class SessionAlreadyExists(HTTPSessionError):
    pass


class SessionExpired(HTTPSessionError):
    pass


