# -*- coding: utf-8 -*-
"""ファミポート決済/引取プラグイン
"""
import logging
import pystache
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from lxml import etree
from sqlalchemy import sql
from markupsafe import Markup
from zope.interface import implementer
import sqlalchemy as sa
from pyramid.response import Response
from altair.pyramid_dynamic_renderer import lbr_view_config
from altair.sqlahelper import get_db_session
from altair.models import Identifier, MutationDict, JSONEncodedDict
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
from altair.app.ticketing.models import DBSession, Base
from altair.app.ticketing.famiport import api as famiport_api
from altair.app.ticketing.cart.models import CartedProductItem
from altair.app.ticketing.core.models import FamiPortTenant
from altair.app.ticketing.famiport.exc import FamiPortAPIError
from altair.app.ticketing.orders.models import OrderedProductItem
from altair.app.ticketing.core.modelmanage import ApplicableTicketsProducer
from altair.app.ticketing.famiport.userside_models import AltairFamiPortSalesSegmentPair

from altair.app.ticketing.famiport.models import (
    FamiPortOrderType,
    FamiPortTicketType,
    )
from altair.app.ticketing.tickets.utils import (
    NumberIssuer,
    build_dicts_from_ordered_product_item,
    build_dicts_from_carted_product_item,
    build_cover_dict_from_order,
    )

from ..interfaces import IOrderDelivery
from ..exceptions import PaymentPluginException
import altair.app.ticketing.orders.models as order_models
from . import FAMIPORT_PAYMENT_PLUGIN_ID as PAYMENT_PLUGIN_ID
from . import FAMIPORT_DELIVERY_PLUGIN_ID as DELIVERY_PLUGIN_ID


logger = logging.getLogger(__name__)


def select_famiport_order_type(order_like, plugin):
    """FamiPortOrderのどの値を使えば良いか判断する

    - 組み合わせと返す値

      - FamiPortPaymentPlugin -> (前払)
        - 発券開始日時/払い期限関係なし               -> 前払         -> PaymentOnly
      - FamiPortDeliveryPlugin -> (代済)
        - 発券開始日時/払い期限関係なし               -> 代済         -> Ticketing
      - FamiPortPaymentDeliveryPlugin (代引/前払後日前払/前払後日発券)
         - 発券開始日時が支払開始日時と同じ           -> 代引         -> CashOnDelivery
         - 発券開始日時が支払開始日時よりもあと(前払後日) -> 前払後日前払 -> Payment

    - pluginは3種類
      - FamiPortPaymentPlugin -> (前払)
      - FamiPortDeliveryPlugin -> (代済)
      - FamiPortPaymentDeliveryPlugin -> (代引/前払後日前払/前払後日発券)

    - 発券開始日時と支払期限などの状況

      - 発券開始日時/払い期限関係なし
      - 発券開始日時/払い期限関係あり

        - 発券開始日時が支払期限以前(通常)
        - 発券開始日時が支払日時よりもあと(前払後日)

    .. note::

       - 前払後日が発生するのはpayment delivery pluginのみ。
       - FamiPortOrder.type_の値は変更しない。
       - 前払後日発券の値を返すケースでは以下の条件をAPI側で判断して返す。(その際FamiPortOrder.typeの値更新はしない)

         - FamiPortOrder.type が Payment
         - 支払日時がNoneではない

    - 返す事の出来る値
      - CashOnDelivery  # 代引き
      - Payment  # 前払い（後日渡し）の前払い時
      - Ticketing  # 代済発券と前払い(後日渡し)の後日渡し時
      - PaymentOnly  # 前払いのみ
    """
    if isinstance(plugin, FamiPortPaymentPlugin):
        return FamiPortOrderType.PaymentOnly.value
    elif isinstance(plugin, FamiPortDeliveryPlugin):
        return FamiPortOrderType.Ticketing.value
    elif isinstance(plugin, FamiPortPaymentDeliveryPlugin):
        if order_like.payment_start_at and order_like.issuing_start_at and \
           order_like.issuing_start_at > order_like.payment_start_at:
            return FamiPortOrderType.Payment.value  # 前払後日前払
        else:
            return FamiPortOrderType.CashOnDelivery.value
    raise FamiPortPluginFailure('invalid payment type: order_no={}, plugin{}'.format(order_like, plugin), order_no=order_like.order_no, back_url=None)


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


def build_ticket_dict(type_, data, template_code, price, token_serial, logically_subticket):
    return dict(
        type=type_,
        data=data,
        template=template_code,
        price=price,
        userside_id=token_serial,
        logically_subticket=logically_subticket
        )


