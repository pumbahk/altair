# -*- coding: utf-8 -*-

from zope.interface import Interface, Attribute


class IFamiPortOrderAutoCompleter(Interface):
    def complete(session, receipt_id):
        pass


class IReceiptEvent(Interface):
    famiport_receipt = Attribute('')


class IReceiptInquired(IReceiptEvent):
    pass


class IReceiptPaymentRequestReceived(IReceiptEvent):
    pass


class IReceiptCompleted(IReceiptEvent):
    pass


class IReceiptVoided(IReceiptEvent):
    pass


class IReceiptCanceled(IReceiptEvent):
    pass

class IOrderCanceled(Interface):
    famiport_order = Attribute('')
