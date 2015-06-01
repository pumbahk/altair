# -*- coding: utf-8 -*-
"""ファミポート決済/引取プラグイン
"""
from markupsafe import Markup
from zope.interface import implementer
from pyramid.response import Response
from lxml import etree
from altair.pyramid_dynamic_renderer import lbr_view_config
from altair.app.ticketing.cart import helpers as cart_helper
from altair.app.ticketing.cart.interfaces import (
    ICartPayment,
    ICartDelivery,
    )
from altair.app.ticketing.payments.interfaces import (
    IOrderPayment,
    IPaymentPlugin,
    IDeliveryPlugin,
    IPaymentDeliveryPlugin,
    )
from altair.app.ticketing.mails.interfaces import (
    ICompleteMailResource,
    ILotsElectedMailResource,
    IOrderCancelMailResource,
    ILotsAcceptedMailResource,
    ILotsRejectedMailResource,
    )

from altair.app.ticketing.famiport.models import FamiPortOrderType, FamiPortTicketType
import altair.app.ticketing.famiport.api as famiport_api
from altair.app.ticketing.famiport.api import create_famiport_order as do_famiport_order
from altair.app.ticketing.famiport.exc import FamiPortError
from altair.app.ticketing.core.models import FamiPortTenant
from altair.app.ticketing.core.modelmanage import ApplicableTicketsProducer
from altair.app.ticketing.orders.models import OrderedProductItem
from altair.app.ticketing.cart.models import CartedProductItem
from altair.app.ticketing.tickets.utils import (
    NumberIssuer,
    build_dicts_from_ordered_product_item,
    build_dicts_from_carted_product_item,
    transform_matrix_from_ticket_format
    )

from ..interfaces import IOrderDelivery
from ..exceptions import PaymentPluginException
import altair.app.ticketing.orders.models as order_models
from . import FAMIPORT_PAYMENT_PLUGIN_ID as PAYMENT_PLUGIN_ID
from . import FAMIPORT_DELIVERY_PLUGIN_ID as DELIVERY_PLUGIN_ID
import pystache


def includeme(config):
    config.include('altair.app.ticketing.famiport')
    config.add_payment_plugin(FamiPortPaymentPlugin(), PAYMENT_PLUGIN_ID)
    config.add_delivery_plugin(FamiPortDeliveryPlugin(), DELIVERY_PLUGIN_ID)
    config.add_payment_delivery_plugin(FamiPortPaymentDeliveryPlugin(), PAYMENT_PLUGIN_ID, DELIVERY_PLUGIN_ID)
    config.scan(__name__)


class FamiPortPluginFailure(PaymentPluginException):
    pass


def applicable_tickets_iter(bundle):
    return ApplicableTicketsProducer(bundle).famiport_only_tickets()


def build_ticket_dict(type_, data, template_code):
    return dict(
        type=type_,
        data=data,
        template=template_code
        )

DICT_XML_ELEMENT_NAME_MAP = {
    u'TTEVEN0001': [
        (u'TitleOver', u'{{{イベント名}}}'),
        (u'TitleMain', u'{{{パフォーマンス名}}}'),
        (u'TitleSub', u'{{{公演名副題}}}'),
        (u'Date', u'{{{開催日}}}'),
        (u'OpenTime', u'{{{開場時刻}}}'),
        (u'StartTime', u'{{{開始時刻}}}'),
        (u'Price', u'{{{チケット価格}}}'),
        (u'Hall', u'{{{会場名}}}'),
        (u'Note1', u'{{{aux.注意事項1}}}'),
        (u'Note2', u'{{{aux.注意事項2}}}'),
        (u'Note3', u'{{{aux.注意事項3}}}'),
        (u'Note4', u'{{{aux.注意事項4}}}'),
        (u'Note5', u'{{{aux.注意事項5}}}'),
        (u'Note6', u'{{{aux.注意事項6}}}'),
        (u'Note7', u'{{{aux.注意事項7}}}'),
        (u'Seat1', u'{{{券種名}}}'),
        (u'Sub-Title1', u'{{{イベント名}}}'),
        (u'Sub-Title2', u'{{{パフォーマンス名}}}'),
        (u'Sub-Title3', u'{{{公演名副題}}}'),
        (u'Sub-Date', u'{{{開催日s}}}'),
        (u'Sub-OpenTime', u'{{{開場時刻s}}}'),
        (u'Sub-StartTime', u'{{{開始時刻s}}}'),
        (u'Sub-Price', u'{{{チケット価格}}}'),
        (u'Sub-Seat1', u'{{{券種名}}}'),
        ],
    }


