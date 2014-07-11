# -*- coding:utf-8 -*-
import re
import logging
from datetime import datetime, timedelta
from zope.interface import implementer
from lxml import etree
from decimal import Decimal
import numpy
import pystache
from pyramid.view import view_config
from pyramid.response import Response
from sqlalchemy.sql.expression import desc

from altair.app.ticketing.cart.interfaces import ICartPayment, ICartDelivery
from altair.app.ticketing.mails.interfaces import (
    ICompleteMailPayment, 
    IOrderCancelMailPayment,
    ICompleteMailDelivery,
    IOrderCancelMailDelivery,
    ILotsAcceptedMailPayment,
    ILotsAcceptedMailDelivery,
    ILotsElectedMailPayment,
    ILotsElectedMailDelivery,
    ILotsRejectedMailPayment,
    ILotsRejectedMailDelivery,
)

from altair.app.ticketing.utils import clear_exc
from altair.app.ticketing.core import models as c_models
from altair.app.ticketing.orders import models as order_models
from altair.app.ticketing.sej import userside_api
from altair.app.ticketing.sej.exceptions import SejErrorBase
from altair.app.ticketing.sej.models import SejOrder, SejPaymentType, SejTicketType, SejOrderUpdateReason
from altair.app.ticketing.sej.api import do_sej_order, refresh_sej_order, build_sej_tickets_from_dicts, create_sej_order, get_sej_order, get_ticket_template_record, refund_sej_order
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

from ..interfaces import IPaymentPlugin, IOrderPayment, IDeliveryPlugin, IOrderDelivery, ISejDeliveryPlugin
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

def _overridable_payment(path):
    from . import _template
    if _template is None:
        return '%s:templates/%s' % (__name__, path)
    else:
        return _template(path, type='overridable', for_='payments', plugin_type='payment', plugin_id=PAYMENT_PLUGIN_ID)

def _overridable_delivery(path):
    from . import _template
    if _template is None:
        return '%s:templates/%s' % (__name__, path)
    else:
        return _template(path, type='overridable', for_='payments', plugin_type='delivery', plugin_id=DELIVERY_PLUGIN_ID)

def get_payment_due_at(current_date, order_like):
    return order_like.payment_due_at

def get_ticketing_start_at(current_date, order_like):
    return order_like.issuing_start_at

def get_ticketing_due_at(current_date, order_like):
    return order_like.issuing_end_at

