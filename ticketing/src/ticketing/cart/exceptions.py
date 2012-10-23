# encoding: utf-8

class CartException(Exception):
    pass

class NoCartError(CartException):
    pass

class NoEventError(CartException):
    pass

class NoPerformanceError(CartException):
    pass

class NoSalesSegment(CartException):
    pass

class OutTermSalesException(CartException):
    """ 期限外の販売区分に対するアクセス"""
    def __init__(self, event, sales_segment):
        Exception.__init__(self)
        self.event = event
        self.sales_segment = sales_segment

class InvalidCSRFTokenException(Exception):
    pass

class OverQuantityLimitError(CartException):
    def __init__(self, upper_limit):
        Exception.__init__(self)
        self.upper_limit = upper_limit

class ZeroQuantityError(CartException):
    pass

class CartCreationExceptoion(CartException):
    pass
