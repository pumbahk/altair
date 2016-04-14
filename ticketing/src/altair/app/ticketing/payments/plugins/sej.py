# -*- coding:utf-8 -*-
import re
import logging
from datetime import datetime, timedelta
from zope.interface import implementer
from lxml import etree
from decimal import Decimal
import numpy
import pystache
from pyramid.response import Response
from sqlalchemy.sql.expression import desc
from altair.pyramid_dynamic_renderer import lbr_view_config
from altair.app.ticketing.cart.interfaces import ICartPayment, ICartDelivery
from altair.app.ticketing.mails.interfaces import (
    ICompleteMailResource,
    IOrderCancelMailResource,
    ILotsAcceptedMailResource,
    ILotsElectedMailResource,
    ILotsRejectedMailResource,
    )
from altair.app.ticketing.utils import clear_exc
from altair.app.ticketing.core import models as c_models
from altair.app.ticketing.orders import models as order_models
from altair.app.ticketing.sej import userside_api
from altair.app.ticketing.sej.exceptions import SejErrorBase, SejError
from altair.app.ticketing.sej.models import SejOrder, SejPaymentType, SejTicketType, SejOrderUpdateReason
from altair.app.ticketing.sej import api as sej_api
from altair.app.ticketing.sej.utils import han2zen

from altair.app.ticketing.tickets.convert import convert_svg
from altair.app.ticketing.tickets.utils import (
    NumberIssuer,
    build_dicts_from_ordered_product_item,
    build_dicts_from_carted_product_item,
    transform_matrix_from_ticket_format
    )
from altair.app.ticketing.core.utils import ApplicableTicketsProducer
from altair.app.ticketing.cart import helpers as cart_helper

from ..interfaces import IPaymentPlugin, IOrderPayment, IDeliveryPlugin, IPaymentDeliveryPlugin, IOrderDelivery, ISejDeliveryPlugin
from ..exceptions import PaymentPluginException, OrderLikeValidationFailure
from . import SEJ_PAYMENT_PLUGIN_ID as PAYMENT_PLUGIN_ID
from . import SEJ_DELIVERY_PLUGIN_ID as DELIVERY_PLUGIN_ID

logger = logging.getLogger(__name__)

class SejPluginFailure(PaymentPluginException):
    pass

def includeme(config):
    config.include('altair.app.ticketing.sej')
    config.include('altair.app.ticketing.sej.userside_impl')
    # 決済系(マルチ決済)
    settings = config.registry.settings
    config.add_payment_plugin(SejPaymentPlugin(), PAYMENT_PLUGIN_ID)
    config.add_delivery_plugin(SejDeliveryPlugin(), DELIVERY_PLUGIN_ID)
    config.add_payment_delivery_plugin(SejPaymentDeliveryPlugin(), PAYMENT_PLUGIN_ID, DELIVERY_PLUGIN_ID)
    config.scan(__name__)

def _overridable_payment(path, fallback_ua_type=None):
    from . import _template
    return _template(path, type='overridable', for_='payments', plugin_type='payment', plugin_id=PAYMENT_PLUGIN_ID, fallback_ua_type=fallback_ua_type)

def _overridable_delivery(path, fallback_ua_type=None):
    from . import _template
    return _template(path, type='overridable', for_='payments', plugin_type='delivery', plugin_id=DELIVERY_PLUGIN_ID, fallback_ua_type=fallback_ua_type)

def get_payment_due_at(current_date, order_like):
    return order_like.payment_due_at

def get_ticketing_start_at(current_date, order_like):
    return order_like.issuing_start_at

def get_ticketing_due_at(current_date, order_like):
    return order_like.issuing_end_at

def get_sej_ticket_data(product_item, ticket_type, svg, ticket_template_id=None, token_id=None):
    assert ticket_template_id is not None
    performance = product_item.performance

    return dict(
        ticket_type         = ticket_type,
        event_name          = re.sub('[ \-\.,;\'\"]', '', han2zen(performance.event.title)[:20]),
        performance_name    = re.sub('[ \-\.,;\'\"]', '', han2zen(performance.name)[:20]),
        ticket_template_id  = ticket_template_id,
        performance_datetime= performance.start_on,
        xml=svg,
        product_item_id = product_item.id,
        ordered_product_item_token_id=token_id
    )

def applicable_tickets_iter(bundle):
    return ApplicableTicketsProducer(bundle).sej_only_tickets()

def get_ticket_template_id_from_ticket_format(ticket_format):
    retval = None
    aux = ticket_format.data.get('aux')
    if aux is not None:
        retval = aux.get('sej_ticket_template_id')
    if retval is None:
        retval = u'TTTS000001' # XXX: デフォルト
    return retval

def get_ticket_count(request, order_like):
    return sum(
        element.quantity * sum(1 for ticket in applicable_tickets_iter(element.product_item.ticket_bundle))
        for item in order_like.items
        for element in item.elements
        )

