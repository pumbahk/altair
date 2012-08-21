# -*- coding:utf-8 -*-
from zope.interface import implementer
from pyramid.view import view_config
from pyramid.response import Response

from ..interfaces import IPaymentPlugin, ICartPayment, IOrderPayment
from ..interfaces import IDeliveryPlugin, ICartDelivery, IOrderDelivery

from .. import logger

from pyramid.threadlocal import get_current_registry

from ticketing.core import models as c_models

from ticketing.sej.ticket import SejTicketDataXml
from ticketing.sej.models import SejOrder, SejTenant
from ticketing.sej.payment import request_order
from ticketing.sej.resources import SejPaymentType, SejTicketType
from ticketing.sej.utils import han2zen

from ticketing.tickets.convert import convert_svg
from ticketing.tickets.utils import *

from lxml import html, etree
from lxml.builder import E
from datetime import datetime, timedelta

PAYMENT_PLUGIN_ID = 3
DELIVERY_PLUGIN_ID = 2

def includeme(config):
    # 決済系(マルチ決済)
    config.add_payment_plugin(SejPaymentPlugin(), PAYMENT_PLUGIN_ID)
    config.add_delivery_plugin(SejDeliveryPlugin(), DELIVERY_PLUGIN_ID)
    config.add_payment_delivery_plugin(SejPaymentDeliveryPlugin(), PAYMENT_PLUGIN_ID, DELIVERY_PLUGIN_ID)
    config.scan(__name__)

def get_payment_due_at(current_date, cart):
    if cart.payment_delivery_pair.payment_period_days:
        payment_due_at = current_date + timedelta(days=cart.payment_delivery_pair.payment_period_days)
    else:
        payment_due_at = current_date + timedelta(days=3)
    return payment_due_at

def get_ticketing_start_at(current_date, cart):
    if cart.payment_delivery_pair.issuing_start_at:
        ticketing_start_at = cart.payment_delivery_pair.issuing_start_at
    else:
        ticketing_start_at = current_date + timedelta(days=cart.payment_delivery_pair.issuing_interval_days)
    return ticketing_start_at

def get_sej_order(order):
    return SejOrder.filter(SejOrder.order_id == order.order_no).first()

def get_ticket(order_no, product_item, svg):
    performance = product_item.performance
    return dict(
        ticket_type         = SejTicketType.TicketWithBarcode,
        event_name          = han2zen(performance.event.title)[:40].replace(' ', ''),
        performance_name    = han2zen(performance.name)[:40].replace(' ', ''),
        ticket_template_id  = u'TTTS000001',
        performance_datetime= performance.start_on,
        xml = SejTicketDataXml(svg)
    )

def get_tickets(order):
    tickets = []
    for ordered_product in order.items:
        for ordered_product_item in ordered_product.ordered_product_items:
            bundle = ordered_product_item.product_item.ticket_bundle
            dicts = build_dicts_from_ordered_product_item(ordered_product_item)
            for dict_ in dicts:
                for ticket in bundle.tickets:
                    svg = convert_svg(etree.parse(pystache.render(ticket.data['drawing'], dict_)))
                    ticket = get_ticket(order.order_no, ordered_product_item, svg)
                    tickets.append(ticket)
    return tickets

def get_tickets_from_cart(cart):
    tickets = list()
    for product in cart.products:
        for item in product.items:
            ticket = get_ticket(u'%012d' % cart.id, item)
            tickets.append(ticket)
    return tickets

@implementer(IPaymentPlugin)
class SejPaymentPlugin(object):

    def prepare(self, request, cart):
        """  """

    def finish(self, request, cart):
        """ 売り上げ確定 """
        logger.debug('Sej Payment')
        order = c_models.Order.create_from_cart(cart)
        cart.finish()

        shipping_address = order.shipping_address
        performance = order.performance
        current_date = datetime.now()

        payment_due_at = get_payment_due_at(current_date,order)
        ticketing_start_at = get_ticketing_start_at(current_date,order)
        ticketing_due_at = order.payment_delivery_pair.issuing_end_at
        tel1 = shipping_address.tel_1.replace('-', '')
        tel2 = shipping_address.tel_2.replace('-', '')

        settings = get_current_registry().settings
        tenant = SejTenant.find_by(organization_id = performance.event.organization.id)
        api_key = tenant.api_key or settings['sej.api_key']
        api_url = tenant.inticket_api_url or settings['sej.inticket_api_url']

        sej_order = get_sej_order(order)
        if not sej_order:
            request_order(
                shop_name           = tenant.shop_name,
                shop_id             = tenant.shop_id,
                contact_01          = tenant.contact_01,
                contact_02          = tenant.contact_02,
                order_id            = order.order_no,
                username            = u'%s%s' % (shipping_address.last_name, shipping_address.first_name),
                username_kana       = u'%s%s' % (shipping_address.last_name_kana, shipping_address.first_name_kana),
                tel                 = tel1 if tel1 else tel2,
                zip                 = shipping_address.zip.replace('-', ''),
                email               = shipping_address.email,
                total               = order.total_amount,
                ticket_total        = cart.tickets_amount,
                commission_fee      = order.system_fee + order.transaction_fee,
                payment_type        = SejPaymentType.PrepaymentOnly,
                ticketing_fee       = order.delivery_fee,
                payment_due_at      = payment_due_at,
                ticketing_start_at  = ticketing_start_at,
                ticketing_due_at    = ticketing_due_at,
                regrant_number_due_at = performance.start_on + timedelta(days=1) if performance.start_on else
                current_date + timedelta(days=365),
                secret_key = api_key,
                hostname = api_url
            )

        return order


