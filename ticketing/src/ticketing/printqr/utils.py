# -*- coding:utf-8 -*-

from ticketing.models import DBSession
from ticketing.core.models import Order, TicketPrintHistory, OrderedProductItem, OrderedProduct
import hashlib
import logging
from . import helpers as h
logger = logging.getLogger(__name__)

def _order_and_history_from_qrdata(qrdata):
    return DBSession.query(Order, TicketPrintHistory)\
        .filter(TicketPrintHistory.id==qrdata["serial"])\
        .filter(TicketPrintHistory.ordered_product_item_id==OrderedProductItem.id)\
        .filter(OrderedProductItem.ordered_product_id == OrderedProduct.id)\
        .filter(OrderedProduct.order_id == Order.id)\
        .filter(Order.order_no == qrdata["order"]).first()

def ticketdata_from_qrdata(qrdata):
    order, history = _order_and_history_from_qrdata(qrdata)
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
        "token_id": history.item_token_id, 
        "order_id": order.id, 
        "orderno": order.order_no, 
        "performance_name": performance_name, 
        "performance_date": h.japanese_datetime(performance.start_on), 
        "product_name": product_name, 
        "seat_name": seat.name if seat else u""
        }

#todo: 券面ステータス
