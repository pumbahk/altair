# encoding: utf-8

class CartException(Exception):
    pass

class NoCartError(CartException):
    pass

class NoEventError(CartException):
    pass

class NoPerformanceError(CartException):
    def __init__(self, event_id=None, sales_segment_group_id=None):
        CartException.__init__(self, event_id, sales_segment_group_id)

class NoSalesSegment(CartException):
    pass

class OutTermSalesException(CartException):
    """ 期限外の販売区分に対するアクセス"""
    def __init__(self, next, last, outer):
        Exception.__init__(self)
        self.next = next
        self.last = last
        self.outer = outer

class InvalidCSRFTokenException(Exception):
    pass

class OverQuantityLimitError(CartException):
    def __init__(self, upper_limit):
        Exception.__init__(self)
        self.upper_limit = upper_limit

class ZeroQuantityError(CartException):
    pass

class CartCreationException(CartException):
    pass

class DeliveryFailedException(Exception):
    def __init__(self, order_no, event_id):
        self.order_no = order_no
        self.event_id = event_id

class UnassignedOrderNumberError(CartException):
    def __init__(self, cart_id):
        self.cart_id = cart_id

class InvalidCartStatusError(CartException):
    def __init__(self, cart_id=None):
        self.cart_id = cart_id

class OverOrderLimitException(Exception):
    def __init__(self, event_id, event_name, performance_name, order_limit):
        self.event_id = event_id
        self.event_name = event_name
        self.performance_name = performance_name
        self.order_limit = order_limit

class PaymentMethodEmptyError(CartException):
    pass
