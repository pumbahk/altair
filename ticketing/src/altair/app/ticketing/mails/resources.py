# -*- coding:utf-8 -*-

from pyramid.decorator import reify
from altair.app.ticketing.core import models as c_models
from zope.interface import implementer

from .interfaces import ICompleteMailPayment, ICompleteMailDelivery
from .interfaces import IOrderCancelMailPayment, IOrderCancelMailDelivery
from .interfaces import ILotsAcceptedMailPayment, ILotsAcceptedMailDelivery
from .interfaces import ILotsElectedMailPayment, ILotsElectedMailDelivery
from .interfaces import ILotsRejectedMailPayment, ILotsRejectedMailDelivery
from .api import get_mail_utility

def payment_key(order, k):
    payment_plugin_id  = order.payment_delivery_pair.payment_method.payment_plugin_id
    return "P%s%s" % (payment_plugin_id, k)

def delivery_key(order, k):
    delivery_plugin_id  = order.payment_delivery_pair.delivery_method.delivery_plugin_id
    return "D%s%s" % (delivery_plugin_id, k)


class MailForOrderContext(object):
    mtype = None
    get_key = None
    def __init__(self, request, order):
        self.request = request
        self.order = order

    @reify
    def mailinfo_traverser(self):
        mutil = get_mail_utility(self.request, self.__class__.mtype)
        return mutil.get_traverser(self.request, self.order)

    def mail_data(self, k):
        return self.mailinfo_traverser.data[self.__class__.get_key(self.order, k)]

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
