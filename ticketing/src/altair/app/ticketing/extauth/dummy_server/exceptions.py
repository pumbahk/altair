class RequestHandlerError(Exception):
    pass

class UnsupportedFlavor(RequestHandlerError):
    pass

class BadRequestError(RequestHandlerError):
    pass

class BadParamError(BadRequestError):
    pass
