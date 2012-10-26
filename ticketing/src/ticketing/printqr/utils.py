# -*- coding:utf-8 -*-

import sqlalchemy as sa
import sqlalchemy.orm as orm

from ticketing.models import DBSession
from ticketing.core.models import Order
from ticketing.core.models import TicketPrintHistory
from ticketing.core.models import OrderedProductItemToken
from ticketing.core.models import OrderedProductItem
from ticketing.core.models import OrderedProduct
from ticketing.core.models import PageFormat


from ticketing.cart.plugins.qr import DELIVERY_PLUGIN_ID as QR_DELIVERY_ID
from ticketing.core import models as c_models

from ticketing.tickets.utils import build_dict_from_ordered_product_item_token
from ticketing.utils import json_safe_coerce

import logging
from . import helpers as h
logger = logging.getLogger(__name__)

class UnmatchEventException(Exception):
    pass

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
    return DBSession.query(Order, TicketPrintHistory)\
        .filter(TicketPrintHistory.id==qrdata["serial"])\
        .filter(TicketPrintHistory.ordered_product_item_id==OrderedProductItem.id)\
        .filter(OrderedProductItem.ordered_product_id == OrderedProduct.id)\
        .filter(OrderedProduct.order_id == Order.id)\
        .filter(Order.order_no == qrdata["order"])\
        .options(orm.joinedload(Order.performance), 
                 orm.joinedload(Order.shipping_address), 
                 orm.joinedload(TicketPrintHistory.ordered_product_item), 
                 orm.joinedload(TicketPrintHistory.item_token), 
                 orm.joinedload(TicketPrintHistory.seat))\
        .first()

def ticketdata_from_qrdata(qrdata, event_id="*"):
    order, history = _order_and_history_from_qrdata(qrdata)
    performance = order.performance
    shipping_address = order.shipping_address
    product_name = history.ordered_product_item.ordered_product.product.name
    token = history.item_token
    seat = history.seat
    performance_name = u"%s (%s)" % (performance.name, performance.venue.name)
    note = order.note

    if event_id != "*" and str(performance.event_id) != str(event_id):
        fmt = "ticketdata_from_qrdata: unmatched event id (order.id=%s, expected event_id=%s, event_id=%s)"
        logger.warn(fmt % (order.id, event_id, performance.event_id))
        raise UnmatchEventException

    ##history.idがあればQRコードを再生成できるそう。それに気づいてもデータがなければ見れなそうなのでhash化しなくて良い
    #codeno = hashlib.sha1(str(history.id)).hexdigest()
    codeno = history.id
    return {
        "user": shipping_address.full_name_kana if shipping_address else u"", 
        "codeno": codeno, 
        "ordered_product_item_token_id": token.id, 
        "ordered_product_item_id": history.ordered_product_item.id, 
        "printed": str(token.printed_at) if token.printed_at else None, ##todo:データ整理
        "canceled": str(order.canceled_at) if order.is_canceled() else None, ##todo:データ整理
        "orderno": order.order_no, 
        "order_id": order.id, 
        "performance_name": performance_name, 
        "performance_date": h.japanese_datetime(performance.start_on), 
        "event_id": performance.event_id, 
        "product_name": product_name, 
        "seat_id": seat.id if seat else None,
        "seat_name": seat.name if seat else u"自由席",
        "note": note,
        }

def svg_data_from_token(ordered_product_item_token):
    pair = build_dict_from_ordered_product_item_token(ordered_product_item_token)
    retval = [] 
    if pair is not None:
        retval.append({
                u'ordered_product_item_token_id': ordered_product_item_token.id,
                u'ordered_product_item_id': ordered_product_item_token.item.id,
                u'order_id': ordered_product_item_token.item.ordered_product.order.id,
                u'seat_id': ordered_product_item_token.seat_id or "",
                u'serial': ordered_product_item_token.serial,
                u'data': json_safe_coerce(pair[1])
                })
    return retval