def build_xml_from_dicts(template_code, dicts):
    render = pystache.render
    root = etree.Element(u'TICKET')
    map_ = DICT_XML_ELEMENT_NAME_MAP[template_code]
    for element_name, t in map_:
        e = etree.Element(element_name)
        e.text = render(t, dicts)
        root.append(e)
    return root


def get_ticket_template_code_from_ticket_format(ticket_format):
    retval = None
    aux = ticket_format.data.get('aux')
    if aux is not None:
        retval = aux.get('famiport_ticket_template_code')
    if retval is None:
        retval = u'TTEVEN0001' # XXX: デフォルト
    return retval

def build_ticket_dicts_from_order_like(request, order_like):
    tickets = []
    issuer = NumberIssuer()
    for ordered_product in order_like.items:
        for ordered_product_item in ordered_product.elements:
            # XXX: OrderedProductLike is not reachable from OrderedProductItemLike
            if isinstance(ordered_product_item, OrderedProductItem):
                dicts = build_dicts_from_ordered_product_item(ordered_product_item, ticket_number_issuer=issuer)
            elif isinstance(ordered_product_item, CartedProductItem):
                dicts = build_dicts_from_carted_product_item(ordered_product_item, ticket_number_issuer=issuer)
            else:
                raise TypeError('!')
            bundle = ordered_product_item.product_item.ticket_bundle
            for seat, dict_ in dicts:
                for ticket in applicable_tickets_iter(bundle):
                    if ticket.principal:
                        ticket_type = FamiPortTicketType.TicketWithBarcode.value
                    else:
                        ticket_type = FamiPortTicketType.ExtraTicket.value
                    ticket_format = ticket.ticket_format
                    template_code = get_ticket_template_code_from_ticket_format(ticket_format)
                    xml = etree.tostring(
                        build_xml_from_dicts(template_code, dicts),
                        encoding='unicode'
                        )
                    ticket = build_ticket_dict(
                        type_=ticket_type,
                        data=xml,
                        template_code=template_code
                        )
                    tickets.append(ticket)
    return tickets


def lookup_famiport_tenant(request, order_like):
    return FamiPortTenant.query.filter_by(organization_id=order_like.organization_id).first()


def create_famiport_order(request, order_like, in_payment, name='famiport'):
    """FamiPortOrderを作成する

    クレカ決済などで決済をFamiPortで実施しないケースはin_paymentにFalseを指定する。
    """

    # FamiPortで決済しない場合は0をセットする
    total_amount = 0
    system_fee = 0
    ticketing_fee = 0
    ticket_payment = 0

    if in_payment:
        total_amount = order_like.total_amount
        system_fee = order_like.transaction_fee + order_like.system_fee + order_like.special_fee
        ticketing_fee = order_like.delivery_fee
        ticket_payment = order_like.total_amount - (order_like.system_fee + order_like.transaction_fee + order_like.delivery_fee + order_like.special_fee)

    customer_address_1 = order_like.shipping_address.prefecture + order_like.shipping_address.city + order_like.shipping_address.address_1
    customer_address_2 = order_like.shipping_address.address_2
    customer_name = order_like.shipping_address.last_name + order_like.shipping_address.first_name
    customer_phone_number = (order_like.shipping_address.tel_1 or order_like.shipping_address.tel_2 or u'').replace(u'-', u'')

    tenant = lookup_famiport_tenant(request, order_like)
    tenant = lookup_famiport_tenant(request, order_like)
    if tenant is None:
        raise FamiPortPluginFailure('not found famiport tenant: order_no={}'.format(order_like.order_no))

    return do_famiport_order(
        client_code=tenant.code,
        type_=FamiPortOrderType.Ticketing.value,
        order_no=order_like.order_no,
        userside_sales_segment_id=order_like.sales_segment.id,
        customer_address_1=customer_address_1,
        customer_address_2=customer_address_2,
        customer_name=customer_name,
        customer_phone_number=customer_phone_number,
        total_amount=total_amount,
        system_fee=system_fee,
        ticketing_fee=ticketing_fee,
        ticket_payment=ticket_payment,
        tickets=build_ticket_dicts_from_order_like(request, order_like)
        )