def get_tickets(request, order, ticket_template_id=None):
    tickets = []
    issuer = NumberIssuer()
    for ordered_product in order.items:
        for ordered_product_item in ordered_product.elements:
            dicts = build_dicts_from_ordered_product_item(ordered_product_item, ticket_number_issuer=issuer)
            bundle = ordered_product_item.product_item.ticket_bundle
            for seat, dict_ in dicts:
                for ticket in applicable_tickets_iter(bundle):
                    if ticket.principal:
                        ticket_type = SejTicketType.TicketWithBarcode
                        #tkt1200 バーコードありチケットについてはOrderedProductItemTokenとSejTicketを関連付けたい
                        token_id = dict_.get(u'token_id')
                    else:
                        ticket_type = SejTicketType.ExtraTicket
                        token_id = None
                    ticket_format = ticket.ticket_format
                    ticket_template_id = get_ticket_template_id_from_ticket_format(ticket_format)
                    transform = transform_matrix_from_ticket_format(ticket_format)
                    template_record = sej_api.get_ticket_template_record(request, ticket_template_id)
                    notation_version = template_record.notation_version if template_record is not None else 1
                    #tkt330 プレースホルダーを二重交換
                    ticket_drawing_data = pystache.render(ticket.data['drawing'], dict_)
                    ticket_drawing_data = pystache.render(ticket_drawing_data, dict_)
                    svg = etree.tostring(
                        convert_svg(
                            etree.ElementTree(
                                etree.fromstring(ticket_drawing_data)
                                ),
                            global_transform=transform,
                            notation_version=notation_version
                            ),
                        encoding=unicode
                        )
                    ticket = get_sej_ticket_data(ordered_product_item.product_item, ticket_type, svg, ticket_template_id, token_id)
                    tickets.append(ticket)
    return tickets

def get_tickets_from_cart(request, cart, now):
    tickets = []
    issuer = NumberIssuer()
    for carted_product in cart.items:
        for carted_product_item in carted_product.elements:
            bundle = carted_product_item.product_item.ticket_bundle
            dicts = build_dicts_from_carted_product_item(carted_product_item, now=now, ticket_number_issuer=issuer)
            for (seat, dict_) in dicts:
                for ticket in applicable_tickets_iter(bundle):
                    if ticket.principal:
                        ticket_type = SejTicketType.TicketWithBarcode
                        #tkt1200 バーコードありチケットについてはOrderedProductItemTokenとSejTicketを関連付けたい
                        token_id = dict_.get(u'token_id')
                    else:
                        ticket_type = SejTicketType.ExtraTicket
                        token_id = None
                    ticket_format = ticket.ticket_format
                    ticket_template_id = get_ticket_template_id_from_ticket_format(ticket_format)
                    transform = transform_matrix_from_ticket_format(ticket_format)
                    template_record = sej_api.get_ticket_template_record(request, ticket_template_id)
                    notation_version = template_record.notation_version if template_record is not None else 1
                    #tkt330 プレースホルダーを二重交換
                    ticket_drawing_data = pystache.render(ticket.data['drawing'], dict_)
                    ticket_drawing_data = pystache.render(ticket_drawing_data, dict_)
                    svg = etree.tostring(
                        convert_svg(
                            etree.ElementTree(
                                etree.fromstring(ticket_drawing_data)
                                ),
                            global_transform=transform,
                            notation_version=notation_version
                            ),
                        encoding=unicode
                        )
                    ticket = get_sej_ticket_data(carted_product_item.product_item, ticket_type, svg, ticket_template_id, token_id)
                    tickets.append(ticket)
    return tickets

SEJ_ORDER_ATTRS = [
    'payment_type',
    'order_no',
    'user_name',
    'user_name_kana',
    'tel',
    'zip_code',
    'email',
    'total_price',
    'ticket_price',
    'commission_fee',
    'ticketing_fee',
    'payment_due_at',
    'ticketing_start_at',
    'ticketing_due_at',
    'regrant_number_due_at',
    ]

def is_same_sej_order(sej_order, sej_args, ticket_dicts):
    for k in SEJ_ORDER_ATTRS:
        v1 = getattr(sej_order, k)
        v2 = sej_args[k]
        if v1 != v2:
            logger.debug('%s differs (%r != %r)' % (k, v1, v2))
            return False

    if int(sej_order.payment_type) != SejPaymentType.PrepaymentOnly.v:
        # 発券が伴う場合は ticket も比較する
        tickets = sej_order.tickets
        if len(ticket_dicts) != len(tickets):
            return False

        for ticket, d in zip(sorted(tickets, key=lambda ticket: ticket.ticket_idx), ticket_dicts):
            if int(ticket.ticket_type) != int(d['ticket_type']):
                return False
            if ticket.event_name != d['event_name']:
                return False
            if ticket.performance_name != d['performance_name']:
                return False
            if ticket.performance_datetime != d['performance_datetime']:
                return False
            if ticket.ticket_template_id != d['ticket_template_id']:
                return False
            if ticket.product_item_id != d['product_item_id']:
                return False
            if ticket.ticket_data_xml != d['xml']:
                return False
    return True

