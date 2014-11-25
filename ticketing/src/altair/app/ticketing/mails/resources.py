# -*- coding:utf-8 -*-

from pyramid.decorator import reify
from altair.app.ticketing.core import models as c_models
from zope.interface import implementer, provider

from .interfaces import IMailDataStoreGetter
from .api import get_mail_utility

@provider(IMailDataStoreGetter)
def get_mail_data_store(request, order, mtype):
    mutil = get_mail_utility(request, mtype)
    return mutil.get_traverser(request, order).data

class MailContextBase(object):
    def build_key(self, category, k):
        pdmp = self.payment_delivery_method_pair
        if category == 'P':
            return "P%s%s" % (pdmp.payment_method.payment_plugin_id, k)
        elif category == 'D':
            return "D%s%s" % (pdmp.delivery_method.delivery_plugin_id, k)
        else:
            raise ValueError('unknown category: %s' % category)

    def mail_data(self, category, k):
        return self.mail_data_store[self.build_key(category, k)]


class MailForOrderContext(MailContextBase):
    mtype = None

    def __init__(self, request, order):
        self.request = request
        self.order = order

    @property
    def payment_delivery_method_pair(self):
        return self.order.payment_delivery_pair

    @reify
    def mail_data_store(self):
        getter = self.request.registry.getUtility(IMailDataStoreGetter)
        return getter(self.request, self.order, self.__class__.mtype)

class MailForLotContext(MailContextBase):
    mtype = None

    def __init__(self, request, (lot_entry, elected_wish)):
        self.request = request
        self.lot_entry = lot_entry
        self.elected_wish = elected_wish

    @property
    def payment_delivery_method_pair(self):
        return self.lot_entry.payment_delivery_method_pair

    @reify
    def mail_data_store(self):
        getter = self.request.registry.getUtility(IMailDataStoreGetter)
        return getter(self.request, self.lot_entry, self.__class__.mtype)