def refund_order(request, order, refund_record, now=None):
    """払い戻し"""
    raise FamiPortPluginFailure('unimplemented', None, None, None)


def cancel_order(request, order, now=None):
    """キャンセル"""
    raise FamiPortPluginFailure('unimplemented', None, None, None)


def refresh_order(request, order, now=None):
    """予約更新"""
    raise FamiPortPluginFailure('unimplemented', None, None, None)


def _overridable_payment(path, fallback_ua_type=None):
    """ここがどこに作用してくるのかわからない
    """
    from . import _template
    return _template(
        path, type='overridable', for_='payments', plugin_type='payment',
        plugin_id=PAYMENT_PLUGIN_ID, fallback_ua_type=fallback_ua_type,
        )


def _overridable_delivery(path, fallback_ua_type=None):
    from . import _template
    return _template(
        path, type='overridable', for_='payments', plugin_type='delivery',
        plugin_id=DELIVERY_PLUGIN_ID, fallback_ua_type=fallback_ua_type,
        )


@lbr_view_config(context=IOrderPayment, name='payment-%d' % PAYMENT_PLUGIN_ID,
                 renderer=_overridable_payment('famiport_payment_completion.html'))
def reserved_number_payment_viewlet(context, request):
    """決済方法の完了画面用のhtmlを生成"""
    payment_method = context.order.payment_delivery_pair.payment_method
    from altair.app.ticketing.famiport.models import _session
    famiport_order = famiport_api.get_famiport_order(context.order.order_no, _session)
    return dict(payment_name=payment_method.name, description=Markup(payment_method.description),
                famiport_order=famiport_order, h=cart_helper)


@lbr_view_config(context=ICartPayment, name="payment-%d" % PAYMENT_PLUGIN_ID,
                 renderer=_overridable_payment("famiport_payment_confirm.html"))
def reserved_number_payment_confirm_viewlet(context, request):
    """決済方法の確認画面用のhtmlを生成"""
    cart = context.cart
    payment_method = cart.payment_delivery_pair.payment_method
    return dict(payment_name=payment_method.name, description=Markup(payment_method.description), h=cart_helper)


@lbr_view_config(context=ICompleteMailResource, name="payment-%d" % PAYMENT_PLUGIN_ID,
                 renderer=_overridable_payment("famiport_mail_complete.html", fallback_ua_type='mail'))
def complete_mail(context, request):
    """購入完了メールの決済方法部分のhtmlを出力する"""
    notice = context.mail_data("P", "notice")
    return dict(notice=notice, h=cart_helper)


@lbr_view_config(context=IOrderCancelMailResource, name="payment-%d" % PAYMENT_PLUGIN_ID)
def cancel_mail(context, request):
    """キャンセルメールの決済方法"""
    return Response(context.mail_data("P", "notice"))


@lbr_view_config(context=ILotsElectedMailResource, name="payment-%d" % PAYMENT_PLUGIN_ID)
@lbr_view_config(context=ILotsRejectedMailResource, name="payment-%d" % PAYMENT_PLUGIN_ID)
@lbr_view_config(context=ILotsAcceptedMailResource, name="payment-%d" % PAYMENT_PLUGIN_ID)
def lot_payment_notice_viewlet(context, request):
    return Response(context.mail_data("P", "notice"))


@implementer(IPaymentPlugin)
class FamiPortPaymentPlugin(object):
    """ファミポート用決済プラグイン"""

    _in_payment = False  # FamiPortでの決済を行う

    def validate_order(self, request, order_like):
        """予約を作成する前にvalidationする"""

    def prepare(self, request, cart):
        """前処理"""

    def finish(self, request, cart):
        """確定処理"""
        order = order_models.Order.create_from_cart(cart)
        cart.finish()
        self.finish2(request, order)
        return order

    def finish2(self, request, cart):
        """確定処理2"""
        try:
            return create_famiport_order(request, cart, in_payment=self._in_payment)
        except FamiPortError:
            raise FamiPortPluginFailure()

    def finished(self, requrst, order):
        """支払状態遷移済みかどうかを判定"""
        return True

    def refresh(self, request, order):
        """決済側の状態をDBに反映"""
        return refresh_order(request, order)

    def cancel(self, request, order):
        """キャンセル処理"""
        return cancel_order(request, order)

    def refund(self, request, order, refund_record):
        """払戻処理"""
        return refund_order(request, order, refund_record)


