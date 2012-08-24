# -*- coding:utf-8 -*-
from zope.interface import implementer
from pyramid.view import view_config
from pyramid.response import Response

from ..interfaces import IPaymentPlugin, ICartPayment, IOrderPayment, ICompleteMailPayment, ICompleteMailDelivery
from ..interfaces import IDeliveryPlugin, ICartDelivery, IOrderDelivery

from .. import logger

from pyramid.threadlocal import get_current_registry

from ticketing.core import models as c_models

from ticketing.sej.ticket import SejTicketDataXml
from ticketing.sej.models import SejOrder, SejTenant
from ticketing.sej.payment import request_order
from ticketing.sej.resources import SejPaymentType, SejTicketType
from ticketing.sej.utils import han2zen

from ticketing.tickets.convert import convert_svg, as_user_unit
from ticketing.tickets.utils import *

from lxml import html, etree
from lxml.builder import E
from datetime import datetime, timedelta
import numpy
import pystache
from ticketing.cart import helpers as cart_helper
import re

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
        payment_due_at.replace(hour=23, minute=59, second=59)
    return payment_due_at

def get_ticketing_start_at(current_date, cart):
    if cart.payment_delivery_pair.issuing_start_at:
        ticketing_start_at = cart.payment_delivery_pair.issuing_start_at
    else:
        ticketing_start_at = current_date + timedelta(days=cart.payment_delivery_pair.issuing_interval_days)
        ticketing_start_at.replace(hour=00, minute=00, second=00)
    return ticketing_start_at

def get_sej_order(order):
    return SejOrder.filter(SejOrder.order_id == order.order_no).first()

def get_ticket(order_no, product_item, svg):
    performance = product_item.performance
    return dict(
        ticket_type         = SejTicketType.TicketWithBarcode,
        event_name          = re.sub('[ \-\.,;\'\"]', '', han2zen(performance.event.title)[:20]),
        performance_name    = re.sub('[ \-\.,;\'\"]', '', han2zen(performance.name)[:20]),
        ticket_template_id  = u'TTTS000001',
        performance_datetime= performance.start_on,
        xml = SejTicketDataXml(svg)
    )

def translate(x, y):
    return numpy.matrix(
        [
            [1., 0., float(x)],
            [0., 1., float(y)],
            [0., 0., 1.]
            ],
        dtype=numpy.float64)

def get_tickets(order):
    tickets = []
    for ordered_product in order.items:
        for ordered_product_item in ordered_product.ordered_product_items:
            bundle = ordered_product_item.product_item.ticket_bundle
            dicts = build_dicts_from_ordered_product_item(ordered_product_item)
            for dict_ in dicts:
                for ticket in bundle.tickets:
                    ticket_format = ticket.ticket_format
                    applicable = False
                    for delivery_method in ticket_format.delivery_methods:
                        if delivery_method.delivery_plugin_id == DELIVERY_PLUGIN_ID:
                            applicable = True
                            break
                    if not applicable:
                        continue
                    transform = translate(-as_user_unit(ticket_format.data['print_offset']['x']), -as_user_unit(ticket_format.data['print_offset']['y']))
                    svg = etree.tostring(convert_svg(etree.ElementTree(etree.fromstring(pystache.render(ticket.data['drawing'], dict_))), transform), encoding=unicode)
                    ticket = get_ticket(order.order_no, ordered_product_item.product_item, svg)
                    tickets.append(ticket)
    return tickets

