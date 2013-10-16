# -*- coding:utf-8 -*-
import re
import logging
from datetime import datetime, timedelta
from zope.interface import implementer
from lxml import etree
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

from altair.app.ticketing.models import DBSession
from altair.app.ticketing.core import models as c_models

from altair.app.ticketing.sej.api import get_sej_order
from altair.app.ticketing.sej.exceptions import SejErrorBase
from altair.app.ticketing.sej.ticket import SejTicketDataXml
from altair.app.ticketing.sej.models import SejOrder, SejTenant, SejPaymentType, SejTicketType, SejOrderUpdateReason
from altair.app.ticketing.sej.payment import request_order, request_update_order, build_sej_tickets_from_dicts
from altair.app.ticketing.sej.utils import han2zen

from altair.app.ticketing.tickets.convert import convert_svg
from altair.app.ticketing.tickets.utils import (
    as_user_unit,
    build_dicts_from_ordered_product_item,
    build_dicts_from_carted_product_item,
    transform_matrix_from_ticket_format
    )
from altair.app.ticketing.core.utils import ApplicableTicketsProducer
from altair.app.ticketing.cart import helpers as cart_helper

from ..interfaces import IPaymentPlugin, IOrderPayment, IDeliveryPlugin, IOrderDelivery
from ..exceptions import PaymentPluginException
from . import SEJ_PAYMENT_PLUGIN_ID as PAYMENT_PLUGIN_ID
from . import SEJ_DELIVERY_PLUGIN_ID as DELIVERY_PLUGIN_ID

logger = logging.getLogger(__name__)

class SejPluginFailure(PaymentPluginException):
    pass

def includeme(config):
    # 決済系(マルチ決済)
    settings = config.registry.settings
    config.add_payment_plugin(SejPaymentPlugin(), PAYMENT_PLUGIN_ID)
    config.add_delivery_plugin(SejDeliveryPlugin(template=settings["altair.sej.template_file"]), DELIVERY_PLUGIN_ID)
    config.add_payment_delivery_plugin(SejPaymentDeliveryPlugin(), PAYMENT_PLUGIN_ID, DELIVERY_PLUGIN_ID)
    config.scan(__name__)

def get_payment_due_at(current_date, cart):
    payment_period_days = cart.payment_delivery_pair.payment_period_days or 3
    payment_due_at = current_date + timedelta(days=payment_period_days)
    payment_due_at = payment_due_at.replace(hour=23, minute=59, second=59)
    return payment_due_at

def get_ticketing_start_at(current_date, cart):
    if cart.payment_delivery_pair.issuing_start_at:
        ticketing_start_at = cart.payment_delivery_pair.issuing_start_at
    else:
        ticketing_start_at = current_date + timedelta(days=cart.payment_delivery_pair.issuing_interval_days)
        ticketing_start_at = ticketing_start_at.replace(hour=00, minute=00, second=00)
    return ticketing_start_at

def get_sej_ticket_data(product_item, svg):
    performance = product_item.performance
    return dict(
        ticket_type         = SejTicketType.TicketWithBarcode,
        event_name          = re.sub('[ \-\.,;\'\"]', '', han2zen(performance.event.title)[:20]),
        performance_name    = re.sub('[ \-\.,;\'\"]', '', han2zen(performance.name)[:20]),
        ticket_template_id  = u'TTTS000001',
        performance_datetime= performance.start_on,
        xml = SejTicketDataXml(svg),
        product_item_id = product_item.id
    )

def applicable_tickets_iter(bundle):
    return ApplicableTicketsProducer(bundle).sej_only_tickets()

def get_tickets(order):
    tickets = []
    for ordered_product in order.ordered_products:
        for ordered_product_item in ordered_product.ordered_product_items:
            dicts = build_dicts_from_ordered_product_item(ordered_product_item)
            bundle = ordered_product_item.product_item.ticket_bundle
            for seat, dict_ in dicts:
                for ticket in applicable_tickets_iter(bundle):
                    ticket_format = ticket.ticket_format
                    transform = transform_matrix_from_ticket_format(ticket_format)
                    svg = etree.tostring(convert_svg(etree.ElementTree(etree.fromstring(pystache.render(ticket.data['drawing'], dict_))), transform), encoding=unicode)
                    ticket = get_sej_ticket_data(ordered_product_item.product_item, svg)
                    tickets.append(ticket)
    return tickets