@lbr_view_config(context=ICartDelivery, name='delivery-%d' % DELIVERY_PLUGIN_ID,
                 renderer=_overridable_delivery('famiport_delivery_confirm.html'))
def deliver_confirm_viewlet(context, request):
    """引取方法の確認画面のhtmlを生成"""
    cart = context.cart
    delivery_method = cart.payment_delivery_pair.delivery_method
    return dict(delivery_name=delivery_method.name, description=Markup(delivery_method.description), h=cart_helper)


@lbr_view_config(context=IOrderDelivery, name='delivery-%d' % DELIVERY_PLUGIN_ID,
                 renderer=_overridable_delivery('famiport_delivery_complete.html'))
def deliver_completion_viewlet(context, request):
    """引取方法の完了画面のhtmlを生成"""
    from altair.app.ticketing.famiport.models import _session
    delivery_method = context.order.payment_delivery_pair.delivery_method
    famiport_order = famiport_api.get_famiport_order(context.order.order_no, _session)
    return dict(delivery_name=delivery_method.name, description=Markup(delivery_method.description),
                famiport_order=famiport_order, h=cart_helper)


@lbr_view_config(context=ICompleteMailResource, name='delivery-%d' % DELIVERY_PLUGIN_ID,
                 renderer=_overridable_delivery('famiport_mail_complete.html', fallback_ua_type='mail'))
def deliver_completion_mail_viewlet(context, request):
    """購入完了メールの配送方法部分のhtmlを出力する"""
    notice = context.mail_data("P", "notice")
    return dict(notice=notice, h=cart_helper)


@lbr_view_config(context=IOrderCancelMailResource, name='delivery-%d' % DELIVERY_PLUGIN_ID)
@lbr_view_config(context=ILotsRejectedMailResource, name='delivery-%d' % DELIVERY_PLUGIN_ID)
@lbr_view_config(context=ILotsAcceptedMailResource, name='delivery-%d' % DELIVERY_PLUGIN_ID)
@lbr_view_config(context=ILotsElectedMailResource, name='delivery-%d' % DELIVERY_PLUGIN_ID)
def delivery_notice_viewlet(context, request):
    return Response(text=u'ファミポート受け取り')


@implementer(IDeliveryPlugin)
class FamiPortDeliveryPlugin(object):
    _in_payment = False  # FamiPortで決済を行わない (例えばクレカ決済)

    def validate_order(self, request, order_like, update=False):
        """予約の検証"""

    def prepare(self, request, cart):
        """ 前処理 """

    def finish(self, request, cart):
        """確定時処理"""
        self.finish2(request, cart)

    def finish2(self, request, order_like):
        """確定時処理"""
        try:
            return create_famiport_order(request, order_like, in_payment=self._in_payment)  # noqa
        except FamiPortError:
            raise FamiPortPluginFailure()

    def finished(self, request, order):
        """ tokenが存在すること """
        return True

    def refresh(self, request, order):
        """リフレッシュ"""
        return refresh_order(request, order)

    def cancel(self, request, order):
        """キャンセル処理"""
        return cancel_order(request, order)

    def refund(self, request, order, refund_record):
        """払い戻し"""
        return refund_order(request, order, refund_record)


@implementer(IPaymentDeliveryPlugin)
class FamiPortPaymentDeliveryPlugin(object):
    _in_payment = True  # FamiPortで決済を行う

    def validate_order(self, request, order_like, update=False):
        """予約の検証"""

    def prepare(self, request, cart):
        """ 前処理 """

    def finish(self, request, cart):
        """ 確定時処理 """
        order = order_models.Order.create_from_cart(cart)
        cart.finish()
        self.finish2(request, order)
        return order

    def finish2(self, request, order_like):
        """ 確定時処理 """
        try:
            return create_famiport_order(request, order_like, in_payment=self._in_payment)  # noqa
        except FamiPortError:
            raise FamiPortPluginFailure()

    def finished(self, request, order):
        """ tokenが存在すること """
        return True

    def refresh(self, request, order):
        """リフレッシュ"""
        return refresh_order(request, order)

    def cancel(self, request, order):
        """キャンセル処理"""
        return cancel_order(request, order)

    def refund(self, request, order, refund_record):
        """払い戻し"""
        return refund_order(request, order, refund_record)
