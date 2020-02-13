# -*- coding:utf-8 -*-
"""TicketHub引取(QR入場)
"""

import re

from altair.app.ticketing.cart.interfaces import ICartDelivery
from altair.app.ticketing.mails.interfaces import (
    ICompleteMailResource,
    IOrderCancelMailResource,
    ILotsAcceptedMailResource,
    ILotsElectedMailResource,
    ILotsRejectedMailResource,
)
from altair.app.ticketing.payments.interfaces import IDeliveryPlugin, IOrderDelivery
from altair.app.ticketing.ticket_hub.models import TicketHubOrder
from altair.pyramid_dynamic_renderer import lbr_view_config
from altair.ticket_hub.api import TicketHubClient, TicketHubAPI
from altair.ticket_hub.interfaces import ITicketHubAPI
from altair.ticket_hub.exc import TicketHubAPIError
from markupsafe import Markup
from pyramid.response import Response
from pyramid.view import view_defaults
from zope.interface import implementer
from ..exceptions import PaymentPluginException
from . import TICKET_HUB_DELIVERY_PLUGIN_ID as DELIVERY_PLUGIN_ID
from . import logger
from . import models as m
from .helpers import get_delivery_method_info

tag_re = re.compile(r"<[^>]*?>")

class TicketHubPluginFailure(PaymentPluginException):
    pass

def includeme(config):
    config.add_delivery_plugin(TicketHubDeliveryPlugin(), DELIVERY_PLUGIN_ID)
    config.scan(__name__)
    settings = config.registry.settings
    api = TicketHubAPI(TicketHubClient(
        base_uri=settings["altair.tickethub.base_uri"],
        api_key=settings["altair.tickethub.api_key"],
        api_secret=settings["altair.tickethub.api_secret"],
        seller_code=settings["altair.tickethub.seller_code"],
        seller_channel_code=settings["altair.tickethub.seller_channel_code"]
    ))
    config.registry.registerUtility(api, ITicketHubAPI)

def _overridable_delivery(path, fallback_ua_type=None):
    from . import _template
    return _template(path, type='overridable', for_='payments', plugin_type='delivery', plugin_id=DELIVERY_PLUGIN_ID, fallback_ua_type=fallback_ua_type)


@lbr_view_config(context=IOrderDelivery, name="delivery-%d" % DELIVERY_PLUGIN_ID, renderer=_overridable_delivery("ticket_hub_completion.html"))
def ticket_hub_viewlet(context, request):
    logger.debug(u"TicketHub complete viewlet")
    order = context.order
    logger.debug(u"order_no = %s" % order.order_no)
    delivery_method = order.payment_delivery_pair.delivery_method
    description = get_delivery_method_info(request, delivery_method, 'description')
    ticket_hub_order = order.ticket_hub_order
    return dict(description=Markup(description), ticket_hub_order=ticket_hub_order)


@lbr_view_config(context=ICartDelivery, name="delivery-%d" % DELIVERY_PLUGIN_ID, renderer=_overridable_delivery("ticket_hub_confirm.html"))
def ticket_hub_confirm_viewlet(context, request):
    logger.debug(u"TicketHub confirm viewlet")
    cart = context.cart
    delivery_method = cart.payment_delivery_pair.delivery_method
    delivery_name = get_delivery_method_info(request, delivery_method, 'name')
    description = get_delivery_method_info(request, delivery_method, 'description')
    return dict(delivery_name=delivery_name, description=Markup(description))

def ticket_hub_facility(cart):
    return cart.items[0].product.ticket_hub_item.ticket_hub_item_group.ticket_hub_facility

def _build_ticket_hub_cart_items(cart):
    # cart_items = [{ "item_group_code": String(5), items: [{ "item_code": String(4), "quantity": Int }] }]
    import itertools
    # FIXME: Cartからticket_hubの商品グループ、商品、購入数を含んだデータ構造に変換したい
    ticket_hub_items = [(carted_product.product.ticket_hub_item, carted_product.quantity) for carted_product in cart.items]
    group_codes = set([item.ticket_hub_item_group.code for item, qty in ticket_hub_items])
    ticket_hub_cart_items = [dict(item_group_code=group_code, items=[]) for group_code in group_codes]
    for item, quantity in ticket_hub_items:
        target_groups = next(itertools.ifilter(lambda x: x.get("item_group_code") == item.ticket_hub_item_group.code, ticket_hub_cart_items), None)
        target_groups.get("items").append(dict(item_code=item.code, quantity=quantity))
        dict(item_code=item.code, quantity=quantity)
    return ticket_hub_cart_items