def get_tickets_from_cart(cart, now):
    tickets = []
    for carted_product in cart.products:
        for carted_product_item in carted_product.items:
            bundle = carted_product_item.product_item.ticket_bundle
            dicts = build_dicts_from_carted_product_item(carted_product_item, now=now)
            for (seat, dict_) in dicts:
                for ticket in applicable_tickets_iter(bundle):
                    ticket_format = ticket.ticket_format
                    transform = transform_matrix_from_ticket_format(ticket_format)
                    svg = etree.tostring(convert_svg(etree.ElementTree(etree.fromstring(pystache.render(ticket.data['drawing'], dict_))), transform), encoding=unicode)
                    ticket = get_sej_ticket_data(carted_product_item.product_item, svg)
                    tickets.append(ticket)
    return tickets

def refresh_order(order, update_reason):
    sej_order = get_sej_order(order.order_no)
    if sej_order is None:
        raise Exception('no corresponding SejOrder found for order %s' % order.order_no)

    new_sej_order = sej_order.new_branch()
    new_sej_order.tickets = build_sej_tickets_from_dicts(
        sej_order,
        get_tickets(order),
        lambda idx: None
        )
    for k, v in build_sej_args(sej_order.payment_type, order, sej_order.created_at).items():
        setattr(new_sej_order, k, v)
    new_sej_order.total_ticket_count = new_sej_order.ticket_count = len(new_sej_order.tickets)

    DBSession.add(new_sej_order)

    try:
        request_update_order(new_sej_order, update_reason)
    except SejErrorBase:
        raise SejPluginFailure('refresh_order', order_no=order.order_no, back_url=None)


def build_sej_args(payment_type, order_like, now):
    shipping_address = order_like.shipping_address
    tel1 = shipping_address.tel_1 and shipping_address.tel_1.replace('-', '')
    tel2 = shipping_address.tel_2 and shipping_address.tel_2.replace('-', '')
    ticketing_start_at = get_ticketing_start_at(now, order_like)
    ticketing_due_at = order_like.payment_delivery_pair.issuing_end_at
    performance = order_like.performance
    if int(payment_type) == int(SejPaymentType.Paid):
        total_price         = 0
        ticket_price        = 0
        commission_fee      = 0
        ticketing_fee       = 0
        payment_due_at      = None
    elif int(payment_type) == int(SejPaymentType.PrepaymentOnly):
        # 支払いのみの場合は、ticketing_fee が無視されるので、commission に算入してあげないといけない。
        total_price         = order_like.total_amount
        ticket_price        = order_like.total_amount - (order_like.system_fee + order_like.special_fee + order_like.transaction_fee + order_like.delivery_fee)
        commission_fee      = order_like.system_fee + order_like.special_fee + order_like.transaction_fee + order_like.delivery_fee
        ticketing_fee       = 0
        payment_due_at      = get_payment_due_at(now, order_like)
    elif int(payment_type) in (int(SejPaymentType.CashOnDelivery), int(payment_type) == int(SejPaymentType.Prepayment)):
        total_price         = order_like.total_amount
        ticket_price        = order_like.total_amount - (order_like.system_fee + order_like.special_fee + order_like.transaction_fee + order_like.delivery_fee)
        commission_fee      = order_like.system_fee + order_like.special_fee + order_like.transaction_fee
        ticketing_fee       = order_like.delivery_fee
        payment_due_at      = get_payment_due_at(now, order_like)
    else:
        raise SejPluginFailure('unknown payment type %s' % payment_type, order_link.order_no, None)

    return dict(
        payment_type        = payment_type,
        order_no            = order_like.order_no,
        user_name           = u'%s%s' % (shipping_address.last_name, shipping_address.first_name),
        user_name_kana      = u'%s%s' % (shipping_address.last_name_kana, shipping_address.first_name_kana),
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
        regrant_number_due_at = performance.start_on + timedelta(days=1) if performance and performance.start_on else now + timedelta(days=365)
        )