def refresh_order(request, tenant, order, update_reason, current_date=None):
    from altair.app.ticketing.sej.models import _session
    if current_date is None:
        current_date = datetime.now()
    sej_order = sej_api.get_sej_order(order.order_no, session=_session)
    if sej_order is None:
        raise SejPluginFailure('no corresponding SejOrder found', order_no=order.order_no, back_url=None)

    # 代引もしくは前払後日発券の場合は payment_type の決定を再度行う (refs. #10350)
    if int(sej_order.payment_type) in (int(SejPaymentType.CashOnDelivery), int(SejPaymentType.Prepayment)):
        payment_type = int(determine_payment_type(current_date, order))
    else:
        payment_type = int(sej_order.payment_type)

    sej_args = build_sej_args(payment_type, order, order.created_at, regrant_number_due_at=sej_order.regrant_number_due_at)
    ticket_dicts = get_tickets(request, order)

    if is_same_sej_order(sej_order, sej_args, ticket_dicts):
        logger.info('the resulting order is the same as the old one; will do nothing')
        return

    if int(sej_order.payment_type) == SejPaymentType.PrepaymentOnly.v:
        if order.paid_at is not None:
            raise SejPluginFailure('already paid', order_no=order.order_no, back_url=None)
    else:
        if order.delivered_at is not None:
            raise SejPluginFailure('already delivered', order_no=order.order_no, back_url=None)

    if payment_type != int(sej_order.payment_type):
        logger.info('new sej order will be created as payment type is being changed: %d => %d' % (int(sej_order.payment_type), payment_type))

        new_sej_order = sej_order.new_branch()
        new_sej_order.tickets = sej_api.build_sej_tickets_from_dicts(
            sej_order.order_no,
            ticket_dicts,
            lambda idx: None
            )
        for k, v in sej_args.items():
            setattr(new_sej_order, k, v)
        new_sej_order.total_ticket_count = new_sej_order.ticket_count = len(new_sej_order.tickets)

        try:
            new_sej_order = sej_api.do_sej_order(
                request,
                tenant=tenant,
                sej_order=new_sej_order,
                session=_session
                )
            sej_api.cancel_sej_order(request, tenant=tenant, sej_order=sej_order, origin_order=order, now=current_date)
        except SejErrorBase:
            raise SejPluginFailure('refresh_order', order_no=order.order_no, back_url=None)
    else:
        new_sej_order = sej_order.new_branch()
        new_sej_order.tickets = sej_api.build_sej_tickets_from_dicts(
            sej_order.order_no,
            ticket_dicts,
            lambda idx: None
            )
        for k, v in sej_args.items():
            setattr(new_sej_order, k, v)
        new_sej_order.total_ticket_count = new_sej_order.ticket_count = len(new_sej_order.tickets)

        try:
            new_sej_order = sej_api.refresh_sej_order(
                request,
                tenant=tenant,
                sej_order=new_sej_order,
                update_reason=update_reason,
                session=_session
                )
            sej_order.cancel_at = new_sej_order.created_at
            _session.add(sej_order)
            _session.commit()
        except SejErrorBase:
            raise SejPluginFailure('refresh_order', order_no=order.order_no, back_url=None)

def refund_order(request, tenant, order, refund_record, now=None):
    sej_orders = sej_api.get_valid_sej_orders(order.order_no)
    if order.paid_at is None:
        raise SejPluginFailure(u'cannot refund an order that is not paid yet')
    if order.issued_at is None:
        logger.warning("trying to refund SEJ order that is not marked issued: %s" % order.order_no)
    refund = refund_record.refund
    performance = order.performance
    try:
        for sej_order in sej_orders:
            if int(sej_order.payment_type) == int(SejPaymentType.PrepaymentOnly):
                continue
            sej_api.refund_sej_order(
                request,
                tenant=tenant,
                sej_order=sej_order,
                performance_name=performance.name,
                performance_code=performance.code,
                performance_start_on=order.performance.start_on,
                per_order_fee=refund_record.refund_per_order_fee,
                per_ticket_fee=refund_record.refund_per_ticket_fee,
                refund_start_at=refund.start_at,
                refund_end_at=refund.end_at,
                need_stub=refund.need_stub,
                ticket_expire_at=refund.end_at + timedelta(days=+7),
                ticket_price_getter=lambda sej_ticket: refund_record.get_refund_ticket_price(sej_ticket.product_item_id),
                refund_total_amount=refund_record.refund_total_amount,
                now=now
                )
    except SejErrorBase:
        raise SejPluginFailure('refund_order', order_no=order.order_no, back_url=None)

def cancel_order(request, tenant, order, now=None):
    sej_order = sej_api.get_sej_order(order.order_no)
    if int(sej_order.payment_type) in (SejPaymentType.PrepaymentOnly.v, SejPaymentType.CashOnDelivery.v) and order.paid_at is not None:
        refund_order(request, tenant, order, order, now)
    else:
        if sej_order is None:
            raise SejPluginFailure('no corresponding SejOrder found for order %s' % order.order_no)
        try:
            sej_api.cancel_sej_order(request, tenant=tenant, sej_order=sej_order, origin_order=order, now=now)
        except SejError:
            raise SejPluginFailure('cancel_order', order_no=order.order_no, back_url=None)