def create_ticket_hub_cart(api, cart):
    # Cart <- Product <- TicketHubItem -> TicketHubItemGroup -> TicketHubFacility
    # cartには複数の商品が入っている可能性があるので、それらを全てCartリクエストする必要がある
    # 引取方法でTICKET_HUB_DELIVERY_PLUGIN_IDが選択されている場合、選択された商品は全てTicketHubItemと関連があることを前提とする
    # XXX: items should not contain None. all products in the cart should have a TicketHubItem pair.
    facility = ticket_hub_facility(cart)
    return api.create_cart(
        facility_code=facility.code,
        agent_code=facility.agent_code,
        cart_items=_build_ticket_hub_cart_items(cart)
    )

def create_ticket_hub_temp_order(api, ticket_hub_cart):
    return api.create_temp_order

@implementer(IDeliveryPlugin)
class TicketHubDeliveryPlugin(object):
    """ TicketHub連携によるQR入場する引取方法 """

    def validate_order(self, request, order_like, update=False):
        pass

    def validate_order_cancellation(self, request, order, now):
        """ キャンセルバリデーション """
        pass

    def prepare(self, request, cart):
        """ 前処理 なし"""

    def finish(self, request, cart):
        """ 確定処理 """
        self.finish2(request, cart)

    def finish2(self, request, order_like):
        """ TicketHubにOrderデータを作成し、入場QRデータを取得 """
        try:
            api = request.registry.getUtility(ITicketHubAPI)
            ticket_hub_cart_res = create_ticket_hub_cart(api, order_like)
            ticket_hub_temp_order_res = api.create_temp_order(ticket_hub_cart_res.cart_id)
        except TicketHubAPIError:
            raise TicketHubPluginFailure(u'failed', order_no=order_like.order_no, back_url=None)
        ticket_hub_order = TicketHubOrder.create_from_temp_res(ticket_hub_temp_order_res, ticket_hub_cart_res, order_like)
        logger.debug(u"created TicketHubTempOrder No: %s" % ticket_hub_order.order_no)
        logger.debug(vars(ticket_hub_order))
        logger.debug([vars(t) for t in ticket_hub_order.tickets])
        logger.debug(vars(order_like))

    def finished(self, request, order):
        return bool(order.ticket_hub_order)

    def refresh(self, request, order):
        # not implemented
        pass

    def cancel(self, request, order, now=None):
        # not implemented
        pass

    def refund(self, request, order, refund_record):
        # not implemented
        pass

    def get_order_info(self, request, order):
        return {}


@view_defaults(context=ICompleteMailResource)
class CompletionMailViewlet(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @lbr_view_config(name="delivery-%d" % DELIVERY_PLUGIN_ID, renderer=_overridable_delivery("ticket_hub_mail_complete.html", fallback_ua_type='mail'))
    def delivery(self):
        """ 完了メール表示
        :param context: ICompleteMailDelivery
        """
        order = self.context.order
        delivery_method = order.payment_delivery_pair.delivery_method
        notice = self.context.mail_data("D", "notice")
        reserved_number = m.ReservedNumber.query.filter_by(order_no=self.context.order.order_no).first()
        description = ""
        if delivery_method.description is not None:
            description = tag_re.sub("", delivery_method.description)
        return dict(notice=notice, reserved_number=reserved_number, description=description)


@view_defaults(context=IOrderCancelMailResource)
class OrderCancelMailViewlet(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @lbr_view_config(name="delivery-%d" % DELIVERY_PLUGIN_ID)
    def delivery(self):
        """ cancelメール表示
        """
        return Response(self.context.mail_data("D", "notice"))


@lbr_view_config(context=ILotsElectedMailResource, name="delivery-%d" % DELIVERY_PLUGIN_ID)
@lbr_view_config(context=ILotsRejectedMailResource, name="delivery-%d" % DELIVERY_PLUGIN_ID)
@lbr_view_config(context=ILotsAcceptedMailResource, name="delivery-%d" % DELIVERY_PLUGIN_ID)
def lot_delivery_notice_viewlet(context, request):
    return Response(context.mail_data("D", "notice"))