@implementer(IPaymentPlugin)
class SejPaymentPlugin(object):

    def prepare(self, request, cart):
        """  """

    def finish(self, request, cart):
        """ 売り上げ確定 """
        logger.debug('Sej Payment')
        order = c_models.Order.create_from_cart(cart)
        cart.finish()

        current_date = datetime.now()

        settings = request.registry.settings
        tenant = SejTenant.filter_by(organization_id = cart.performance.event.organization.id).first()
        api_key = (tenant and tenant.api_key) or settings['sej.api_key']
        api_url = (tenant and tenant.inticket_api_url) or settings['sej.inticket_api_url']

        try:
            request_order(
                shop_name=tenant.shop_name,
                shop_id=tenant.shop_id,
                contact_01=tenant.contact_01,
                contact_02=tenant.contact_02,
                secret_key=api_key,
                hostname=api_url,
                **build_sej_args(SejPaymentType.PrepaymentOnly, cart, current_date)
                )
        except SejErrorBase:
            raise SejPluginFailure('payment plugin', order_no=order.order_no, back_url=None)

        return order

    def finished(self, request, order):
        """ 支払番号発行済か判定 """
        sej_order = get_sej_order(order.order_no)
        if sej_order is None:
            return False

        return bool(sej_order.billing_number)

    def refresh(self, request, order):
        if order.paid_at is not None:
            raise Exception('order %s is already paid' % order.order_no)
        refresh_order(order, SejOrderUpdateReason.Change)
 
@implementer(IDeliveryPlugin)
class SejDeliveryPlugin(object):
    def __init__(self, template=None):
        self.template = template

    def prepare(self, request, cart):
        """  """

    def finish(self, request, cart):
        logger.debug('Sej Delivery')

        shipping_address = cart.shipping_address
        current_date = datetime.now()

        settings = request.registry.settings
        tenant = SejTenant.filter_by(organization_id = cart.performance.event.organization.id).first()
        api_key = (tenant and tenant.api_key) or settings['sej.api_key']
        api_url = (tenant and tenant.inticket_api_url) or settings['sej.inticket_api_url']

        try:
            tickets = get_tickets_from_cart(cart, current_date)
            request_order(
                shop_name=tenant.shop_name,
                shop_id=tenant.shop_id,
                contact_01=tenant.contact_01,
                contact_02=tenant.contact_02,
                tickets=tickets,
                secret_key=api_key,
                hostname=api_url,
                **build_sej_args(SejPaymentType.Paid, cart, current_date)
                )
        except SejErrorBase:
            raise SejPluginFailure('delivery plugin', order_no=cart.order_no, back_url=None)

    def finished(self, request, order):
        """ 支払番号発行済か判定 """
        sej_order = get_sej_order(order.order_no)
        if sej_order is None:
            return False

        return bool(sej_order.exchange_number)

    def refresh(self, request, order):
        if order.delivered_at is not None:
            raise Exception('order %s is already delivered' % order.order_no)
        refresh_order(order, SejOrderUpdateReason.Change)

@implementer(IDeliveryPlugin)
class SejPaymentDeliveryPlugin(object):
    def prepare(self, request, cart):
        """  """

    def finish(self, request, cart):
        """  """
        logger.debug('Sej Payment and Delivery')
        order = c_models.Order.create_from_cart(cart)
        cart.finish()

        settings = request.registry.settings
        tenant = SejTenant.filter_by(organization_id = order.performance.event.organization.id).first()
        api_key = (tenant and tenant.api_key) or settings['sej.api_key']
        api_url = (tenant and tenant.inticket_api_url) or settings['sej.inticket_api_url']
        current_date = datetime.now()

        try:
            tickets = get_tickets(order)
            request_order(
                shop_name=tenant.shop_name,
                shop_id=tenant.shop_id,
                contact_01=tenant.contact_01,
                contact_02=tenant.contact_02,
                tickets=tickets,
                secret_key=api_key,
                hostname=api_url,
                **build_sej_args(SejPaymentType.CashOnDelivery, cart, current_date)
                )
        except SejErrorBase:
            raise SejPluginFailure('payment/delivery plugin', order_no=order.order_no, back_url=None)

        return order

    def finished(self, request, order):
        """ 支払番号発行済か判定 """
        sej_order = get_sej_order(order.order_no)
        if sej_order is None:
            return False

        return bool(sej_order.billing_number)

    def refresh(self, request, order):
        if order.paid_at is not None or order.delivered_at is not None:
            raise Exception('order %s is already paid / delivered' % order.order_no)
        refresh_order(order, SejOrderUpdateReason.Change)


@view_config(context=IOrderDelivery, name="delivery-%d" % DELIVERY_PLUGIN_ID, renderer='altair.app.ticketing.payments.plugins:templates/sej_delivery_complete.html')
@view_config(context=IOrderDelivery, request_type='altair.mobile.interfaces.IMobileRequest',
             name="delivery-%d" % DELIVERY_PLUGIN_ID, renderer='altair.app.ticketing.payments.plugins:templates/sej_delivery_complete_mobile.html')