def get_tickets_from_cart(cart):
    tickets = []
    for carted_product in cart.products:
        for carted_product_item in carted_product.items:
            bundle = carted_product_item.product_item.ticket_bundle
            for seat in carted_product_item.seats:
                dict_ = build_dict_from_seat(seat, None)
                for ticket in bundle.tickets:
                    ticket_format = ticket.ticket_format
                    applicable = False
                    for delivery_method in ticket_format.delivery_methods:
                        if delivery_method.delivery_plugin_id == DELIVERY_PLUGIN_ID:
                            applicable = True
                            break
                    if not applicable:
                        continue
                    transform = translate(-as_user_unit(ticket_format.data['print_offset']['x']), -as_user_unit(ticket_format.data['print_offset']['y']))
                    svg = etree.tostring(convert_svg(etree.ElementTree(etree.fromstring(pystache.render(ticket.data['drawing'], dict_))), transform), encoding=unicode)
                    ticket = get_ticket(cart.order_no, carted_product_item.product_item, svg)
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
        tel1 = shipping_address.tel_1 and shipping_address.tel_1.replace('-', '')
        tel2 = shipping_address.tel_2 and shipping_address.tel_2.replace('-', '')

        settings = get_current_registry().settings
        tenant = SejTenant.filter_by(organization_id = performance.event.organization.id).first()
        api_key = (tenant and tenant.api_key) or settings['sej.api_key']
        api_url = (tenant and tenant.inticket_api_url) or settings['sej.inticket_api_url']

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

        shipping_address = cart.shipping_address
        performance = cart.performance
        current_date = datetime.now()

        payment_due_at = get_payment_due_at(current_date,cart)
        ticketing_start_at = get_ticketing_start_at(current_date,cart)
        ticketing_due_at = cart.payment_delivery_pair.issuing_end_at
        tickets = get_tickets_from_cart(cart)
        order_no = cart.order_no
        tel1 = shipping_address.tel_1 and shipping_address.tel_1.replace('-', '')
        tel2 = shipping_address.tel_2 and shipping_address.tel_2.replace('-', '')

        settings = get_current_registry().settings
        tenant = SejTenant.filter_by(organization_id = performance.event.organization.id).first()
        api_key = (tenant and tenant.api_key) or settings['sej.api_key']
        api_url = (tenant and tenant.inticket_api_url) or settings['sej.inticket_api_url']

        sej_order = SejOrder.filter(SejOrder.order_id == cart.order_no).first()
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
        tenant = SejTenant.filter_by(organization_id = performance.event.organization.id).first()
        api_key = (tenant and tenant.api_key) or settings['sej.api_key']
        api_url = (tenant and tenant.inticket_api_url) or settings['sej.inticket_api_url']

        sej_order = get_sej_order(order)
        if not sej_order:
            shipping_address = cart.shipping_address
            performance = cart.performance
            current_date = datetime.now()
            payment_due_at = get_payment_due_at(current_date,order)
            ticketing_start_at = get_ticketing_start_at(current_date,order)
            ticketing_due_at = cart.payment_delivery_pair.issuing_end_at
            tel1 = shipping_address.tel_1 and shipping_address.tel_1.replace('-', '')
            tel2 = shipping_address.tel_2 and shipping_address.tel_2.replace('-', '')
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
                payment_type        = SejPaymentType.CashOnDelivery,
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


@view_config(context=IOrderDelivery, name="delivery-%d" % DELIVERY_PLUGIN_ID, renderer='ticketing.cart.plugins:templates/sej_delivery_complete.html')
@view_config(context=IOrderDelivery, request_type='ticketing.cart.interfaces.IMobileRequest',
             name="delivery-%d" % DELIVERY_PLUGIN_ID, renderer='ticketing.cart.plugins:templates/sej_delivery_complete_mobile.html')
def sej_delivery_viewlet(context, request):
    order = context.order
    sej_order = get_sej_order(order)
    payment_id = context.order.payment_delivery_pair.payment_method.payment_plugin_id
    is_payment_with_sej = int(payment_id or -1) == PAYMENT_PLUGIN_ID
    return dict(
        order=order,
        is_payment_with_sej=is_payment_with_sej, 
        sej_order=sej_order
    )

@view_config(context=ICartDelivery, name="delivery-%d" % DELIVERY_PLUGIN_ID, 
             renderer='ticketing.cart.plugins:templates/sej_delivery_confirm.html')
def sej_delivery_confirm_viewlet(context, request):
    return Response(text=u'セブンイレブン受け取り')

@view_config(context=IOrderPayment, name="payment-%d" % PAYMENT_PLUGIN_ID, 
             renderer='ticketing.cart.plugins:templates/sej_payment_complete.html')
@view_config(context=IOrderPayment, request_type='ticketing.cart.interfaces.IMobileRequest',
             name="payment-%d" % PAYMENT_PLUGIN_ID, renderer='ticketing.cart.plugins:templates/sej_payment_complete_mobile.html')
def sej_payment_viewlet(context, request):
    order = context.order
    sej_order = get_sej_order(order)
    return dict(
        order=order,
        sej_order=sej_order
    )

@view_config(context=ICartPayment, name="payment-%d" % PAYMENT_PLUGIN_ID, renderer='ticketing.cart.plugins:templates/sej_payment_confirm.html')
def sej_payment_confirm_viewlet(context, request):
    return Response(text=u'セブンイレブン支払い')


@view_config(context=ICompleteMailPayment, name="payment-%d" % PAYMENT_PLUGIN_ID, renderer="ticketing.cart.plugins:templates/sej_payment_mail_complete.html")
def completion_payment_mail_viewlet(context, request):
    """ 完了メール表示
    :param context: ICompleteMailPayment
    """
    sej_order=get_sej_order(context.order)
    return dict(sej_order=sej_order, h=cart_helper)

@view_config(context=ICompleteMailDelivery, name="delivery-%d" % DELIVERY_PLUGIN_ID, renderer="ticketing.cart.plugins:templates/sej_delivery_mail_complete.html")
def completion_delivery_mail_viewlet(context, request):
    """ 完了メール表示
    :param context: ICompleteMailDelivery
    """
    sej_order=get_sej_order(context.order)
    payment_id = context.order.payment_delivery_pair.payment_method.payment_plugin_id
    is_payment_with_sej = int(payment_id or -1) == PAYMENT_PLUGIN_ID
    return dict(sej_order=sej_order, h=cart_helper, 
                is_payment_with_sej=is_payment_with_sej)