class FamiPortTicketTemplate(Base):
    __tablename__ = 'FamiPortTicketTemplate'

    id = sa.Column(Identifier(), nullable=False, autoincrement=True, primary_key=True)
    template_code = sa.Column(sa.Unicode(13), nullable=False)
    logically_subticket = sa.Column(sa.Boolean(), nullable=False, default=False)
    mappings = sa.Column(MutationDict.as_mutable(JSONEncodedDict(16384)), nullable=False)


class FamiPortTicketXMLBuilder(object):
    def __init__(self, request):
        self.request = request
        self.session = get_db_session(request, 'slave')
        self.cache = {}

    def _get_template_info(self, template_code):
        ti = self.cache.get(template_code)
        if ti is None:
            ti = self.session.query(FamiPortTicketTemplate) \
                .filter_by(template_code=template_code) \
                .one()
            self.cache[template_code] = ti
        return ti

    def __call__(self, template_code, dicts):
        render = pystache.render
        root = etree.Element(u'ticket')
        ti = self._get_template_info(template_code)
        for element_name, t in ti.mappings:
            e = etree.Element(element_name)
            e.text = render(t, dicts)
            root.append(e)
        return root, ti.logically_subticket


def get_ticket_template_code_from_ticket_format(ticket_format):
    retval = None
    aux = ticket_format.data.get('aux')
    if aux is not None:
        retval = aux.get('famiport_ticket_template_code')
    if retval is None:
        retval = u'TTTSTR0001'  # XXX: デフォルト
    return retval


def build_ticket_dicts_from_order_like(request, order_like):
    tickets = []
    issuer = NumberIssuer()
    for ordered_product in order_like.items:
        for ordered_product_item in ordered_product.elements:
            # XXX: OrderedProductLike is not reachable from OrderedProductItemLike
            if isinstance(ordered_product_item, OrderedProductItem):
                dicts = build_dicts_from_ordered_product_item(ordered_product_item, ticket_number_issuer=issuer, return_tokens=True)
            elif isinstance(ordered_product_item, CartedProductItem):
                dicts = build_dicts_from_carted_product_item(ordered_product_item, ticket_number_issuer=issuer, return_tokens=True)
            else:
                raise TypeError('!')
            bundle = ordered_product_item.product_item.ticket_bundle
            xml_builder = FamiPortTicketXMLBuilder(request)
            for token, dict_ in dicts:
                for ticket in applicable_tickets_iter(bundle):
                    ticket_format = ticket.ticket_format
                    template_code = get_ticket_template_code_from_ticket_format(ticket_format)
                    xml_root, logically_subticket = xml_builder(template_code, dict_)
                    xml = etree.tostring(xml_root, encoding='unicode')
                    if logically_subticket != (not ticket.principal):
                        raise RuntimeError('logically_subticket=%r while expecting %r' % (logically_subticket, not ticket.principal))
                    ticket = build_ticket_dict(
                        type_=FamiPortTicketType.TicketWithBarcode.value,
                        data=xml,
                        template_code=template_code,
                        price=ordered_product_item.price,
                        token_serial=token.serial,
                        logically_subticket=logically_subticket
                        )
                    tickets.append(ticket)
    return tickets


def lookup_famiport_tenant(request, order_like):
    return FamiPortTenant.query.filter_by(organization_id=order_like.organization_id).first()


def get_altair_famiport_sales_segment_pair(order_like):
    return DBSession.query(AltairFamiPortSalesSegmentPair) \
        .filter(
            sql.or_(
                AltairFamiPortSalesSegmentPair.seat_unselectable_sales_segment_id == order_like.sales_segment.id,
                AltairFamiPortSalesSegmentPair.seat_selectable_sales_segment_id == order_like.sales_segment.id
                )
            ) \
        .one()

