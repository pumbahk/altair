# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)
from . import helpers as h
from altair.app.ticketing.utils import json_safe_coerce
from altair.app.ticketing.tickets.utils import build_dict_from_ordered_product_item_token


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

def data_dict_from_order_and_history(order, history):
    performance = order.performance
    shipping_address = order.shipping_address
    product_name = history.ordered_product_item.ordered_product.product.name
    token = history.item_token
    seat = history.seat
    performance_name = u"%s (%s)" % (performance.name, performance.venue.name)
    note = order.note

    ##history.idがあればQRコードを再生成できるそう。それに気づいてもデータがなければ見れなそうなのでhash化しなくて良い
    #codeno = hashlib.sha1(str(history.id)).hexdigest()
    codeno = history.id
    return {
        "user": shipping_address.full_name_kana if shipping_address else u"", 
        "codeno": codeno, 
        "ordered_product_item_token_id": token.id, 
        "ordered_product_item_id": history.ordered_product_item.id, 
        "refreshed_at": str(token.refreshed_at) if token.refreshed_at else None, 
        "printed_at": str(token.printed_at) if token.printed_at else None, 
        "printed": str(token.printed_at) if token.is_printed() else None, 
        "canceled": str(order.canceled_at) if order.is_canceled() else None, ##todo:データ整理
        "orderno": order.order_no,  #どこかでこちらが使われているので残しておく。(js?)
        "order_no": order.order_no, 
        "order_id": order.id, 
        "performance_name": performance_name, 
        "performance_date": h.japanese_datetime(performance.start_on), 
        "event_id": performance.event_id, 
        "product_name": product_name, 
        "seat_id": seat.id if seat else None,
        "seat_name": seat.name if seat else u"自由席",
        "note": note,
        }

def svg_data_from_token(ordered_product_item_token, issuer):
    data = build_dict_from_ordered_product_item_token(ordered_product_item_token, ticket_number_issuer=issuer)
    if data is None:
        logger.error("*svg_data_from_token_with_descinfo data=None (token_id=%s)" % ordered_product_item_token.id)
        return []

    seat = ordered_product_item_token.seat
    item = ordered_product_item_token.item
    ticket_name = "%s(%s)" % (item.ordered_product.product.name, seat.name if seat else u"自由席")
    return {
            u'ordered_product_item_token_id': ordered_product_item_token.id,
            u'ordered_product_item_id': ordered_product_item_token.item.id,
            u'order_id': ordered_product_item_token.item.ordered_product.order.id,
            u'seat_id': ordered_product_item_token.seat_id or "",
            u'serial': ordered_product_item_token.serial,
            u"ticket_name": ticket_name, 
            u'data': json_safe_coerce(data), 
            u"printed_at": str(ordered_product_item_token.printed_at) if ordered_product_item_token.printed_at else None, 
            u"refreshed_at": str(ordered_product_item_token.refreshed_at) if ordered_product_item_token.refreshed_at else None
            }

def svg_data_list_all_template_valiation(retval_data, ticket_templates):
    data_list = []
    for ticket_template in ticket_templates:
        data = retval_data.copy()
        data[u'ticket_template_name'] = ticket_template.name
        data[u'ticket_template_id'] = ticket_template.id
        data[u'ticket_name']= u"{}--{}".format(data[u"ticket_name"], ticket_template.name)
        data_list.append(data)
    return data_list