def sej_delivery_viewlet(context, request):
    order = context.order
    sej_order = get_sej_order(order.order_no)
    payment_id = context.order.payment_delivery_pair.payment_method.payment_plugin_id
    delivery_method = context.order.payment_delivery_pair.delivery_method
    is_payment_with_sej = int(payment_id or -1) == PAYMENT_PLUGIN_ID
    return dict(
        order=order,
        is_payment_with_sej=is_payment_with_sej, 
        sej_order=sej_order,
        delivery_method=delivery_method,
    )

@view_config(context=ICartDelivery, name="delivery-%d" % DELIVERY_PLUGIN_ID, 
             renderer='altair.app.ticketing.payments.plugins:templates/sej_delivery_confirm.html')
def sej_delivery_confirm_viewlet(context, request):
    return Response(text=u'セブン-イレブン受け取り')

@view_config(context=IOrderPayment, name="payment-%d" % PAYMENT_PLUGIN_ID, 
             renderer='altair.app.ticketing.payments.plugins:templates/sej_payment_complete.html')
@view_config(context=IOrderPayment, request_type='altair.mobile.interfaces.IMobileRequest',
             name="payment-%d" % PAYMENT_PLUGIN_ID, renderer='altair.app.ticketing.payments.plugins:templates/sej_payment_complete_mobile.html')
def sej_payment_viewlet(context, request):
    order = context.order
    sej_order = get_sej_order(order.order_no)
    payment_method = context.order.payment_delivery_pair.payment_method
    return dict(
        order=order,
        sej_order=sej_order,
        payment_method=payment_method,
    )

@view_config(context=ICartPayment, name="payment-%d" % PAYMENT_PLUGIN_ID, renderer='altair.app.ticketing.payments.plugins:templates/sej_payment_confirm.html')
def sej_payment_confirm_viewlet(context, request):
    return Response(text=u'セブン-イレブン支払い')


@view_config(context=ICompleteMailPayment, name="payment-%d" % PAYMENT_PLUGIN_ID, renderer="altair.app.ticketing.payments.plugins:templates/sej_payment_mail_complete.html")
@view_config(context=ILotsElectedMailPayment, name="payment-%d" % PAYMENT_PLUGIN_ID, renderer="altair.app.ticketing.payments.plugins:templates/sej_payment_mail_complete.html")
def payment_mail_viewlet(context, request):
    """ 完了メール表示
    :param context: ICompleteMailPayment
    """
    sej_order = get_sej_order(context.order.order_no)
    payment_method = context.order.payment_delivery_pair.payment_method
    return dict(sej_order=sej_order, h=cart_helper, 
                notice=context.mail_data("notice"),
                payment_method=payment_method,
    )

@view_config(context=ICompleteMailDelivery, name="delivery-%d" % DELIVERY_PLUGIN_ID, renderer="altair.app.ticketing.payments.plugins:templates/sej_delivery_mail_complete.html")
@view_config(context=ILotsElectedMailDelivery, name="delivery-%d" % DELIVERY_PLUGIN_ID, renderer="altair.app.ticketing.payments.plugins:templates/sej_delivery_mail_complete.html")
def delivery_mail_viewlet(context, request):
    """ 完了メール表示
    :param context: ICompleteMailDelivery
    """
    sej_order = get_sej_order(context.order.order_no)
    payment_id = context.order.payment_delivery_pair.payment_method.payment_plugin_id
    delivery_method = context.order.payment_delivery_pair.delivery_method
    is_payment_with_sej = int(payment_id or -1) == PAYMENT_PLUGIN_ID
    return dict(sej_order=sej_order, h=cart_helper,
                is_payment_with_sej=is_payment_with_sej, 
                notice=context.mail_data("notice"),
                delivery_method=delivery_method)

@view_config(context=IOrderCancelMailPayment, name="payment-%d" % PAYMENT_PLUGIN_ID)
@view_config(context=IOrderCancelMailDelivery, name="delivery-%d" % DELIVERY_PLUGIN_ID)
@view_config(context=ILotsRejectedMailPayment, name="payment-%d" % PAYMENT_PLUGIN_ID)
@view_config(context=ILotsAcceptedMailPayment, name="payment-%d" % PAYMENT_PLUGIN_ID)
@view_config(context=ILotsRejectedMailDelivery, name="delivery-%d" % DELIVERY_PLUGIN_ID)
@view_config(context=ILotsAcceptedMailDelivery, name="delivery-%d" % DELIVERY_PLUGIN_ID)
def mail_notice_viewlet(context, request):
    return Response(context.mail_data("notice"))