def build_sej_args(payment_type, order_like, now, regrant_number_due_at):
    shipping_address = order_like.shipping_address
    tel1 = shipping_address.tel_1 and shipping_address.tel_1.replace('-', '')
    tel2 = shipping_address.tel_2 and shipping_address.tel_2.replace('-', '')
    ticketing_start_at = get_ticketing_start_at(now, order_like)
    ticketing_due_at = get_ticketing_due_at(now, order_like)
    if int(payment_type) == int(SejPaymentType.Paid):
        total_price         = 0
        ticket_price        = 0
        commission_fee      = 0
        ticketing_fee       = 0
        payment_due_at      = None
        ticketing_start_at  = get_ticketing_start_at(now, order_like)
        ticketing_due_at    = get_ticketing_due_at(now, order_like)
        if ticketing_due_at is None:
            # この処理は代済発券のみでよい
            # 発券期限はつねに確定させておかなければ再付番できない
            ticketing_due_at = now + timedelta(days=365)
    elif int(payment_type) == int(SejPaymentType.PrepaymentOnly):
        # 支払いのみの場合は、ticketing_fee が無視されるので、commission に算入してあげないといけない。
        total_price         = order_like.total_amount
        ticket_price        = order_like.total_amount - (order_like.system_fee + order_like.special_fee + order_like.transaction_fee + order_like.delivery_fee)
        commission_fee      = order_like.system_fee + order_like.special_fee + order_like.transaction_fee + order_like.delivery_fee
        ticketing_fee       = 0
        ticketing_start_at  = None
        ticketing_due_at    = None
        payment_due_at      = get_payment_due_at(now, order_like)
    elif int(payment_type) in (int(SejPaymentType.CashOnDelivery), int(SejPaymentType.Prepayment)):
        total_price         = order_like.total_amount
        ticket_price        = order_like.total_amount - (order_like.system_fee + order_like.special_fee + order_like.transaction_fee + order_like.delivery_fee)
        commission_fee      = order_like.system_fee + order_like.special_fee + order_like.transaction_fee
        ticketing_fee       = order_like.delivery_fee
        payment_due_at      = get_payment_due_at(now, order_like)
        if payment_due_at is None:
            raise SejPluginFailure('payment_due_at is not specified', order_no=order_like.order_no, back_url=None)
        if payment_due_at < now:
            raise SejPluginFailure("payment_due_at ({0:'%Y-%m-%d %H:%M:%S}') < the current time ({1:'%Y-%m-%d %H:%M:%S}')".format(payment_due_at, now), order_no=order_like.order_no, back_url=None)
        if payment_due_at >= now + timedelta(days=365):
            raise SejPluginFailure("payment_due_at ({0:'%Y-%m-%d %H:%M:%S}') >= 365 days after the current time ({1:'%Y-%m-%d %H:%M:%S}')".format(payment_due_at, now), order_no=order_like.order_no, back_url=None)
        if ticketing_due_at is not None:
            if ticketing_due_at <= payment_due_at:
                logger.warning("ticketing_due_at ({0:'%Y-%m-%d %H:%M:%S}) < payment_due_at ({1:'%Y-%m-%d %H:%M:%S})".format(ticketing_due_at, payment_due_at))
        if int(payment_type) == int(SejPaymentType.CashOnDelivery):
            if ticketing_start_at is not None:
                if ticketing_start_at > payment_due_at:
                    logger.warning("ticketing_start_at ({0:'%Y-%m-%d %H:%M:%S}) > payment_due_at ({1:'%Y-%m-%d %H:%M:%S})".format(ticketing_start_at, payment_due_at))
            ticketing_start_at  = None
            ticketing_due_at    = None
    else:
        raise SejPluginFailure('unknown payment type %s' % payment_type, order_no=order_like.order_no, back_url=None)

    return dict(
        payment_type        = u'%d' % int(payment_type),
        order_no            = order_like.order_no,
        user_name           = build_user_name(shipping_address),
        user_name_kana      = build_user_name_kana(shipping_address),
        tel                 = tel1 if tel1 else tel2,
        zip_code            = shipping_address.zip.replace('-', '') if shipping_address.zip else '',
        email               = shipping_address.email_1 or shipping_address.email_2 or '',
        total_price         = total_price,
        ticket_price        = ticket_price,
        commission_fee      = commission_fee,
        ticketing_fee       = ticketing_fee,
        payment_due_at      = payment_due_at,
        ticketing_start_at  = ticketing_start_at,
        ticketing_due_at    = ticketing_due_at,
        regrant_number_due_at = regrant_number_due_at
        )

def build_user_name(shipping_address):
    return u'%s%s' % (shipping_address.last_name, shipping_address.first_name)

def build_user_name_kana(shipping_address):
    return u'%s%s' % (shipping_address.last_name_kana, shipping_address.first_name_kana)

def determine_payment_type(current_date, order_like):
    if order_like.payment_start_at is not None and \
       order_like.payment_start_at != order_like.issuing_start_at:
        # 前払後日発券
        if order_like.payment_start_at > current_date:
            raise SejPluginFailure(u'order_like.payment_start_at cannot be a future date', order_no=order_like.order_no, back_url=None)
        payment_type = SejPaymentType.Prepayment
    else:
        # 代引
        payment_type = SejPaymentType.CashOnDelivery
    return payment_type


def _build_order_info(sej_order):
    retval = {}
    if sej_order.billing_number:
        retval[u'billing_number'] = sej_order.billing_number
    if sej_order.exchange_number:
        retval[u'exchange_number'] = sej_order.exchange_number
    return retval

