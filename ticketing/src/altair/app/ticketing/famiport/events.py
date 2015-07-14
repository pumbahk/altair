from zope.interface import implementer
from .interfaces import IReceiptInquired, IReceiptPaymentRequestReceived, IReceiptCompleted, IReceiptVoided, IReceiptCanceled, IOrderCanceled

class ReceiptEventBase(object):
    def __init__(self, famiport_receipt, request):
        self.famiport_receipt = famiport_receipt
        self.request = request

@implementer(IReceiptInquired)
class ReceiptInquired(ReceiptEventBase):
    pass

@implementer(IReceiptPaymentRequestReceived)
class ReceiptPaymentRequestReceived(ReceiptEventBase):
    pass

@implementer(IReceiptCompleted)
class ReceiptCompleted(ReceiptEventBase):
    pass

@implementer(IReceiptVoided)
class ReceiptVoided(ReceiptEventBase):
    pass

@implementer(IReceiptCanceled)
class ReceiptCanceled(ReceiptEventBase):
    pass

class OrderEventBase(object):
    def __init__(self, famiport_order, request):
        self.famiport_order = famiport_order
        self.request = request

@implementer(IOrderCanceled)
class OrderCanceled(OrderEventBase):
    def __init__(self, famiport_order, request):
        self.famiport_order = famiport_order
        self.request = request