def build_famiport_order_dict(request, order_like, client_code, type_, name='famiport'):
    """FamiPortOrderを作成する
    """

    # FamiPortで決済しない場合は0をセットする
    total_amount = 0
    system_fee = 0
    ticketing_fee = 0
    ticket_payment = 0
    payment_sheet_text = None

    if type_ != FamiPortOrderType.Ticketing.value:
        total_amount = order_like.total_amount
        system_fee = order_like.transaction_fee + order_like.system_fee + order_like.special_fee
        ticketing_fee = order_like.delivery_fee
        ticket_payment = order_like.total_amount - (order_like.system_fee + order_like.transaction_fee + order_like.delivery_fee + order_like.special_fee)

    if type_ == FamiPortOrderType.PaymentOnly.value:
        payment_sheet_text_template = order_like.payment_delivery_pair.payment_method.preferences.get(unicode(PAYMENT_PLUGIN_ID), {}).get(u'payment_sheet_text', None)
        if payment_sheet_text_template is not None:
            dict_ = build_cover_dict_from_order(order_like)
            payment_sheet_text = pystache.render(payment_sheet_text_template, dict_)

    customer_address_1 = order_like.shipping_address.prefecture + order_like.shipping_address.city + order_like.shipping_address.address_1
    customer_address_2 = order_like.shipping_address.address_2
    customer_name = order_like.shipping_address.last_name + order_like.shipping_address.first_name
    customer_phone_number = (order_like.shipping_address.tel_1 or order_like.shipping_address.tel_2 or u'').replace(u'-', u'')

    altair_famiport_sales_segment_pair = get_altair_famiport_sales_segment_pair(order_like)
    try:
        famiport_sales_segment = famiport_api.get_famiport_sales_segment_by_userside_id(request, client_code, altair_famiport_sales_segment_pair.id)
    except:
        raise FamiPortPluginFailure(
            u'cannot retrieve FamiPortSalesSegment with client_code=%s, altair_famiport_sales_segment_pair_id=%ld. perhaps sales information has not been set to the famiport-side database yet?' % (
                client_code,
                altair_famiport_sales_segment_pair.id
                ),
            order_no=order_like.order_no,
            back_url=None
            )

    return dict(
        client_code=client_code,
        type_=type_,
        order_no=order_like.order_no,
        event_code_1=famiport_sales_segment['event_code_1'],
        event_code_2=famiport_sales_segment['event_code_2'],
        performance_code=famiport_sales_segment['performance_code'],
        sales_segment_code=famiport_sales_segment['code'],
        customer_address_1=customer_address_1,
        customer_address_2=customer_address_2,
        customer_name=customer_name,
        customer_phone_number=customer_phone_number,
        total_amount=total_amount,
        system_fee=system_fee,
        ticketing_fee=ticketing_fee,
        ticket_payment=ticket_payment,
        tickets=(
            build_ticket_dicts_from_order_like(request, order_like)
            if type_ != FamiPortOrderType.PaymentOnly.value
            else []
            ),
        payment_start_at=order_like.payment_start_at,
        payment_due_at=order_like.payment_due_at,
        ticketing_start_at=order_like.issuing_start_at,
        ticketing_end_at=order_like.issuing_end_at,
        payment_sheet_text=payment_sheet_text
        )

def create_famiport_order(request, order_like, plugin, name='famiport'):
    """FamiPortOrderを作成する
    """
    tenant = lookup_famiport_tenant(request, order_like)
    if tenant is None:
        raise FamiPortPluginFailure('could not find famiport tenant', order_no=order_like.order_no, back_url=None)

    type_ = select_famiport_order_type(order_like, plugin)
    return famiport_api.create_famiport_order(
        request,
        **build_famiport_order_dict(request, order_like, tenant.code, type_, name) 
        )


def refund_order(request, order, refund_record, now=None):
    """払い戻し"""
    if now is None:
        now = datetime.now()
    tenant = lookup_famiport_tenant(request, order)
    if tenant is None:
        raise FamiPortPluginFailure('could not find famiport tenant', order_no=order_like.order_no, back_url=None)
    if order.paid_at is None:
        raise FamiPortPluginFailure(u'cannot refund an order that is not paid yet', order_no=order.order_no, back_url=None)
    if order.issued_at is None:
        logger.warning("trying to refund FamiPort order that is not marked issued: %s" % order.order_no)
    refund = refund_record.refund

    if refund.end_at is not None:
        base_date = refund.end_at
    else:
        base_date = now
    send_back_due_at = base_date.replace(day=1) + relativedelta(months=6) + timedelta(days=1), # 3ヶ月後の月末

    result = famiport_api.get_or_create_refund(
        request,
        client_code=tenant.code,
        send_back_due_at=send_back_due_at,
        start_at=refund.start_at,
        end_at=refund.end_at,
        userside_id=refund.id
        )
    famiport_refund_id = result['refund_id']
    if result['new']:
        logger.info("new refund has been registered (%ld)" % famiport_refund_id)
    famiport_api.refund_order_by_order_no(
        request,
        client_code=tenant.code,
        refund_id=famiport_refund_id,
        order_no=order.order_no,
        per_order_fee=refund_record.refund_per_order_fee,
        per_ticket_fee=refund_record.refund_per_ticket_fee
        )

def cancel_order(request, order, now=None):
    """キャンセル"""
    tenant = lookup_famiport_tenant(request, order)
    if tenant is None:
        raise FamiPortPluginFailure('could not find famiport tenant', order_no=order_like.order_no, back_url=None)
    try:
        famiport_api.cancel_famiport_order_by_order_no(request, tenant.code, order.order_no)
    except FamiPortAPIError:
        raise FamiPortPluginFailure('failed to cancel order', order_no=order.order_no, back_url=None)