def get_sej_order_info(request, order):
    sej_order = sej_api.get_sej_order(order.order_no, fetch_canceled=True)
    retval = _build_order_info(sej_order)
    if sej_order.pay_store_name:
        retval[u'pay_store_name'] = sej_order.pay_store_name
    if sej_order.ticketing_store_name:
        retval[u'ticketing_store_name'] = sej_order.ticketing_store_name
    retval[u'exchange_sheet'] = dict(
        url=sej_order.exchange_sheet_url,
        number=sej_order.exchange_sheet_number
        )
    retval[u'branches'] = [_build_order_info(branch) for branch in sej_order.branches(sej_order.order_no) if branch != sej_order]
    return retval

# http://www.unicode.org/charts/PDF/U30A0.pdf
katakana_regex = re.compile(ur'^[\u30a1-\u30f6\u30fb\u30fc\u30fd\u30feー]+$')

SEJ_MAX_ALLOWED_AMOUNT = Decimal('300000')

def validate_sej_order_cancellation(request, order, now):
    sej_order = sej_api.get_sej_order(order.order_no)
    sej_tenant = userside_api.lookup_sej_tenant(request, order.organization_id)

    sej_api.validate_sej_order_cancellation(request, sej_tenant, sej_order, order, now)

def validate_order_like(request, current_date, order_like, update=False, ticketing=True):
    if ticketing and get_ticket_count(request, order_like) > 20:
        raise OrderLikeValidationFailure(u'cannot handle more than 20 tickets', '')
    if order_like.shipping_address is not None:
        tel = order_like.shipping_address.tel_1 or order_like.shipping_address.tel_2
        if not tel:
            raise OrderLikeValidationFailure(u'no phone number specified', 'shipping_address.tel_1')
        elif len(tel) > 12 or re.match(ur'[^0-9]', tel):
            raise OrderLikeValidationFailure(u'invalid phone number', 'shipping_address.tel_2')
        if not order_like.shipping_address.last_name:
            raise OrderLikeValidationFailure(u'no last name specified', 'shipping_address.last_name')
        if not order_like.shipping_address.first_name:
            raise OrderLikeValidationFailure(u'no first name specified', 'shipping_address.first_name')
        user_name = build_user_name(order_like.shipping_address)
        try:
            user_name_sjis = user_name.encode('CP932')
        except UnicodeEncodeError:
            raise OrderLikeValidationFailure(u'user name contains a character that is not encodable as CP932', 'shipping_address.last_name')
        if len(user_name_sjis) > 40:
            raise OrderLikeValidationFailure(u'user name too long', 'shipping_address.last_name')
        if not order_like.shipping_address.last_name_kana:
            raise OrderLikeValidationFailure(u'no last name (kana) specified', 'shipping_address.last_name_kana')
        if not re.match(katakana_regex, order_like.shipping_address.last_name_kana):
            raise OrderLikeValidationFailure(u'last name (kana) contains non-katakana characters', 'shipping_address.last_name_kana')
        if not order_like.shipping_address.first_name_kana:
            raise OrderLikeValidationFailure(u'no first name (kana) specified', 'shipping_address.first_name_kana')
        if not re.match(katakana_regex, order_like.shipping_address.first_name_kana):
            raise OrderLikeValidationFailure(u'first name (kana) contains non-katakana characters', 'shipping_address.first_name_kana')
        user_name_kana = build_user_name_kana(order_like.shipping_address)
        if len(user_name_kana.encode('CP932')) > 40:
            raise OrderLikeValidationFailure(u'user name kana too long', 'shipping_address.last_name_kana')
        if order_like.shipping_address.zip and not re.match(ur'^[0-9]{7}$', order_like.shipping_address.zip.replace(u'-', u'')):
            raise OrderLikeValidationFailure(u'invalid zipcode specified', 'shipping_address.zip')
        email = order_like.shipping_address.email_1 or order_like.shipping_address.email_2
        if email and len(email) > 64:
            raise OrderLikeValidationFailure(u'invalid email address', 'shipping_address.email_1')
    else:
        logger.debug('order_like.shipping_address is None')

    payment_type = None
    if order_like.payment_delivery_pair.payment_method.payment_plugin_id == PAYMENT_PLUGIN_ID:
        if order_like.payment_delivery_pair.delivery_method.delivery_plugin_id == DELIVERY_PLUGIN_ID:
            try:
                payment_type = determine_payment_type(current_date, order_like)
            except SejPluginFailure as e:
                raise OrderLikeValidationFailure(e.message, 'payment_start_at')
        else:
            payment_type = int(SejPaymentType.PrepaymentOnly)
    else:
        payment_type = int(SejPaymentType.Paid)

    if payment_type is not None:
        _payment_type = int(payment_type)
        if _payment_type == int(SejPaymentType.CashOnDelivery) or (not update and _payment_type == int(SejPaymentType.Prepayment)):
            payment_due_at = get_payment_due_at(current_date, order_like)
            if payment_due_at < current_date:
                raise OrderLikeValidationFailure(u'payment_due_at (%s) < now (%s)' % (payment_due_at, current_date) , 'order.payment_due_at')

        if int(payment_type) != int(SejPaymentType.PrepaymentOnly):
            ticketing_due_at = get_ticketing_due_at(current_date, order_like)
            if ticketing_due_at is not None and ticketing_due_at < current_date:
                raise OrderLikeValidationFailure(u'issuing_end_at (%s) < now (%s)' % (ticketing_due_at, current_date), 'order.issuing_end_at')

    if payment_type is not None and payment_type != int(SejPaymentType.Paid):
        if order_like.total_amount > SEJ_MAX_ALLOWED_AMOUNT:
            raise OrderLikeValidationFailure(u'total_amount exceeds the maximum allowed amount', 'order.total_amount')
        elif order_like.total_amount <= 0:
            raise OrderLikeValidationFailure(u'total_amount is zero', 'order.total_amount')