def svg_data_from_token_with_descinfo(ordered_product_item_token):
    pair = build_dict_from_ordered_product_item_token(ordered_product_item_token)
    retval = [] 
    if pair is not None:
        seat = ordered_product_item_token.seat
        item = ordered_product_item_token.item
        ticket_name = "%s(%s)" % (item.ordered_product.product.name, seat.name if seat else u"自由席")
        retval.append({
                u'ordered_product_item_token_id': ordered_product_item_token.id,
                u'ordered_product_item_id': ordered_product_item_token.item.id,
                u'order_id': ordered_product_item_token.item.ordered_product.order.id,
                u'seat_id': ordered_product_item_token.seat_id or "",
                u'serial': ordered_product_item_token.serial,
                u"ticket_name": ticket_name, 
                u'data': json_safe_coerce(pair[1]), 
                u"printed_at": str(ordered_product_item_token.printed_at) if ordered_product_item_token.printed_at else None
                })
    return retval

def history_from_token(request, operator_id, order_id, token):
    return TicketPrintHistory(
        operator_id=operator_id, 
        seat_id=token.seat_id, 
        item_token_id=token.id,
        ordered_product_item_id=token.item.id,
        order_id=order_id,
        )

def add_history(request, operator_id, params):
    seat_id = params.get(u'seat_id')
    ordered_product_item_token_id = params.get(u'ordered_product_item_token_id')
    ordered_product_item_id = params.get(u'ordered_product_item_id')
    order_id = params.get(u'order_id')
    ticket_id = params[u'ticket_id']
    return TicketPrintHistory(
        operator_id=operator_id, 
        seat_id=seat_id,
        item_token_id=ordered_product_item_token_id,
        ordered_product_item_id=ordered_product_item_id,
        order_id=order_id,
        ticket_id=ticket_id
        )

## progress
def performance_data_from_performance_id(event_id, performance_id):
    performance = c_models.Performance.query.join(c_models.Event)\
        .filter(c_models.Event.id==event_id, c_models.Performance.id==performance_id)\
        .first()
    return {"name": performance.name, 
            "start_on": h.japanese_datetime(performance.start_on), 
            "pk": performance.id}

def _as_total_quantity(opi_query):
    return int(opi_query.with_entities(sa.func.sum(OrderedProductItem.quantity)).first()[0] or 0)

def _query_filtered_by_performance(query, event_id, performance_id):
    return query.join(c_models.OrderedProduct)\
        .join(c_models.Product)\
        .join(c_models.Order)\
        .filter(c_models.Order.performance_id==performance_id)\
        .filter(c_models.Product.event_id==event_id)\
        .filter(c_models.Order.canceled_at==None)\
        .filter(c_models.Order.deleted_at==None)

def _query_filtered_by_delivery_plugin(query, delivery_plugin_id):
    return query.join(c_models.PaymentDeliveryMethodPair)\
        .join(c_models.DeliveryMethod)\
        .filter(c_models.DeliveryMethod.delivery_plugin_id==delivery_plugin_id)

def _query_removed_by_delivery_plugin(query, delivery_plugin_id):
    return query.join(c_models.PaymentDeliveryMethodPair)\
        .join(c_models.DeliveryMethod)\
        .filter(c_models.DeliveryMethod.delivery_plugin_id!=delivery_plugin_id)

## 余事象取れば計算で求められるけれど。実際にDBアクセスした方が良いのかな。
def total_result_data_from_performance_id(event_id, performance_id):
    opi_query = _query_filtered_by_performance(OrderedProductItem.query, event_id, performance_id)

    total = _as_total_quantity(opi_query)
    total_qr = _as_total_quantity(_query_filtered_by_delivery_plugin(opi_query, QR_DELIVERY_ID))

    token_query = _query_filtered_by_performance(OrderedProductItemToken.query.join(OrderedProductItem), event_id, performance_id)
    total_tokens = token_query.count()
    total_qr_printed = token_query.filter(OrderedProductItemToken.printed_at != None).count()

    total_other_printed = _as_total_quantity(_query_removed_by_delivery_plugin(opi_query, QR_DELIVERY_ID).filter(OrderedProductItem.printed_at != None))

    return {
        "total": total, 

        "total_qr": total_qr, 
        "total_other": total - total_qr, 

        "qr_printed": total_qr_printed, 
        "qr_unprinted": total_tokens - total_qr_printed, 

        "other_printed": total_other_printed, 
        "other_unprinted": total - total_qr - total_other_printed, 
        }
    

