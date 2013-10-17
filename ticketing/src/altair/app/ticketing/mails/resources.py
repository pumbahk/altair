# -*- coding:utf-8 -*-

from pyramid.decorator import reify
from altair.app.ticketing.core import models as c_models
from zope.interface import implementer, provider

from .interfaces import ICompleteMailPayment, ICompleteMailDelivery
from .interfaces import IOrderCancelMailPayment, IOrderCancelMailDelivery
from .interfaces import ILotsAcceptedMailPayment, ILotsAcceptedMailDelivery
from .interfaces import ILotsElectedMailPayment, ILotsElectedMailDelivery
from .interfaces import ILotsRejectedMailPayment, ILotsRejectedMailDelivery
from .interfaces import IMailDataStoreGetter
from .api import get_mail_utility

def payment_key(order, k):
    payment_plugin_id  = order.payment_delivery_pair.payment_method.payment_plugin_id
    return "P%s%s" % (payment_plugin_id, k)

def delivery_key(order, k):
    delivery_plugin_id  = order.payment_delivery_pair.delivery_method.delivery_plugin_id
    return "D%s%s" % (delivery_plugin_id, k)


@provider(IMailDataStoreGetter)
def get_mail_data_store(request, order, mtype):
    mutil = get_mail_utility(request, mtype)
    return mutil.get_traverser(request, order).data
    
class MailForOrderContext(object):
    mtype = None
    get_key = None
    def __init__(self, request, order):
        self.request = request
        self.order = order

    @reify
    def mail_data_store(self):
        getter = self.request.registry.getUtility(IMailDataStoreGetter)
        return getter(self.request, self.order, self.__class__.mtype)

    def mail_data(self, k):
        return self.mail_data_store[self.__class__.get_key(self.order, k)]

@implementer(ICompleteMailDelivery)
class PurchaseCompleteMailDelivery(MailForOrderContext):
    """ 完了メール delivery
    """
    mtype = c_models.MailTypeEnum.PurchaseCompleteMail
    get_key = staticmethod(delivery_key)

@implementer(ICompleteMailPayment)
class PurchaseCompleteMailPayment(MailForOrderContext):
    """ 完了メール payment
    """
    mtype = c_models.MailTypeEnum.PurchaseCompleteMail
    get_key = staticmethod(payment_key)

@implementer(IOrderCancelMailDelivery)
class OrderCancelMailDelivery(MailForOrderContext):
    """ キャンセルメール delivery
    """
    mtype = c_models.MailTypeEnum.PurchaseCancelMail
    get_key = staticmethod(delivery_key)

@implementer(IOrderCancelMailPayment)
class OrderCancelMailPayment(MailForOrderContext):
    """ キャンセルメール payment
    """
    mtype = c_models.MailTypeEnum.PurchaseCancelMail
    get_key = staticmethod(payment_key)

@implementer(ILotsAcceptedMailDelivery)
class LotsAcceptedMailDelivery(MailForOrderContext):
    """ 申し込み完了メール delivery
    """
    mtype = c_models.MailTypeEnum.PurchaseCancelMail
    get_key = staticmethod(delivery_key)

@implementer(ILotsAcceptedMailPayment)
class LotsAcceptedMailPayment(MailForOrderContext):
    """ 申し込み完了メール payment
    """
    mtype = c_models.MailTypeEnum.PurchaseCancelMail
    get_key = staticmethod(payment_key)

@implementer(ILotsElectedMailDelivery)
class LotsElectedMailDelivery(MailForOrderContext):
    """ 当選メール delivery
    """
    mtype = c_models.MailTypeEnum.PurchaseCancelMail
    get_key = staticmethod(delivery_key)

@implementer(ILotsElectedMailPayment)
class LotsElectedMailPayment(MailForOrderContext):
    """ 当選メール payment
    """
    mtype = c_models.MailTypeEnum.PurchaseCancelMail
    get_key = staticmethod(payment_key)

@implementer(ILotsRejectedMailDelivery)
class LotsRejectedMailDelivery(MailForOrderContext):
    """ 落選メール delivery
    """
    mtype = c_models.MailTypeEnum.PurchaseCancelMail
    get_key = staticmethod(delivery_key)

@implementer(ILotsRejectedMailPayment)
class LotsRejectedMailPayment(MailForOrderContext):
    """ 落選メール payment
    """
    mtype = c_models.MailTypeEnum.PurchaseCancelMail
    get_key = staticmethod(payment_key)