def refresh_order(request, order, now=None, name='famiport'):
    """予約更新"""
    tenant = lookup_famiport_tenant(request, order)
    if tenant is None:
        raise FamiPortPluginFailure('could not find famiport tenant', order_like.order_no, None, None)
    try:
        existing_order = famiport_api.get_famiport_order(request, tenant.code, order.order_no)
        type_ = existing_order['type']
        famiport_api.update_famiport_order_by_order_no(
            request,
            **build_famiport_order_dict(request, order, tenant.code, type_, name=name)
            )
    except FamiPortAPIError:
        raise FamiPortPluginFailure('failed to refresh order', order_no=order.order_no, back_url=None)


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
    tenant = lookup_famiport_tenant(request, context.order)
    assert tenant is not None
    payment_method = context.order.payment_delivery_pair.payment_method
    famiport_order = famiport_api.get_famiport_order(request, tenant.code, context.order.order_no)
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
                 renderer=_overridable_payment("famiport_payment_mail_complete.html", fallback_ua_type='mail'))
def payment_mail_viewlet(context, request):
    """購入完了メールの決済方法部分のhtmlを出力する"""
    tenant = lookup_famiport_tenant(request, context.order)
    assert tenant is not None
    payment_method = context.order.payment_delivery_pair.payment_method
    famiport_order = famiport_api.get_famiport_order(request, tenant.code, context.order.order_no)
    return dict(payment_name=payment_method.name, description=Markup(payment_method.description),
                famiport_order=famiport_order, h=cart_helper)


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
            create_famiport_order(request, cart, plugin=self)
        except FamiPortAPIError:
            raise FamiPortPluginFailure('payment failed', order_no=cart.order_no, back_url=None)

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
    tenant = lookup_famiport_tenant(request, context.order)
    assert tenant is not None
    delivery_method = context.order.payment_delivery_pair.delivery_method
    famiport_order = famiport_api.get_famiport_order(request, tenant.code, context.order.order_no)
    return dict(delivery_name=delivery_method.name, description=Markup(delivery_method.description),
                famiport_order=famiport_order, h=cart_helper)


# @lbr_view_config(context=ICompleteMailResource, name="delivery-%d" % DELIVERY_PLUGIN_ID,
#                  renderer=_overridable_payment("famiport_delivery_mail_complete.html", fallback_ua_type='mail'))
# def delivery_mail_viewlet(context, request):
#     """購入完了メールの決済方法部分のhtmlを出力する"""
#     tenant = lookup_famiport_tenant(request, context.order)
#     assert tenant is not None
#     delivery_method = context.order.payment_delivery_pair.delivery_method
#     famiport_order = famiport_api.get_famiport_order(request, tenant.code, context.order.order_no)
#     return dict(delivery_name=delivery_method.name, description=Markup(delivery_method.description),
#                 famiport_order=famiport_order, h=cart_helper)




@lbr_view_config(context=ICompleteMailResource, name='delivery-%d' % DELIVERY_PLUGIN_ID,
                 renderer=_overridable_delivery('famiport_delivery_mail_complete.html', fallback_ua_type='mail'))
def deliver_completion_mail_viewlet(context, request):
    """購入完了メールの配送方法部分のhtmlを出力する"""
    tenant = lookup_famiport_tenant(request, context.order)
    assert tenant is not None
    delivery_method = context.order.payment_delivery_pair.delivery_method
    famiport_order = famiport_api.get_famiport_order(request, tenant.code, context.order.order_no)
    return dict(delivery_name=delivery_method.name, description=Markup(delivery_method.description),
                famiport_order=famiport_order, h=cart_helper)

    # notice = context.mail_data("P", "notice")
    # return dict(notice=notice, h=cart_helper)


@lbr_view_config(context=IOrderCancelMailResource, name='delivery-%d' % DELIVERY_PLUGIN_ID)
@lbr_view_config(context=ILotsRejectedMailResource, name='delivery-%d' % DELIVERY_PLUGIN_ID)
@lbr_view_config(context=ILotsAcceptedMailResource, name='delivery-%d' % DELIVERY_PLUGIN_ID)
@lbr_view_config(context=ILotsElectedMailResource, name='delivery-%d' % DELIVERY_PLUGIN_ID)
def delivery_notice_viewlet(context, request):
    return Response(text=u'ファミポート受け取り')


@implementer(IDeliveryPlugin)
class FamiPortDeliveryPlugin(object):
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
            create_famiport_order(request, order_like, plugin=self)  # noqa
        except FamiPortAPIError:
            raise FamiPortPluginFailure(u'failed', order_no=order_like.order_no, back_url=None)

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
            create_famiport_order(request, order_like, plugin=self)  # noqa
        except FamiPortAPIError:
            raise FamiPortPluginFailure(u'failed', order_no=order_like.order_no, back_url=None)

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