@implementer(IPaymentPlugin)
class SejPaymentPlugin(object):
    def validate_order(self, request, order_like, update=False):
        validate_order_like(request, datetime.now(), order_like, update, ticketing=False)

    def validate_order_cancellation(self, request, order, now):
        """ キャンセルバリデーション """
        validate_sej_order_cancellation(request, order, now)

    def prepare(self, request, cart):
        """  """

    @clear_exc
    def finish(self, request, cart):
        """ 売り上げ確定 """
        logger.debug('Sej Payment')
        order = order_models.Order.create_from_cart(cart)
        cart.finish()
        self.finish2(request, order)
        return order

    @clear_exc
    def finish2(self, request, order_like):
        current_date = datetime.now()
        tenant = userside_api.lookup_sej_tenant(request, order_like.organization_id)
        try:
            sej_order = sej_api.create_sej_order(   
                request,
                **build_sej_args(SejPaymentType.PrepaymentOnly, order_like, current_date, None)
                )
            sej_api.do_sej_order(
                request,
                tenant=tenant,
                sej_order=sej_order
                )
        except SejErrorBase:
            raise SejPluginFailure('payment plugin', order_no=order_like.order_no, back_url=None)

    def finished(self, request, order):
        """ 支払番号発行済か判定 """
        sej_order = sej_api.get_sej_order(order.order_no)
        if sej_order is None:
            return False

        return bool(sej_order.billing_number)

    @clear_exc
    def refresh(self, request, order, current_date=None):
        if current_date is None:
            current_date = datetime.now()
        settings = request.registry.settings
        tenant = userside_api.lookup_sej_tenant(request, order.organization_id)
        refresh_order(
            request,
            tenant=tenant,
            order=order,
            update_reason=SejOrderUpdateReason.Change,
            current_date=current_date
            )

    @clear_exc
    def cancel(self, request, order, now=None):
        tenant = userside_api.lookup_sej_tenant(request, order.organization_id)
        cancel_order(
            request,
            tenant=tenant,
            order=order,
            now=now
            )

    @clear_exc
    def refund(self, request, order, refund_record):
        """ *** 支払のみの場合は払戻しない *** """
        if order.paid_at is None:
            raise SejPluginFailure(u'cannot refund an order that is not paid yet', order_no=order.order_no, back_url=None)
        sej_order = sej_api.get_sej_order(order.order_no)
        assert int(sej_order.payment_type) == int(SejPaymentType.PrepaymentOnly)

    def get_order_info(self, request, order):
        return get_sej_order_info(request, order)


@implementer(ISejDeliveryPlugin)
class SejDeliveryPluginBase(object):
    def template_record_for_ticket_format(self, request, ticket_format):
        ticket_template_id = get_ticket_template_id_from_ticket_format(ticket_format)
        return sej_api.get_ticket_template_record(request, ticket_template_id)


@implementer(IDeliveryPlugin)
class SejDeliveryPlugin(SejDeliveryPluginBase):
    def validate_order(self, request, order_like, update=False):
        validate_order_like(request, datetime.now(), order_like, update, ticketing=True)

    def validate_order_cancellation(self, request, order, now):
        """ キャンセルバリデーション """
        validate_sej_order_cancellation(request, order, now)

    def prepare(self, request, cart):
        """  """

    @clear_exc
    def finish(self, request, cart):
        logger.debug('Sej Delivery')
        self.finish2(request, cart)

    @clear_exc
    def finish2(self, request, order_like):
        from altair.app.ticketing.cart.models import Cart
        shipping_address = order_like.shipping_address
        current_date = datetime.now()
        _365_days_from_now = current_date + timedelta(days=365)
        regrant_number_due_at = min(_365_days_from_now, order_like.issuing_end_at) if order_like.issuing_end_at is not None else _365_days_from_now
        tenant = userside_api.lookup_sej_tenant(request, order_like.organization_id)
        try:
            if isinstance(order_like, Cart):
                tickets = get_tickets_from_cart(request, order_like, current_date)
            else:
                tickets = get_tickets(request, order_like)
            sej_order = sej_api.create_sej_order(
                request,
                tickets=tickets,
                **build_sej_args(SejPaymentType.Paid, order_like, current_date, regrant_number_due_at)
                )
            sej_api.do_sej_order(
                request,
                tenant=tenant,
                sej_order=sej_order
                )
        except SejErrorBase:
            raise SejPluginFailure('delivery plugin', order_no=order_like.order_no, back_url=None)

    def finished(self, request, order):
        """ 支払番号発行済か判定 """
        sej_order = sej_api.get_sej_order(order.order_no)
        if sej_order is None:
            return False

        return bool(sej_order.exchange_number)

    @clear_exc
    def refresh(self, request, order, current_date=None):
        if current_date is None:
            current_date = datetime.now()
        tenant = userside_api.lookup_sej_tenant(request, order.organization_id)
        refresh_order(
            request,
            tenant=tenant,
            order=order,
            update_reason=SejOrderUpdateReason.Change,
            current_date=current_date
            )

    @clear_exc
    def cancel(self, request, order, now=None):
        tenant = userside_api.lookup_sej_tenant(request, order.organization_id)
        cancel_order(
            request,
            tenant=tenant,
            order=order,
            now=now
            )

    @clear_exc
    def refund(self, request, order, refund_record):
        if order.paid_at is None:
            raise SejPluginFailure(u'cannot refund an order that is not paid yet', order_no=order.order_no, back_url=None)
        tenant = userside_api.lookup_sej_tenant(request, order.organization_id)
        refund_order(
            request,
            tenant=tenant,
            order=order,
            refund_record=refund_record
            )

    def get_order_info(self, request, order):
        return get_sej_order_info(request, order)


