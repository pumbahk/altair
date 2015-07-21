# -*- coding:utf-8 -*-

import sqlalchemy as sa
import sqlalchemy.orm as orm

from altair.app.ticketing.models import DBSession
from altair.app.ticketing.core.models import TicketPrintHistory
from altair.app.ticketing.orders.models import (
    Order,
    OrderedProductItemToken,
    OrderedProductItem,
    OrderedProduct,
    )

from altair.app.ticketing.payments.plugins.qr import DELIVERY_PLUGIN_ID as QR_DELIVERY_ID
from altair.app.ticketing.payments.plugins import ORION_DELIVERY_PLUGIN_ID
from altair.app.ticketing.core import models as c_models
from altair.app.ticketing.orders import models as order_models
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
    qs = DBSession.query(TicketPrintHistory)
    if qrdata.get("serial"):
        qs = qs.filter(TicketPrintHistory.id == qrdata["serial"])
    if qrdata.get("order"):
        qs = qs.outerjoin(OrderedProductItemToken, OrderedProductItemToken.id == TicketPrintHistory.item_token_id) \
               .outerjoin(OrderedProductItem, OrderedProductItem.id == OrderedProductItemToken.ordered_product_item_id) \
               .outerjoin(OrderedProduct, OrderedProduct.id == OrderedProductItem.ordered_product_id) \
               .outerjoin(Order, (OrderedProduct.order_id == Order.id) | (TicketPrintHistory.order_id == Order.id)) \
               .filter(Order.order_no == qrdata["order"])
    qs = qs.with_entities(Order, TicketPrintHistory)
    qs = qs.options(
        orm.joinedload(Order.performance),
        orm.joinedload(Order.shipping_address),
        orm.joinedload(TicketPrintHistory.ordered_product_item),
        orm.joinedload(TicketPrintHistory.item_token),
        orm.joinedload(TicketPrintHistory.seat)
        )
    return qs.first()

def order_from_token(token, order):
    qs =  DBSession.query(Order, OrderedProductItemToken)\
        .filter(OrderedProductItemToken.id == token)\
        .filter(OrderedProductItemToken.ordered_product_item_id==OrderedProductItem.id)\
        .filter(OrderedProductItem.ordered_product_id == OrderedProduct.id)\
        .filter(OrderedProduct.order_id == Order.id)\
        .filter(Order.order_no == order)\
        .options(orm.joinedload(Order.performance),
                 orm.joinedload(Order.shipping_address),
                 orm.joinedload(OrderedProductItemToken.seat))
    return qs.first()

def verify_order(order, event_id="*"):
    performance = order.performance
    if event_id != "*" and str(performance.event_id) != str(event_id):
        fmt = "ticketdata_from_qrdata: unmatched event id (order.id=%s, expected event_id=%s, event_id=%s)"
        logger.warn(fmt % (order.id, event_id, performance.event_id))
        raise UnmatchEventException


def history_from_token(request, operator_id, order_id, token, template_id=None):
    return TicketPrintHistory(
        operator_id=operator_id,
        seat_id=token.seat_id,
        item_token_id=token.id,
        ordered_product_item_id=token.item.id,
        order_id=order_id,
        ticket_id=template_id
        )

def add_history(request, operator_id, params):
    seat_id = params.get(u'seat_id')
    ordered_product_item_token_id = params.get(u'ordered_product_item_token_id')
    ordered_product_item_id = params.get(u'ordered_product_item_id')
    order_id = params.get(u'order_id')
    ticket_id = params.get(u'ticket_id')
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
    def __init__(self, delivery_plugin_ids=None):
        self.cache = {}
        self.delivery_plugin_ids = delivery_plugin_ids

    def __call__(self, ordered_product_item_token):
        bundle = ordered_product_item_token.item.product_item.ticket_bundle
        if bundle.id in self.cache:
            return self.cache[bundle.id][:]
        else:
            self.cache[bundle.id] = enable_ticket_template_list(ordered_product_item_token, delivery_plugin_ids=self.delivery_plugin_ids)
            return self.cache[bundle.id]

def enable_ticket_template_list(ordered_product_item_token, delivery_plugin_ids=None):
    producer = ApplicableTicketsProducer.from_bundle(ordered_product_item_token.item.product_item.ticket_bundle)
    r = []
    for ticket_template in producer.will_issued_by_own_tickets(delivery_plugin_ids=delivery_plugin_ids):
        if ticket_template is None:
            logger.error("*enable_ticket_template_list ticket_template=None (token_id=%s)" % ordered_product_item_token.id)
        r.append(ticket_template)
    return r


def performance_data_from_performance_id(event_id, performance_id):
    performance = c_models.Performance.query.join(c_models.Event)\
        .filter(c_models.Event.id==event_id, c_models.Performance.id==performance_id)\
        .first()
    return {"name": performance.name,
            "start_on": h.japanese_datetime(performance.start_on),
            "pk": performance.id}

from altair.app.ticketing.print_progress.progress import PerformancePrintProgress
## 余事象取れば計算で求められるけれど。実際にDBアクセスした方が良いのかな。
def total_result_data_from_performance_id(event_id, performance_id):
    performance = c_models.Performance.query.filter_by(id=performance_id,event_id=event_id).one()
    progress = PerformancePrintProgress(performance)
    return {
        "total": progress.total,

        "total_qr": progress.qr.total,
        "total_other": progress.total - progress.qr.total,
        "qr_printed": progress.qr.printed,
        "qr_unprinted": progress.qr.unprinted,

        "other_printed": progress.shipping.printed+progress.other.printed,
        "other_unprinted": progress.shipping.unprinted+progress.other.unprinted,
        }


