# -*- coding:utf-8 -*-
## TODO: move to enqueue.py
import re
import logging
from altair.app.ticketing.tickets.utils import build_dict_from_ordered_product_item_token
from altair.app.ticketing.tickets.utils import build_dicts_from_ordered_product_item
from altair.app.ticketing.tickets.utils import build_cover_dict_from_order
from altair.app.ticketing.tickets.utils import NumberIssuer
from altair.app.ticketing.core.models import TicketPrintQueueEntry, TicketCover
from altair.app.ticketing.core.utils import ApplicableTicketsProducer
from altair.app.ticketing.payments.plugins import SEJ_DELIVERY_PLUGIN_ID
from altair.app.ticketing.utils import json_safe_coerce
logger = logging.getLogger(__name__)

## 
from pyramid.threadlocal import get_current_request
from altair.app.ticketing.tickets.api import get_svg_builder

def delivery_type_from_built_dict(dict_):
    try:
        if int(dict_["deliveryMethod"][u"plugin_id"]) == int(SEJ_DELIVERY_PLUGIN_ID):
            return "sej"
        return "other"
    except (KeyError, ValueError),  e:
        logger.warn("orders: preview ticket: %s" % e)
        return "other"

def guess_preview_type_from_ticket_format(ticket_format):
    if any(int(delivery_method.delivery_plugin_id) == int(SEJ_DELIVERY_PLUGIN_ID) for delivery_method in ticket_format.delivery_methods):
        return 'sej'
    else:
        return 'other'

def item_ticket_pairs(order, ticket_dict=None, ticket=None):
    for ordered_product in order.items:
        for ordered_product_item in ordered_product.ordered_product_items:
            ticket = ticket or ticket_dict.get(int(ordered_product_item.id))
            if ticket is None:
                logger.warn("*ticket print queue* ticket is not found. order.id=%s, item.id=%s" % \
                                (order.id, ordered_product_item.id))
                continue
            yield ordered_product_item, ticket

def enqueue_cover(request, operator, order, ticket_format_id=None):
    cover = TicketCover.get_from_order(order, ticket_format_id)
    if cover is None:
        logger.info("cover is not found. order = {order.id} organization_id = {operator.organization_id}".format(order=order, operator=operator))
        return
    if not is_cover_print(order):
        return
    dict_ = build_cover_dict_from_order(order)
    svg_builder = get_svg_builder(request)
    TicketPrintQueueEntry.enqueue(
        operator=operator, 
        ticket=cover.ticket, 
        data = json_safe_coerce({u"drawing": svg_builder.build(cover.ticket, dict_), "vars_defaults": cover.ticket.vars_defaults}), 
        summary=u"表紙 {order.order_no}".format(order=order)
        )

def is_cover_print(order):
    cover_print = False
    for ordered_product in order.items:
        for ordered_product_item in ordered_product.ordered_product_items:
            bundle = ordered_product_item.product_item.ticket_bundle
            for ticket in bundle.tickets:
                if ticket.cover_print:
                    cover_print = True
    return cover_print

def enqueue_for_order(request, operator, order, ticket_format_id=None, delivery_plugin_ids=None):
    svg_builder = get_svg_builder(request)
    for ordered_product in order.items:
        for ordered_product_item in ordered_product.ordered_product_items:
            enqueue_item(
                request, operator, order, ordered_product_item,
                ticket_format_id=ticket_format_id,
                delivery_plugin_ids=delivery_plugin_ids,
                svg_builder=svg_builder
                )

def enqueue_token(request, operator, token, ticket, i, j, ordered_product_item=None, order=None, seat=None, issuer=None):
    dict_ = build_dict_from_ordered_product_item_token(token, ticket_number_issuer=issuer)
    ordered_product_item = ordered_product_item or token.ordered_product_item
    svg_builder = get_svg_builder(request)
    TicketPrintQueueEntry.enqueue(
        operator=operator, 
        ticket=ticket, 
        data=json_safe_coerce({u'drawing': svg_builder.build(ticket, dict_), u"vars_defaults": ticket.vars_defaults}),
        summary=u'注文 %s - %s%s' % (
            order.order_no,
            ordered_product_item.product_item.name,
            u' (%d / %d枚目)' % (i, j) if (i and j) else u""
            ),
        ordered_product_item=ordered_product_item,
        seat=seat
        )
   
def enqueue_item(request, operator, order, ordered_product_item, ticket_format_id=None, delivery_plugin_ids=None, svg_builder=None):
    bundle = ordered_product_item.product_item.ticket_bundle
    dicts = comfortable_sorted_built_dicts(ordered_product_item)
    svg_builder = svg_builder or get_svg_builder(request)
    for index, (seat, dict_) in enumerate(dicts):
        iter_factory = ApplicableTicketsProducer.from_bundle(bundle)
        # CXX: よくない仕様だけど互換性のため。ticket_format_id が None でないときはそちらのみを見る
        if delivery_plugin_ids is None and ticket_format_id is not None:
            tickets = iter_factory.all(format_id=ticket_format_id)
        else:
            tickets = iter_factory.will_issued_by_own_tickets(delivery_plugin_ids=delivery_plugin_ids)
        for ticket in tickets:
            TicketPrintQueueEntry.enqueue(
                operator=operator,
                ticket=ticket,
                data=json_safe_coerce({ u'drawing': svg_builder.build(ticket, dict_), u"vars_defaults": ticket.vars_defaults}),
                summary=u'注文 %s - %s%s' % (
                    order.order_no,
                    ordered_product_item.product_item.name,
                    (u' (%d / %d枚目)' % (index + 1, len(dicts))
                     if len(dicts) > 1 else u'')
                    ),
                ordered_product_item=ordered_product_item,
                seat=seat
                )
last_char = "\uFE4F" #utf-8(cjk)
DIGIT_RX = re.compile(r"([0-9]+)")

def compare_by_comfortable_order((seat, dicts_)):
    if seat is None:
        return (last_char,  dicts_.get(u"発券番号"))
    else:
        return [(int(x) if x.isdigit() else x) for x in re.split(DIGIT_RX, seat.name) if x]

def comfortable_sorted_built_dicts(ordered_product_item):
    dicts = build_dicts_from_ordered_product_item(ordered_product_item, ticket_number_issuer=NumberIssuer())
    return sorted(dicts, key=compare_by_comfortable_order)