@implementer(IPaymentDeliveryPlugin)
class SejPaymentDeliveryPlugin(SejDeliveryPluginBase):
    def validate_order(self, request, order_like, update=False):
        validate_order_like(request, datetime.now(), order_like, update, ticketing=True)

    def validate_order_cancellation(self, request, order, now):
        """ キャンセルバリデーション """
        validate_sej_order_cancellation(request, order, now)

    def prepare(self, request, cart):
        """  """

    @clear_exc
    def finish(self, request, cart):
        """  """
        logger.debug('Sej Payment and Delivery')
        order = order_models.Order.create_from_cart(cart)
        cart.finish()
        self.finish2(request, order)
        return order

    @clear_exc
    def finish2(self, request, order_like):
        current_date = datetime.now()
        _365_days_from_now = current_date + timedelta(days=365)
        regrant_number_due_at = min(_365_days_from_now, order_like.issuing_end_at) if order_like.issuing_end_at is not None else _365_days_from_now
        tenant = userside_api.lookup_sej_tenant(request, order_like.organization_id)
        payment_type = determine_payment_type(current_date, order_like)
        try:
            tickets = get_tickets(request, order_like)
            sej_order = sej_api.create_sej_order(
                request,
                tickets=tickets,
                **build_sej_args(payment_type, order_like, current_date, regrant_number_due_at)
                )
            sej_api.do_sej_order(
                request,
                tenant=tenant,
                sej_order=sej_order
                )
        except SejErrorBase:
            raise SejPluginFailure('payment/delivery plugin', order_no=order_like.order_no, back_url=None)

    def finished(self, request, order):
        """ 支払番号発行済か判定 """
        sej_order = sej_api.get_sej_order(order.order_no)
        if sej_order is None:
            return False

        return bool(sej_order.billing_number)

    @clear_exc
    def refresh(self, request, order, current_date=None):
        if current_date is None:
            current_date = datetime.now()
        tenant = userside_api.lookup_sej_tenant(request, order.organization_id)
        refresh_order(
            request,
            tenant=tenant,
            order=order,
            update_reason=SejOrderUpdateReason.Change,
            current_date=current_date
            )

    @clear_exc
    def cancel(self, request, order, now=None):
        tenant = userside_api.lookup_sej_tenant(request, order.organization_id)
        cancel_order(
            request,
            tenant=tenant,
            order=order,
            now=now
            )

    @clear_exc
    def refund(self, request, order, refund_record):
        if order.paid_at is None:
            raise SejPluginFailure(u'cannot refund an order that is not paid yet', order_no=order.order_no, back_url=None)
        tenant = userside_api.lookup_sej_tenant(request, order.organization_id)
        refund_order(
            request,
            tenant=tenant,
            order=order,
            refund_record=refund_record
            )

    def get_order_info(self, request, order):
        return get_sej_order_info(request, order)



def payment_type_to_string(payment_type):
    for entry in SejPaymentType:
        if int(payment_type) == entry.v:
            return entry.k
    return None

@lbr_view_config(context=IOrderDelivery, name="delivery-%d" % DELIVERY_PLUGIN_ID, renderer=_overridable_delivery('sej_delivery_complete.html'))
def sej_delivery_viewlet(context, request):
    order = context.order
    sej_order = sej_api.get_sej_order(order.order_no, fetch_canceled=True)
    payment_plugin_id = context.order.payment_delivery_pair.payment_method.payment_plugin_id
    payment_method = context.order.payment_delivery_pair.payment_method
    delivery_method = context.order.payment_delivery_pair.delivery_method
    payment_type = payment_type_to_string(sej_order.payment_type)
    now = datetime.now()

    return dict(
        order=order,
        payment_type=payment_type,
        can_receive_from_next_day= can_receive_from_next_day(now, sej_order),
        sej_order=sej_order,
        payment_method=payment_method,
        delivery_method=delivery_method
        )

def can_receive_from_next_day(now, sej_order):
    if sej_order is None:
        return False

    if sej_order.ticketing_start_at is None:
        return False

    # 前払い後日発券の場合は、翌日の〜文言を出さない。
    if int(sej_order.payment_type) == int(SejPaymentType.Prepayment):
        return False

    next_day = now + timedelta(days=1)
    return bool(next_day.year == sej_order.ticketing_start_at.year \
        and next_day.month == sej_order.ticketing_start_at.month \
        and next_day.day == sej_order.ticketing_start_at.day)