def get_sej_ticket_data(product_item, ticket_type, svg, ticket_template_id=None):
    assert ticket_template_id is not None
    performance = product_item.performance
    return dict(
        ticket_type         = ticket_type,
        event_name          = re.sub('[ \-\.,;\'\"]', '', han2zen(performance.event.title)[:20]),
        performance_name    = re.sub('[ \-\.,;\'\"]', '', han2zen(performance.name)[:20]),
        ticket_template_id  = ticket_template_id,
        performance_datetime= performance.start_on,
        xml=svg,
        product_item_id = product_item.id
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
                    else:
                        ticket_type = SejTicketType.Ticket
                    ticket_format = ticket.ticket_format
                    ticket_template_id = get_ticket_template_id_from_ticket_format(ticket_format)
                    transform = transform_matrix_from_ticket_format(ticket_format)
                    template_record = get_ticket_template_record(request, ticket_template_id)
                    notation_version = template_record.notation_version if template_record is not None else 1
                    svg = etree.tostring(
                        convert_svg(
                            etree.ElementTree(
                                etree.fromstring(pystache.render(ticket.data['drawing'], dict_))
                                ),
                            global_transform=transform,
                            notation_version=notation_version
                            ),
                        encoding=unicode
                        )
                    ticket = get_sej_ticket_data(ordered_product_item.product_item, ticket_type, svg, ticket_template_id)
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
                    else:
                        ticket_type = SejTicketType.Ticket
                    ticket_format = ticket.ticket_format
                    ticket_template_id = get_ticket_template_id_from_ticket_format(ticket_format)
                    transform = transform_matrix_from_ticket_format(ticket_format)
                    template_record = get_ticket_template_record(request, ticket_template_id)
                    notation_version = template_record.notation_version if template_record is not None else 1
                    svg = etree.tostring(
                        convert_svg(
                            etree.ElementTree(
                                etree.fromstring(pystache.render(ticket.data['drawing'], dict_))
                                ),
                            global_transform=transform,
                            notation_version=notation_version
                            ),
                        encoding=unicode
                        )
                    ticket = get_sej_ticket_data(carted_product_item.product_item, ticket_type, svg, ticket_template_id)
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

def refresh_order(request, tenant, order, update_reason):
    sej_order = get_sej_order(order.order_no)
    if sej_order is None:
        raise SejPluginFailure('no corresponding SejOrder found', order_no=order.order_no, back_url=None)

    sej_args = build_sej_args(sej_order.payment_type, order, order.created_at)
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

    new_sej_order = sej_order.new_branch()
    new_sej_order.tickets = build_sej_tickets_from_dicts(
        sej_order.order_no,
        ticket_dicts,
        lambda idx: None
        )
    for k, v in sej_args.items():
        setattr(new_sej_order, k, v)
    new_sej_order.total_ticket_count = new_sej_order.ticket_count = len(new_sej_order.tickets)

    try:
        refresh_sej_order(
            request,
            tenant=tenant,
            sej_order=new_sej_order,
            update_reason=update_reason
            )
    except SejErrorBase:
        raise SejPluginFailure('refresh_order', order_no=order.order_no, back_url=None)

def refund_order(request, tenant, order, refund_record, now=None):
    refund = refund_record.refund
    sej_order = get_sej_order(order.order_no)
    performance = order.performance
    try:
        refund_sej_order(
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
            refund_total_amount=order.refund_total_amount,
            now=now
            )
    except SejErrorBase:
        raise SejPluginFailure('refund_order', order_no=order.order_no, back_url=None)

def build_sej_args(payment_type, order_like, now):
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
        payment_due_at      = get_payment_due_at(now, order_like)
    elif int(payment_type) in (int(SejPaymentType.CashOnDelivery), int(SejPaymentType.Prepayment)):
        total_price         = order_like.total_amount
        ticket_price        = order_like.total_amount - (order_like.system_fee + order_like.special_fee + order_like.transaction_fee + order_like.delivery_fee)
        commission_fee      = order_like.system_fee + order_like.special_fee + order_like.transaction_fee
        ticketing_fee       = order_like.delivery_fee
        payment_due_at      = get_payment_due_at(now, order_like)
    else:
        raise SejPluginFailure('unknown payment type %s' % payment_type, order_no=order_link.order_no, back_url=None)

    regrant_number_due_at = None
    performance = order_like.sales_segment.performance
    if performance and (performance.start_on or performance.end_on):
        regrant_number_due_at = (performance.end_on or performance.start_on) + timedelta(days=1)
    regrant_number_due_at = regrant_number_due_at or now + timedelta(days=365)

    return dict(
        payment_type        = payment_type,
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

# http://www.unicode.org/charts/PDF/U30A0.pdf
katakana_regex = re.compile(ur'^[\u30a1-\u30f6\u30fb\u30fc\u30fd\u30feー]+$')

SEJ_MAX_ALLOWED_AMOUNT = Decimal('300000')

def validate_order_like(current_date, order_like):
    if order_like.shipping_address is None:
        raise OrderLikeValidationFailure(u'shipping address does not exist', 'shipping_address')
    tel = order_like.shipping_address.tel_1 or order_like.shipping_address.tel_2
    if not tel:
        raise OrderLikeValidationFailure(u'no phone number specified', 'shipping_address.tel_1')
    elif len(tel) > 12 or re.match(ur'[^0-9]', tel):
        raise OrderLikeValidationFailure(u'invalid phone number', 'shipping_address.tel_1')
    if not order_like.shipping_address.last_name:
        raise OrderLikeValidationFailure(u'no last name specified', 'shipping_address.last_name')
    if not order_like.shipping_address.first_name:
        raise OrderLikeValidationFailure(u'no first name specified', 'shipping_address.first_name')
    user_name = build_user_name(order_like.shipping_address)
    if len(user_name.encode('CP932')) > 40:
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
        if int(payment_type) == int(SejPaymentType.CashOnDelivery):
            if get_payment_due_at(current_date, order_like) < current_date:
                raise OrderLikeValidationFailure(u'payment_due_at < now', 'order.payment_due_at')

        if int(payment_type) != int(SejPaymentType.PrepaymentOnly):
            ticketing_due_at = get_ticketing_due_at(current_date, order_like)
            if ticketing_due_at is not None and ticketing_due_at < current_date:
                raise OrderLikeValidationFailure(u'issuing_end_at < now', 'order.issuing_end_at')

    if payment_type is not None and payment_type != int(SejPaymentType.Paid) and order_like.total_amount > SEJ_MAX_ALLOWED_AMOUNT:
        raise OrderLikeValidationFailure(u'total_amount exceeds the maximum allowed amount', 'order.total_amount')

@implementer(IPaymentPlugin)
class SejPaymentPlugin(object):
    def validate_order(self, request, order_like):
        validate_order_like(datetime.now(), order_like)

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
            sej_order = create_sej_order(   
                request,
                **build_sej_args(SejPaymentType.PrepaymentOnly, order_like, current_date)
                )
            do_sej_order(
                request,
                tenant=tenant,
                sej_order=sej_order
                )
        except SejErrorBase:
            raise SejPluginFailure('payment plugin', order_no=order_like.order_no, back_url=None)

    def finished(self, request, order):
        """ 支払番号発行済か判定 """
        sej_order = get_sej_order(order.order_no)
        if sej_order is None:
            return False

        return bool(sej_order.billing_number)

    @clear_exc
    def refresh(self, request, order):
        settings = request.registry.settings
        tenant = userside_api.lookup_sej_tenant(request, order.organization_id)
        refresh_order(
            request,
            tenant=tenant,
            order=order,
            update_reason=SejOrderUpdateReason.Change
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

@implementer(ISejDeliveryPlugin)
class SejDeliveryPluginBase(object):
    def template_record_for_ticket_format(self, request, ticket_format):
        ticket_template_id = get_ticket_template_id_from_ticket_format(ticket_format)
        return get_ticket_template_record(request, ticket_template_id)


@implementer(IDeliveryPlugin)
class SejDeliveryPlugin(SejDeliveryPluginBase):
    def validate_order(self, request, order_like):
        validate_order_like(datetime.now(), order_like)

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
        tenant = userside_api.lookup_sej_tenant(request, order_like.organization_id)
        try:
            if isinstance(order_like, Cart):
                tickets = get_tickets_from_cart(request, order_like, current_date)
            else:
                tickets = get_tickets(request, order_like)
            sej_order = create_sej_order(
                request,
                tickets=tickets,
                **build_sej_args(SejPaymentType.Paid, order_like, current_date)
                )
            do_sej_order(
                request,
                tenant=tenant,
                sej_order=sej_order
                )
        except SejErrorBase:
            raise SejPluginFailure('delivery plugin', order_no=order_like.order_no, back_url=None)

    def finished(self, request, order):
        """ 支払番号発行済か判定 """
        sej_order = get_sej_order(order.order_no)
        if sej_order is None:
            return False

        return bool(sej_order.exchange_number)

    @clear_exc
    def refresh(self, request, order):
        tenant = userside_api.lookup_sej_tenant(request, order.organization_id)
        refresh_order(
            request,
            tenant=tenant,
            order=order,
            update_reason=SejOrderUpdateReason.Change
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

@implementer(IDeliveryPlugin)
class SejPaymentDeliveryPlugin(SejDeliveryPluginBase):
    def validate_order(self, request, order_like):
        validate_order_like(datetime.now(), order_like)

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
        tenant = userside_api.lookup_sej_tenant(request, order_like.organization_id)
        payment_type = determine_payment_type(current_date, order_like)
        try:
            tickets = get_tickets(request, order_like)
            sej_order = create_sej_order(
                request,
                tickets=tickets,
                **build_sej_args(payment_type, order_like, current_date)
                )
            do_sej_order(
                request,
                tenant=tenant,
                sej_order=sej_order
                )
        except SejErrorBase:
            raise SejPluginFailure('payment/delivery plugin', order_no=order_like.order_no, back_url=None)

    def finished(self, request, order):
        """ 支払番号発行済か判定 """
        sej_order = get_sej_order(order.order_no)
        if sej_order is None:
            return False

        return bool(sej_order.billing_number)

    @clear_exc
    def refresh(self, request, order):
        tenant = userside_api.lookup_sej_tenant(request, order.organization_id)
        refresh_order(
            request,
            tenant=tenant,
            order=order,
            update_reason=SejOrderUpdateReason.Change
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


def payment_type_to_string(payment_type):
    for entry in SejPaymentType:
        if int(payment_type) == entry.v:
            return entry.k
    return None

@view_config(context=IOrderDelivery, name="delivery-%d" % DELIVERY_PLUGIN_ID, renderer=_overridable_delivery('sej_delivery_complete.html'))
@view_config(context=IOrderDelivery, request_type='altair.mobile.interfaces.IMobileRequest',
             name="delivery-%d" % DELIVERY_PLUGIN_ID, renderer=_overridable_delivery('sej_delivery_complete_mobile.html'))
def sej_delivery_viewlet(context, request):
    order = context.order
    sej_order = get_sej_order(order.order_no)
    payment_id = context.order.payment_delivery_pair.payment_method.payment_plugin_id
    delivery_method = context.order.payment_delivery_pair.delivery_method
    payment_type = payment_type_to_string(sej_order.payment_type)
    now = datetime.now()
    return dict(
        order=order,
        payment_type=payment_type,
        can_receive_from_next_day=can_receive_from_next_day(now, sej_order.ticketing_start_at),
        sej_order=sej_order,
        delivery_method=delivery_method,
    )

def can_receive_from_next_day(now, ticketing_start_at):
    if ticketing_start_at is None:
        return False

    next_day = now + timedelta(days=1)
    return bool(next_day.year == ticketing_start_at.year \
        and next_day.month == ticketing_start_at.month \
        and next_day.day == ticketing_start_at.day)

@view_config(context=ICartDelivery, name="delivery-%d" % DELIVERY_PLUGIN_ID,
             renderer=_overridable_delivery('sej_delivery_confirm.html'))
def sej_delivery_confirm_viewlet(context, request):
    return Response(text=u'セブン-イレブン受け取り')

@view_config(context=IOrderPayment, name="payment-%d" % PAYMENT_PLUGIN_ID, 
             renderer=_overridable_delivery('sej_payment_complete.html'))
@view_config(context=IOrderPayment, request_type='altair.mobile.interfaces.IMobileRequest',
             name="payment-%d" % PAYMENT_PLUGIN_ID, renderer=_overridable_payment('sej_payment_complete_mobile.html'))
def sej_payment_viewlet(context, request):
    order = context.order
    sej_order = get_sej_order(order.order_no)
    payment_method = context.order.payment_delivery_pair.payment_method
    payment_type = payment_type_to_string(sej_order.payment_type)
    return dict(
        order=order,
        sej_order=sej_order,
        payment_type=payment_type,
        payment_method=payment_method,
    )

@view_config(context=ICartPayment, name="payment-%d" % PAYMENT_PLUGIN_ID, renderer=_overridable_payment('sej_payment_confirm.html'))
def sej_payment_confirm_viewlet(context, request):
    return Response(text=u'セブン-イレブン支払い')


@view_config(context=ICompleteMailPayment, name="payment-%d" % PAYMENT_PLUGIN_ID, renderer=_overridable_payment('sej_payment_mail_complete.html'))
@view_config(context=ILotsElectedMailPayment, name="payment-%d" % PAYMENT_PLUGIN_ID, renderer=_overridable_payment('sej_payment_mail_complete.html'))
def payment_mail_viewlet(context, request):
    """ 完了メール表示
    :param context: ICompleteMailPayment
    """
    provided_sej_order = getattr(context, 'sej_order', None)
    if provided_sej_order is not None:
        sej_order = provided_sej_order
    else:
        sej_order = get_sej_order(context.order.order_no)
    delivery_plugin_id = context.order.payment_delivery_pair.delivery_method.delivery_plugin_id
    payment_method = context.order.payment_delivery_pair.payment_method
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
        notice=context.mail_data("notice"),
        payment_type=payment_type,
        payment_method=payment_method,
    )

@view_config(context=ICompleteMailDelivery, name="delivery-%d" % DELIVERY_PLUGIN_ID, renderer=_overridable_delivery('sej_delivery_mail_complete.html'))
@view_config(context=ILotsElectedMailDelivery, name="delivery-%d" % DELIVERY_PLUGIN_ID, renderer=_overridable_delivery('sej_delivery_mail_complete.html'))
def delivery_mail_viewlet(context, request):
    """ 完了メール表示
    :param context: ICompleteMailDelivery
    """
    provided_sej_order = getattr(context, 'sej_order', None)
    if provided_sej_order is not None:
        sej_order = provided_sej_order
    else:
        sej_order = get_sej_order(context.order.order_no)
    payment_id = context.order.payment_delivery_pair.payment_method.payment_plugin_id
    delivery_method = context.order.payment_delivery_pair.delivery_method
    now = datetime.now()
    if sej_order is not None:
        payment_type = payment_type_to_string(sej_order.payment_type)
        can_receive_from_next_day = \
            sej_order.ticketing_start_at is not None and \
            (sej_order.ticketing_start_at.day - now.day) == 1
    else:
        payment_type = (
            SejPaymentType.CashOnDelivery
            if payment_id == PAYMENT_PLUGIN_ID
            else SejPaymentType.Paid
            )
        can_receive_from_next_day = (payment_id != PAYMENT_PLUGIN_ID)

    return dict(
        sej_order=sej_order,
        h=cart_helper,
        payment_type=payment_type,
        can_receive_from_next_day=can_receive_from_next_day,
        notice=context.mail_data("notice"),
        delivery_method=delivery_method
        )

@view_config(context=IOrderCancelMailPayment, name="payment-%d" % PAYMENT_PLUGIN_ID)
@view_config(context=IOrderCancelMailDelivery, name="delivery-%d" % DELIVERY_PLUGIN_ID)
@view_config(context=ILotsRejectedMailPayment, name="payment-%d" % PAYMENT_PLUGIN_ID)
@view_config(context=ILotsAcceptedMailPayment, name="payment-%d" % PAYMENT_PLUGIN_ID)
@view_config(context=ILotsRejectedMailDelivery, name="delivery-%d" % DELIVERY_PLUGIN_ID)
@view_config(context=ILotsAcceptedMailDelivery, name="delivery-%d" % DELIVERY_PLUGIN_ID)
def mail_notice_viewlet(context, request):
    return Response(context.mail_data("notice"))
