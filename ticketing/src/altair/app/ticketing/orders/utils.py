# -*- coding:utf-8 -*-
## TODO: move to enqueue.py
from collections import Counter
import re
import logging
import pystache
from altair.app.ticketing.tickets.utils import build_dict_from_ordered_product_item_token
from altair.app.ticketing.tickets.utils import build_dicts_from_ordered_product_item
from altair.app.ticketing.tickets.utils import build_cover_dict_from_order
from altair.app.ticketing.core.models import TicketPrintQueueEntry, TicketCover
from altair.app.ticketing.core.utils import ApplicableTicketsProducer
from altair.app.ticketing.payments.plugins import SEJ_DELIVERY_PLUGIN_ID
logger = logging.getLogger(__name__)

def delivery_type_from_built_dict(dict_):
    try:
        if int(dict_["deliveryMethod"][u"plugin_id"]) == int(SEJ_DELIVERY_PLUGIN_ID):
            return "sej"
        return "other"
    except (KeyError, ValueError),  e:
        logger.warn("orderes: preview ticket: %s" % e)
        return "other"


def item_ticket_pairs(order, ticket_dict=None, ticket=None):
    for ordered_product in order.items:
        for ordered_product_item in ordered_product.ordered_product_items:
            ticket = ticket or ticket_dict.get(int(ordered_product_item.id))
            if ticket is None:
                logger.warn("*ticket print queue* ticket is not found. order.id=%s, item.id=%s" % \
                                (order.id, ordered_product_item.id))
                continue
            yield ordered_product_item, ticket

def enqueue_cover(operator, order):
    cover = TicketCover.get_from_order(order)
    if cover is None:
        logger.error("cover is not found. order = {order.id} organization_id = {operator.organization_id}".format(order=order, operator=operator))
        return 
    dict_ = build_cover_dict_from_order(order)
    TicketPrintQueueEntry.enqueue(
        operator=operator, 
        ticket=cover.ticket, 
        data = {u"drawing": pystache.render(cover.ticket.data["drawing"], dict_)}, 
        summary=u"表紙 {order.order_no}".format(order=order)
        )

def enqueue_for_order(operator, order, ticket_format_id=None):
    for ordered_product in order.items:
        for ordered_product_item in ordered_product.ordered_product_items:
            enqueue_item(operator, order, ordered_product_item, ticket_format_id)

def enqueue_token(operator, token, ticket, i, j, ordered_product_item=None, order=None, seat=None, issuer=None):
    dict_ = build_dict_from_ordered_product_item_token(token, ticket_number_issuer=issuer)
    ordered_product_item = ordered_product_item or token.ordered_product_item
    TicketPrintQueueEntry.enqueue(
        operator=operator, 
        ticket=ticket, 
        data={ u'drawing': pystache.render(ticket.data['drawing'], dict_) },
        summary=u'注文 %s - %s%s' % (
            order.order_no,
            ordered_product_item.product_item.name,
            u' (%d / %d枚目)' % (i, j) if (i and j) else u""
            ),
        ordered_product_item=ordered_product_item,
        seat=seat
        )
   
def enqueue_item(operator, order, ordered_product_item, ticket_format_id=None):
    bundle = ordered_product_item.product_item.ticket_bundle
    dicts = comfortable_sorted_built_dicts(ordered_product_item)
    for index, (seat, dict_) in enumerate(dicts):
        for ticket in ApplicableTicketsProducer.from_bundle(bundle).will_issued_by_own_tickets(format_id=ticket_format_id):
            TicketPrintQueueEntry.enqueue(
                operator=operator,
                ticket=ticket,
                data={ u'drawing': pystache.render(ticket.data['drawing'], dict_) },
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

class NumberIssuer(object):
    def __init__(self):
        self.counter = Counter()

    def __call__(self, k):
        v = self.counter[k] + 1
        self.counter[k] = v
        return v
        
def comfortable_sorted_built_dicts(ordered_product_item):
    dicts = build_dicts_from_ordered_product_item(ordered_product_item, ticket_number_issuer=NumberIssuer())
    return sorted(dicts, key=compare_by_comfortable_order)
