# -*- coding:utf-8 -*-

from pyramid.view import view_config
from zope.interface import implementer
from ..interfaces import IOrderDelivery, ICartDelivery, ICompleteMailDelivery
from . import models as m
from ticketing.core import models as core_models
from . import logger
import qrcode
import StringIO
from ticketing.qr import qr
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

builder = qr()
builder.key = u"THISISIMPORTANTSECRET"

@view_config(context=IOrderDelivery, name="delivery-%d" % DELIVERY_PLUGIN_ID, renderer="ticketing.cart.plugins:templates/qr_complete.html")
@view_config(context=IOrderDelivery, name="delivery-%d-mobile" % DELIVERY_PLUGIN_ID, renderer="ticketing.cart.plugins:templates/qr_complete_mobile.html")
def deliver_completion_viewlet(context, request):
    tickets = [ ]
    order = context.order
    for op in order.ordered_products:
        for opi in op.ordered_product_items:
            for s in opi.seats:
                # 発行済みかどうかを取得
                history = core_models.TicketPrintHistory.filter_by(ordered_product_item_id = opi.id, seat_id = s.id).first()
                class QRTicket:
                    order = context.order
                    performance = context.order.performance
                    product = op.product
                    seat = s
                    printed_at = history.created_at if history else ''
                ticket = QRTicket()
                tickets.append(ticket)
    
    # TODO: orderreviewから呼ばれた場合とcartの完了画面で呼ばれた場合で
    # 処理を分岐したい
    
    return dict(
        paid = (order.paid_at != None),
        order = order,
        tel = order.shipping_address.tel_1,
        tickets = tickets,
        )

@view_config(context=ICompleteMailDelivery, name="delivery-%d" % DELIVERY_PLUGIN_ID, renderer="ticketing.cart.plugins:templates/qr_mail_complete.html")
def deliver_completion_mail_viewlet(context, request):
    shipping_address = context.order.shipping_address
    mutil = get_mail_utility(request, c_models.MailTypeEnum.CompleteMail)
    trv = mutil.get_traverser(request, context.order)
    return dict(h=cart_helper, shipping_address=shipping_address, 
                notice=trv.data[MailInfoTemplate.delivery_key(context.order, "notice")]
                )

def _with_serial_and_seat(ordered_product,  ordered_product_item):
    if ordered_product_item.seats:
        for i, s in enumerate(ordered_product_item.seats):
            yield i, s
    else:
        for i in xrange(ordered_product.quantity):
            yield i, s

class QRTicketDeliveryPlugin(object):
    def prepare(self, request, cart):
        """ 前処理 """

    def finish(self, request, cart):
        """ 確定時処理 """
        order = cart.order
        for op in order.ordered_products:
            for opi in op.ordered_product_items:
                for i, seat in _with_serial_and_seat(op, opi):
                    token = core_models.OrderedProductItemToken(
                        item = opi, 
                        serial = i, 
                        seat = seat, 
                        valid=True
                        )
                    opi.tokens.append(token)
