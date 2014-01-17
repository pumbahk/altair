# -*- coding:utf-8 -*-

import sqlalchemy as sa
import sqlalchemy.orm as orm

from altair.app.ticketing.models import DBSession
from altair.app.ticketing.core.models import Order
from altair.app.ticketing.core.models import TicketPrintHistory
from altair.app.ticketing.core.models import OrderedProductItemToken
from altair.app.ticketing.core.models import OrderedProductItem
from altair.app.ticketing.core.models import OrderedProduct

from altair.app.ticketing.payments.plugins.qr import DELIVERY_PLUGIN_ID as QR_DELIVERY_ID
from altair.app.ticketing.core import models as c_models
from altair.app.ticketing.core.utils import ApplicableTicketsProducer


import logging
from . import helpers as h
logger = logging.getLogger(__name__)


from altair.app.ticketing.tickets.utils import NumberIssuer

_issuer = None
def get_issuer():
    global _issuer
    if _issuer is None:
        _issuer = NumberIssuer()
    return _issuer

def reset_issuer():
    get_issuer().clear()

class UnmatchEventException(Exception):
    pass

def order_and_history_from_qrdata(qrdata):
    qs =  DBSession.query(Order, TicketPrintHistory)\
        .filter(TicketPrintHistory.id==qrdata["serial"])\
        .filter(TicketPrintHistory.ordered_product_item_id==OrderedProductItem.id)\
        .filter(OrderedProductItem.ordered_product_id == OrderedProduct.id)\
        .filter(OrderedProduct.order_id == Order.id)\
        .filter(Order.order_no == qrdata["order"])\
        .options(orm.joinedload(Order.performance), 
                 orm.joinedload(Order.shipping_address), 
                 orm.joinedload(TicketPrintHistory.ordered_product_item), 
                 orm.joinedload(TicketPrintHistory.item_token), 
                 orm.joinedload(TicketPrintHistory.seat))
    return qs.first()

def verify_order(order, event_id="*"):
    performance = order.performance
    if event_id != "*" and str(performance.event_id) != str(event_id):
        fmt = "ticketdata_from_qrdata: unmatched event id (order.id=%s, expected event_id=%s, event_id=%s)"
        logger.warn(fmt % (order.id, event_id, performance.event_id))
        raise UnmatchEventException


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

def ordered_product_item_token_query_on_organization(organization_id):
    return (DBSession.query(OrderedProductItemToken) 
            .join(OrderedProductItem) 
            .join(OrderedProduct) 
            .filter(Order.id==OrderedProduct.order_id) 
            .filter(Order.organization_id==organization_id))

def get_matched_ordered_product_item_token(ordered_product_item_token_id, organization_id):
    qs = ordered_product_item_token_query_on_organization(organization_id)
    return qs.filter(OrderedProductItemToken.id==ordered_product_item_token_id).first()

class EnableTicketTemplatesCache(object):
    def __init__(self):
        self.cache = {}

    def __call__(self, ordered_product_item_token):
        bundle = ordered_product_item_token.item.product_item.ticket_bundle
        if bundle.id in self.cache:
            return self.cache[bundle.id][:]
        else:
            self.cache[bundle.id] = enable_ticket_template_list(ordered_product_item_token)
            return self.cache[bundle.id]

def enable_ticket_template_list(ordered_product_item_token):
    producer = ApplicableTicketsProducer.from_bundle(ordered_product_item_token.item.product_item.ticket_bundle)
    r = []
    for ticket_template in producer.qr_only_tickets():
        if ticket_template is None:
            logger.error("*enable_ticket_template_list ticket_template=None (token_id=%s)" % ordered_product_item_token.id)
        r.append(ticket_template)
    return r


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
        .join(c_models.Order)\
        .filter(c_models.Order.performance_id==performance_id)\
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
    total_qr_printed = token_query.filter(OrderedProductItemToken.printed_at != None).count()

    total_other_printed = _as_total_quantity(_query_removed_by_delivery_plugin(opi_query, QR_DELIVERY_ID).filter(OrderedProductItem.printed_at != None))

    return {
        "total": total, 

        "total_qr": total_qr, 
        "total_other": total - total_qr, 

        "qr_printed": total_qr_printed, 
        "qr_unprinted": total_qr - total_qr_printed, 

        "other_printed": total_other_printed, 
        "other_unprinted": total - total_qr - total_other_printed, 
        }
    

