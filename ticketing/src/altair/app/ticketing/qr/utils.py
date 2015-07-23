# -*- encoding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)
import sqlahelper
from sqlalchemy.orm.session import object_session
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
from altair.app.ticketing.orders.api import get_order_by_order_no

DBSession = sqlahelper.get_session()


class QRTicketObject(object):
    def __init__(self, history):
        self.history = history
        self.qr = None
        self.sign = None

    @property
    def id(self):
        return self.history.id

    @property
    def item_token(self):
        return self.history.item_token

    @property
    def ordered_product_item(self):
        return self.item_token and self.item_token.item

    @property
    def order(self):
        if self.history.order_id is not None:
            return object_session(self.history).query(Order).filter_by(id=self.history.order_id).one()
        elif self.history.item_token_id is not None:
            return object_session(self.history).query(Order) \
                    .join(Order.items) \
                    .join(OrderedProduct.elements) \
                    .join(OrderedProductItem.tokens) \
                    .filter(OrderedProductItemToken.id == self.history.item_token_id) \
                    .one()

    @property
    def order_no(self):
        return self.order.order_no

    @property
    def performance(self):
        return self.order.performance

    @property
    def event(self):
        return self.order.sales_segment.sales_segment_group.event

    @property
    def seat(self):
        return self.history.seat

    @property
    def ticket(self):
        return self.history.ticket

    @property
    def operator(self):
        return self.history.operator

    @property
    def product(self):
        return self.ordered_product_item and self.ordered_product_item.ordered_product.product


def build_qr_by_order_no(request, order_no, none_exception=HTTPNotFound):
    order = get_order_by_order_no(request, order_no)
    if order is None:
        raise none_exception
    return build_qr_by_order(request, order)

def build_qr_by_token_id(request, order_no, token_id, none_exception=HTTPNotFound):
    token = get_matched_token_from_token_id(order_no, token_id, none_exception=none_exception)
    return build_qr_by_token(request, order_no, token)

def build_qr_by_order(request, order):
    history = get_or_create_matched_history_from_order(order)
    return build_qr_by_history(request, history)
     
def build_qr_by_token(request, order_no, token):
    history = get_or_create_matched_history_from_token(order_no, token)
    return build_qr_by_history(request, history)

def build_qr_by_history_id(request, ticket_id):
    try:
        history = TicketPrintHistory\
            .filter_by(id = ticket_id)\
            .one()
        return build_qr_by_history(request, history)
    except NoResultFound:
        return None

def build_qr_by_history(request, history):
    params, ticket = make_data_for_qr(history)
    builder = get_qrdata_builder(request)
    ticket.qr = builder.sign(builder.make(params))
    ticket.sign = ticket.qr[0:8]
    return ticket

def build_qr_by_orion(request, history, serial):
    params, ticket = make_data_for_orion(history, serial)
    builder = get_qrdata_builder(request)
    ticket.qr = builder.sign(builder.make(params))
    ticket.sign = ticket.qr[0:8]
    return ticket

def get_matched_token_query_from_order(order):
    return OrderedProductItemToken.query\
        .filter(OrderedProductItemToken.ordered_product_item_id==OrderedProductItem.id)\
        .filter(OrderedProductItem.ordered_product_id == OrderedProduct.id)\
        .filter(OrderedProduct.order_id == order.id)

def get_matched_token_query_from_order_no(order_no):
    return OrderedProductItemToken.query \
        .join(OrderedProductItemToken.item) \
        .join(OrderedProductItem.ordered_product) \
        .join(OrderedProduct.order) \
        .filter(Order.order_no == order_no)

def get_matched_token_from_token_id(order_no, token_id, none_exception=HTTPNotFound):
    token = get_matched_token_query_from_order_no(order_no)\
        .filter(OrderedProductItemToken.id==token_id).first()
    if token is None:
        raise none_exception()
    return token

def get_matched_history_from_token(order_no, token):
    try:
        return TicketPrintHistory.filter(TicketPrintHistory.item_token_id==token.id).first()
    except NoResultFound:
        return None
    
def get_matched_history_from_order(order):
    try:
        return TicketPrintHistory \
            .filter(TicketPrintHistory.seat_id == None) \
            .filter(TicketPrintHistory.item_token_id == None) \
            .filter(TicketPrintHistory.ordered_product_item_id == None) \
            .filter(TicketPrintHistory.order_id == order.id) \
            .one()
    except NoResultFound:
        return None
    
def get_or_create_matched_history_from_token(order_no, token):
    history = get_matched_history_from_token(order_no, token)
    # ここでinsertする
    if history is None:
        logger.info("ticket print histry is not found. create it (orderno=%s,  token=%s)" % (order_no, token.id))
        history = TicketPrintHistory(
            seat_id=token.seat_id,
            item_token_id=token.id, 
            ordered_product_item_id=token.ordered_product_item_id,
            order_id=token.item.ordered_product.order.id
            )
        DBSession.add(history)
        DBSession.flush()
    return history

def get_or_create_matched_history_from_order(order):
    history = get_matched_history_from_order(order)
    # ここでinsertする
    if history is None:
        logger.info("ticket print histry is not found. create it (order_no=%s)" % (order.order_no))
        history = TicketPrintHistory(
            seat_id=None,
            item_token_id=None,
            ordered_product_item_id=None,
            order_id=order.id
            )
        DBSession.add(history)
        DBSession.flush()
    return history

def make_data_for_qr(history):
    qr_ticket_obj = QRTicketObject(history)
    params = dict(serial=str(qr_ticket_obj.id),
                  performance=qr_ticket_obj.performance and qr_ticket_obj.performance.code,
                  order=qr_ticket_obj.order_no,
                  date=qr_ticket_obj.performance and qr_ticket_obj.performance.start_on.strftime("%Y%m%d")
                  )
    if qr_ticket_obj.product:
        params["type"] = qr_ticket_obj.product.id
    if qr_ticket_obj.seat:
        params["seat"] = qr_ticket_obj.seat.l0_id
        params["seat_name"] = qr_ticket_obj.seat.name
    else:
        params["seat"] = ""
        params["seat_name"] = "" #TicketPrintHistoryはtokenが違えば違うのでuniqueなはず
    return params, qr_ticket_obj

def make_data_for_orion(history, serial):
    qr_ticket_obj = QRTicketObject(history)
    params = dict(serial=serial,
                  performance=qr_ticket_obj.performance and qr_ticket_obj.performance.code,
                  order=qr_ticket_obj.order.order_no,
                  date=qr_ticket_obj.performance and qr_ticket_obj.performance.start_on.strftime("%Y%m%d")
                  )
    if qr_ticket_obj.product:
        params["type"] = qr_ticket_obj.product.id
    if qr_ticket_obj.seat:
        params["seat"] = qr_ticket_obj.seat.l0_id
        params["seat_name"] = qr_ticket_obj.seat.name
    else:
        params["seat"] = ""
        params["seat_name"] = ""
    return params, qr_ticket_obj
