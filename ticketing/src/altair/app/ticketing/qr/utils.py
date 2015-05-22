# -*- encoding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)
import sqlahelper
from sqlalchemy.orm.exc import NoResultFound
from altair.app.ticketing.core.models import TicketPrintHistory
from altair.app.ticketing.orders.models import (
    Order,
    OrderedProduct,
    OrderedProductItem,
    OrderedProductItemToken,
    )
from pyramid.httpexceptions import HTTPNotFound

from altair.app.ticketing.qr import get_qrdata_builder
DBSession = sqlahelper.get_session()

def build_qr_by_token_id(request, order_no, token_id, none_exception=HTTPNotFound):
    token = get_matched_token_from_token_id(order_no, token_id, none_exception=none_exception)
    return build_qr_by_token(request, order_no, token)

def build_qr_by_token(request, order_no, token):
    history = get_or_create_matched_history_from_token(order_no, token)
    return build_qr_by_history(request, history)

def build_qr_by_history_id(request, ticket_id):
    try:
        ticket = TicketPrintHistory\
            .filter_by(id = ticket_id)\
            .one()
        return build_qr_by_history(request, ticket)
    except NoResultFound, e:
        return None

def build_qr_by_history(request, ticket):
    params = make_data_for_qr(ticket)
    builder = get_qrdata_builder(request)
    ticket.qr = builder.sign(builder.make(params))
    ticket.sign = ticket.qr[0:8]
    return ticket

def build_qr_by_orion(request, ticket, serial):
    params = make_data_for_orion(ticket, serial)
    builder = get_qrdata_builder(request)
    ticket.qr = builder.sign(builder.make(params))
    ticket.sign = ticket.qr[0:8]
    return ticket

def get_matched_token_query_from_order_no(order_no):
    return OrderedProductItemToken.query\
        .filter(OrderedProductItemToken.ordered_product_item_id==OrderedProductItem.id)\
        .filter(OrderedProductItem.ordered_product_id == OrderedProduct.id)\
        .filter(OrderedProduct.order_id == Order.id)\
        .filter(Order.order_no == order_no)

def get_matched_token_from_token_id(order_no, token_id, none_exception=HTTPNotFound):
    token = get_matched_token_query_from_order_no(order_no)\
        .filter(OrderedProductItemToken.id==token_id).first()
    if token is None:
        raise none_exception()
    return token

def get_matched_history_from_token(order_no, token):
    # tokenがあればorder_noを使わずとも検索できる
    return TicketPrintHistory.filter(TicketPrintHistory.item_token_id==token.id).first()
        # .filter(TicketPrintHistory.ordered_product_item_id==OrderedProductItem.id)\
        # .filter(OrderedProductItem.ordered_product_id == OrderedProduct.id)\
        # .filter(OrderedProduct.order_id == Order.id)\
        # .filter(Order.order_no == order_no).first()

def get_or_create_matched_history_from_token(order_no, token):
    history = get_matched_history_from_token(order_no, token)
    # ここでinsertする
    if history is None:
        logger.info("ticket print histry is not found. create it (orderno=%s,  token=%s)" % (order_no, token.id))
        history = TicketPrintHistory(
            seat_id=token.seat_id,
            item_token_id=token.id,
            ordered_product_item_id=token.ordered_product_item_id)
        DBSession.add(history)
        DBSession.flush()
    return history

def make_data_for_qr(ticket):
    ticket.seat = ticket.seat
    ticket.performance = ticket.ordered_product_item.product_item.performance
    ticket.event = ticket.performance.event
    ticket.product = ticket.ordered_product_item.ordered_product.product
    ticket.order = ticket.ordered_product_item.ordered_product.order
    ticket.item_token = ticket.item_token
    logger.info('aaaaaaaaaaaa  %s bbbbbbbbbbbbbbbbbbbb' % (ticket.order.payment_delivery_pair.delivery_method.delivery_plugin_id))

    params = dict(serial=str(ticket.id),
                  performance=ticket.performance.code,
                  order=ticket.order.order_no,
                  date=ticket.performance.start_on.strftime("%Y%m%d"),
                  delivery_plugin_id=str(ticket.order.payment_delivery_pair.delivery_method.delivery_plugin_id),
                  type=ticket.product.id)
    if ticket.seat:
        params["seat"] = ticket.seat.l0_id
        params["seat_name"] = ticket.seat.name
    else:
        params["seat"] = ""
        params["seat_name"] = "" #TicketPrintHistoryはtokenが違えば違うのでuniqueなはず
    return params

def make_data_for_orion(ticket, serial):
    params = dict(serial=serial,
                  performance=ticket.performance.code,
                  order=ticket.order.order_no,
                  date=ticket.performance.start_on.strftime("%Y%m%d"),
                  delivery_plugin_id=str(ticket.order.payment_delivery_pair.delivery_method.delivery_plugin_id),
                  type=ticket.ordered_product_item.ordered_product.product.id)
    if ticket.seat:
        params["seat"] = ticket.seat.l0_id
        params["seat_name"] = ticket.seat.name
    else:
        params["seat"] = ""
        params["seat_name"] = ""
    return params