@lbr_view_config(context=ICartDelivery, name="delivery-%d" % DELIVERY_PLUGIN_ID,
             renderer=_overridable_delivery('sej_delivery_confirm.html'))
def sej_delivery_confirm_viewlet(context, request):
    return Response(text=u'セブン-イレブン受け取り')

@lbr_view_config(context=IOrderPayment, name="payment-%d" % PAYMENT_PLUGIN_ID,
             renderer=_overridable_delivery('sej_payment_complete.html'))
def sej_payment_viewlet(context, request):
    order = context.order
    sej_order = sej_api.get_sej_order(order.order_no, fetch_canceled=True)
    payment_method = context.order.payment_delivery_pair.payment_method
    delivery_method = context.order.payment_delivery_pair.delivery_method
    payment_type = payment_type_to_string(sej_order.payment_type)
    return dict(
        order=order,
        sej_order=sej_order,
        payment_type=payment_type,
        payment_method=payment_method,
        delivery_method=delivery_method
        )

@lbr_view_config(context=ICartPayment, name="payment-%d" % PAYMENT_PLUGIN_ID, renderer=_overridable_payment('sej_payment_confirm.html'))
def sej_payment_confirm_viewlet(context, request):
    return Response(text=u'セブン-イレブン支払い')


@lbr_view_config(context=ICompleteMailResource, name="payment-%d" % PAYMENT_PLUGIN_ID, renderer=_overridable_payment('sej_payment_mail_complete.html', fallback_ua_type='mail'))
def payment_mail_viewlet(context, request):
    """ 完了メール表示
    :param context: ICompleteMailPayment
    """
    provided_sej_order = getattr(context, 'sej_order', None)
    if provided_sej_order is not None:
        sej_order = provided_sej_order
    else:
        sej_order = sej_api.get_sej_order(context.order.order_no)
    delivery_plugin_id = context.order.payment_delivery_pair.delivery_method.delivery_plugin_id
    payment_method = context.order.payment_delivery_pair.payment_method
    delivery_method = context.order.payment_delivery_pair.delivery_method
    if sej_order is not None:
        payment_type = payment_type_to_string(sej_order.payment_type)
    else:
        payment_type = (
            SejPaymentType.CashOnDelivery
            if delivery_plugin_id == DELIVERY_PLUGIN_ID
            else SejPaymentType.PrepaymentOnly
            )
    return dict(
        sej_order=sej_order,
        h=cart_helper,
        notice=context.mail_data("P", "notice"),
        payment_type=payment_type,
        payment_method=payment_method,
        delivery_method=delivery_method
        )

@lbr_view_config(context=ICompleteMailResource, name="delivery-%d" % DELIVERY_PLUGIN_ID, renderer=_overridable_delivery('sej_delivery_mail_complete.html', fallback_ua_type='mail'))
def delivery_mail_viewlet(context, request):
    """ 完了メール表示
    :param context: ICompleteMailDelivery
    """
    provided_sej_order = getattr(context, 'sej_order', None)
    if provided_sej_order is not None:
        sej_order = provided_sej_order
    else:
        sej_order = sej_api.get_sej_order(context.order.order_no)
    payment_plugin_id = context.order.payment_delivery_pair.payment_method.payment_plugin_id
    payment_method = context.order.payment_delivery_pair.payment_method
    delivery_method = context.order.payment_delivery_pair.delivery_method
    now = datetime.now()
    _can_receive_from_next_day = None
    if sej_order is not None:
        payment_type = payment_type_to_string(sej_order.payment_type)
        _can_receive_from_next_day = \
            sej_order.ticketing_start_at is not None and \
            can_receive_from_next_day(now, sej_order)
    else:
        payment_type = (
            SejPaymentType.CashOnDelivery
            if payment_plugin_id == PAYMENT_PLUGIN_ID
            else SejPaymentType.Paid
            )
        _can_receive_from_next_day = (payment_plugin_id != PAYMENT_PLUGIN_ID)

    return dict(
        sej_order=sej_order,
        h=cart_helper,
        payment_type=payment_type,
        can_receive_from_next_day=_can_receive_from_next_day,
        notice=context.mail_data("D", "notice"),
        payment_method=payment_method,
        delivery_method=delivery_method
        )

@lbr_view_config(context=IOrderCancelMailResource, name="payment-%d" % PAYMENT_PLUGIN_ID)
@lbr_view_config(context=ILotsRejectedMailResource, name="payment-%d" % PAYMENT_PLUGIN_ID)
@lbr_view_config(context=ILotsAcceptedMailResource, name="payment-%d" % PAYMENT_PLUGIN_ID)
def payment_mail_notice_viewlet(context, request):
    return Response(context.mail_data("P", "notice"))

@lbr_view_config(context=IOrderCancelMailResource, name="delivery-%d" % DELIVERY_PLUGIN_ID)
@lbr_view_config(context=ILotsRejectedMailResource, name="delivery-%d" % DELIVERY_PLUGIN_ID)
@lbr_view_config(context=ILotsAcceptedMailResource, name="delivery-%d" % DELIVERY_PLUGIN_ID)
def delivery_mail_notice_viewlet(context, request):
    return Response(context.mail_data("D", "notice"))