@implementer(IDeliveryPlugin)
class SejDeliveryPlugin(object):
    def prepare(self, request, cart):
        """  """

    def finish(self, request, cart):
        logger.debug('Sej Delivery')

        order_no = str(cart.id)
        shipping_address = cart.shipping_address
        performance = cart.performance
        current_date = datetime.now()

        payment_due_at = get_payment_due_at(current_date,cart)
        ticketing_start_at = get_ticketing_start_at(current_date,cart)
        ticketing_due_at = cart.payment_delivery_pair.issuing_end_at
        tickets = get_tickets_from_cart(cart)
        order_no = cart.order_no
        tel1 = shipping_address.tel_1.replace('-', '')
        tel2 = shipping_address.tel_2.replace('-', '')

        settings = get_current_registry().settings
        tenant = SejTenant.find_by(organization_id = performance.event.organization.id)
        api_key = tenant.api_key or settings['sej.api_key']
        api_url = tenant.inticket_api_url or settings['sej.inticket_api_url']

        sej_order = get_sej_order(order)
        if not sej_order:
            request_order(
                shop_name           = tenant.shop_name,
                shop_id             = tenant.shop_id,
                contact_01          = tenant.contact_01,
                contact_02          = tenant.contact_02,
                order_id            = order_no,
                username            = u'%s%s' % (shipping_address.last_name, shipping_address.first_name),
                username_kana       = u'%s%s' % (shipping_address.last_name_kana, shipping_address.first_name_kana),
                tel                 = tel1 if tel1 else tel2,
                zip                 = shipping_address.zip.replace('-', ''),
                email               = shipping_address.email,
                total               = 0,
                ticket_total        = 0,
                commission_fee      = 0,
                payment_type        = SejPaymentType.Paid,
                ticketing_fee       = 0,
                payment_due_at      = payment_due_at,
                ticketing_start_at  = ticketing_start_at,
                ticketing_due_at    = ticketing_due_at,
                regrant_number_due_at = performance.start_on + timedelta(days=1),
                tickets=tickets,
                secret_key = api_key,
                hostname = api_url
            )

@implementer(IDeliveryPlugin)
class SejPaymentDeliveryPlugin(object):
    def prepare(self, request, cart):
        """  """

    def finish(self, request, cart):
        """  """
        logger.debug('Sej Payment and Delivery')
        order = c_models.Order.create_from_cart(cart)
        cart.finish()

        performance = cart.performance

        settings = get_current_registry().settings
        tenant = SejTenant.find_by(organization_id = performance.event.organization.id)
        api_key = tenant.api_key or settings['sej.api_key']
        api_url = tenant.inticket_api_url or settings['sej.inticket_api_url']

        sej_order = get_sej_order(order)
        if not sej_order:
            shipping_address = cart.shipping_address
            performance = cart.performance
            current_date = datetime.now()
            payment_due_at = get_payment_due_at(current_date,order)
            ticketing_start_at = get_ticketing_start_at(current_date,order)
            ticketing_due_at = cart.payment_delivery_pair.issuing_end_at
            tel1 = shipping_address.tel_1.replace('-', '')
            tel2 = shipping_address.tel_2.replace('-', '')
            tickets = get_tickets(order)
            request_order(
                shop_name           = tenant.shop_name,
                shop_id             = tenant.shop_id,
                contact_01          = tenant.contact_01,
                contact_02          = tenant.contact_02,
                order_id            = order.order_no,
                username            = u'%s%s' % (shipping_address.last_name, shipping_address.first_name),
                username_kana       = u'%s%s' % (shipping_address.last_name_kana, shipping_address.first_name_kana),
                tel                 = tel1 if tel1 else tel2,
                zip                 = shipping_address.zip.replace('-', ''),
                email               = shipping_address.email,
                total               = order.total_amount,
                ticket_total        = cart.tickets_amount,
                commission_fee      = order.system_fee + order.transaction_fee,
                payment_type        = SejPaymentType.Prepayment if SejPaymentType.CashOnDelivery else SejPaymentType.Prepayment ,
                ticketing_fee       = order.delivery_fee,
                payment_due_at      = payment_due_at,
                ticketing_start_at  = ticketing_start_at,
                ticketing_due_at    = ticketing_due_at,
                regrant_number_due_at = performance.start_on + timedelta(days=1),
                tickets=tickets,
                secret_key = api_key,
                hostname = api_url
            )

        return order


@view_config(context=IOrderDelivery, name="delivery-%d" % DELIVERY_PLUGIN_ID, renderer='ticketing.cart.plugins:templates/carts/sej_delivery_complete.html')
def sej_delivery_viewlet(context, request):
    order = context.order
    sej_order = get_sej_order(order)
    return dict(
        order=order,
        sej_order=sej_order
    )

@view_config(context=ICartDelivery, name="delivery-%d" % DELIVERY_PLUGIN_ID, renderer='ticketing.cart.plugins:templates/carts/sej_delivery_confirm.html')
def sej_delivery_confirm_viewlet(context, request):
    return Response(text=u'セブンイレブン受け取り')

@view_config(context=IOrderPayment, name="payment-%d" % PAYMENT_PLUGIN_ID, renderer='ticketing.cart.plugins:templates/sej_payment_complete.html')
def sej_payment_viewlet(context, request):
    order = context.order
    sej_order = get_sej_order(order)
    return dict(
        order=order,
        sej_order=sej_order
    )

@view_config(context=ICartPayment, name="payment-%d" % PAYMENT_PLUGIN_ID, renderer='ticketing.cart.plugins:templates/carts/sej_payment_confirm.html')
def sej_payment_confirm_viewlet(context, request):
    return Response(text=u'セブンイレブン支払い')
