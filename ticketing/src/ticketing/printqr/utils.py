# -*- coding:utf-8 -*-

from ticketing.models import DBSession
from ticketing.core.models import Order
from ticketing.core.models import TicketPrintHistory
from ticketing.core.models import OrderedProductItem
from ticketing.core.models import OrderedProduct
from ticketing.core.models import OrderedProductItemToken
from ticketing.core.models import PageFormat
import hashlib
import logging
from . import helpers as h
logger = logging.getLogger(__name__)

def ticket_format_to_dict(ticket_format):
    data = dict(ticket_format.data)
    data[u'id'] = ticket_format.id
    data[u'name'] = ticket_format.name
    return data

def ticket_to_dict(ticket):
    data = dict(ticket.data)
    data[u'id'] = ticket.id
    data[u'name'] = ticket.name
    data[u'ticket_format_id'] = ticket.ticket_format_id
    return data

def page_format_to_dict(page_format):
    data = dict(page_format.data)
    data[u'id'] = page_format.id
    data[u'name'] = page_format.name
    data[u'printer_name'] = page_format.printer_name
    return data

def page_formats_for_organization(organization):
    return [
        page_format_to_dict(page_format) \
        for page_format in DBSession.query(PageFormat).filter_by(organization=organization)
        ]

def _order_and_history_from_qrdata(qrdata):
    return DBSession.query(Order, TicketPrintHistory, OrderedProductItemToken)\
        .filter(TicketPrintHistory.id==qrdata["serial"])\
        .filter(TicketPrintHistory.ordered_product_item_id==OrderedProductItem.id)\
        .filter(OrderedProductItem.ordered_product_id == OrderedProduct.id)\
        .filter(OrderedProduct.order_id == Order.id)\
        .filter(Order.order_no == qrdata["order"]).first()

def ticketdata_from_qrdata(qrdata):
    order, history, token = _order_and_history_from_qrdata(qrdata)
    performance = order.performance
    shipping_address = order.shipping_address
    product_name = history.ordered_product_item.ordered_product.product.name
    seat = history.seat
    #performance_name = u"%s %s (%s)" % (performance.event.title, performance.name, performance.venue.name)
    performance_name = u"%s (%s)" % (performance.name, performance.venue.name)    
    codeno = hashlib.sha1(str(history.id)).hexdigest()
    return {
        "user": shipping_address.full_name_kana, 
        "codeno": codeno, 
        "ordered_product_item_token_id": token.id, 
        "printed": str(token.printed_at), 
        "orderno": order.order_no, 
        "performance_name": performance_name, 
        "performance_date": h.japanese_datetime(performance.start_on), 
        "product_name": product_name, 
        "seat_name": seat.name if seat else u""
        }

#todo: 券面ステータス
