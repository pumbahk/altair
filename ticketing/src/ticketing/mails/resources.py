# -*- coding:utf-8 -*-

from pyramid.decorator import reify
from ticketing.core import models as c_models
from zope.interface import implementer

from .interfaces import ICompleteMailPayment, ICompleteMailDelivery
from .interfaces import IOrderCancelMailPayment, IOrderCancelMailDelivery
from .api import get_mail_utility

def payment_key(order, k):
    payment_plugin_id  = order.payment_delivery_pair.payment_method.payment_plugin_id
    return "P%s%s" % (payment_plugin_id, k)

def delivery_key(order, k):
    delivery_plugin_id  = order.payment_delivery_pair.delivery_method.delivery_plugin_id
    return "D%s%s" % (delivery_plugin_id, k)


@implementer(ICompleteMailDelivery)
class CompleteMailDelivery(object):
    """ 完了メール delivery
    """
    def __init__(self, request, order):
        self.request = request
        self.order = order

    @reify
    def mailinfo_traverser(self):
        mutil = get_mail_utility(self.request, c_models.MailTypeEnum.CompleteMail)
        return mutil.get_traverser(self.request, self.order)

    def mail_data(self, k):
        return self.mailinfo_traverser.data[delivery_key(self.order, k)]

@implementer(ICompleteMailPayment)
class CompleteMailPayment(object):
    """ 完了メール payment
    """
    def __init__(self, request, order):
        self.request = request
        self.order = order

    @reify
    def mailinfo_traverser(self):
        mutil = get_mail_utility(self.request, c_models.MailTypeEnum.CompleteMail)
        return mutil.get_traverser(self.request, self.order)

    def mail_data(self, k):
        return self.mailinfo_traverser.data[payment_key(self.order, k)]

@implementer(IOrderCancelMailDelivery)
class OrderCancelMailDelivery(object):
    """ キャンセルメール delivery
    """
    def __init__(self, request, order):
        self.request = request
        self.order = order

    @reify
    def mailinfo_traverser(self):
        mutil = get_mail_utility(self.request, c_models.MailTypeEnum.PurchaseCancelMail)
        return mutil.get_traverser(self.request, self.order)

    def mail_data(self, k):
        return self.mailinfo_traverser.data[delivery_key(self.order, k)]

@implementer(IOrderCancelMailPayment)
class OrderCancelMailPayment(object):
    """ キャンセルメール payment
    """
    def __init__(self, request, order):
        self.request = request
        self.order = order

    @reify
    def mailinfo_traverser(self):
        mutil = get_mail_utility(self.request, c_models.MailTypeEnum.PurchaseCancelMail)
        return mutil.get_traverser(self.request, self.order)

    def mail_data(self, k):
        return self.mailinfo_traverser.data[payment_key(self.order, k)]
