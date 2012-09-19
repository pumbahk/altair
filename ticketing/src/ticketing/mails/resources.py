from .interfaces import ICompleteMailPayment, ICompleteMailDelivery
from .interfaces import IOrderCancelMailPayment, IOrderCancelMailDelivery
from zope.interface import implementer

@implementer(ICompleteMailDelivery)
class CompleteMailDelivery(object):
    def __init__(self, order):
        self.order = order

@implementer(ICompleteMailPayment)
class CompleteMailPayment(object):
    def __init__(self, order):
        self.order = order

@implementer(IOrderCancelMailPayment)
class OrderCancelMailPayment(object):
    def __init__(self, order):
        self.order = order

@implementer(IOrderCancelMailDelivery)
class OrderCancelMailDelivery(object):
    def __init__(self, order):
        self.order = order
