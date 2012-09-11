# -*- coding:utf-8 -*-

from pyramid.view import view_config
from zope.interface import implementer
from ..interfaces import IOrderDelivery, ICartDelivery, ICompleteMailDelivery
from . import models as m
from . import logger
import qrcode
import StringIO
import ticketing.qr
from ticketing.cart import helpers as cart_helper
from ticketing.core import models as c_models
from ticketing.mails.api import get_mail_utility
from ticketing.mails.forms import MailInfoTemplate

DELIVERY_PLUGIN_ID = 4

def includeme(config):
    config.add_delivery_plugin(QRTicketDeliveryPlugin(), DELIVERY_PLUGIN_ID)
    config.scan(__name__)

@view_config(context=ICartDelivery, name="delivery-%d" % DELIVERY_PLUGIN_ID, renderer="ticketing.cart.plugins:templates/qr_confirm.html")
def deliver_confirm_viewlet(context, request):
    return dict()

@view_config(context=IOrderDelivery, name="delivery-%d" % DELIVERY_PLUGIN_ID, renderer="ticketing.cart.plugins:templates/qr_complete.html")
def deliver_completion_viewlet(context, request):
    return dict()

@view_config(context=ICompleteMailDelivery, name="delivery-%d" % DELIVERY_PLUGIN_ID, renderer="ticketing.cart.plugins:templates/qr_mail_complete.html")
def deliver_completion_mail_viewlet(context, request):
    shipping_address = context.order.shipping_address
    mutil = get_mail_utility(request, c_models.MailTypeEnum.CompleteMail)
    trv = mutil.get_traverser(request, context.order)
    return dict(h=cart_helper, shipping_address=shipping_address, 
                notice=trv.data[MailInfoTemplate.delivery_key(context.order, "notice")]
                )


class QRTicketDeliveryPlugin(object):
    def prepare(self, request, cart):
        """ 前処理 """

    def finish(self, request, cart):
        """ 確定時処理 """
        pass
