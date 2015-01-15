# encoding: utf-8

class MultiCheckoutError(Exception):
    pass

class MultiCheckoutGenericError(MultiCheckoutError):
    pass

class MultiCheckoutAPIError(MultiCheckoutError):
    pass

class MultiCheckoutAPITimeoutError(MultiCheckoutError):
    pass
