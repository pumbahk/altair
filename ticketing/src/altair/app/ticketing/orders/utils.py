# -*- coding:utf-8 -*-

import logging
import pystache
from altair.app.ticketing.tickets.utils import build_dicts_from_ordered_product_item
from altair.app.ticketing.core.models import TicketPrintQueueEntry
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

def enqueue_for_order(operator, order, ticket_format_id=None):
    for ordered_product in order.items:
        for ordered_product_item in ordered_product.ordered_product_items:
            enqueue_item(operator, order, ordered_product_item, ticket_format_id)
   
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

import re
last_char = "\uFE4F" #utf-8(cjk)
DIGIT_RX = re.compile(r"([0-9]+)")

def compare_by_comfortable_order((seat, dicts_)):
    if seat is None:
        return (last_char,  dicts_.get(u"発券番号"))
    else:
        return [(int(x) if x.isdigit() else x) for x in re.split(DIGIT_RX, seat.name) if x]

class RingCounter(object):
    def __init__(self, i=0, maxv=100000):
        self.lower_limit = i
        self.i = i
        self.upper_limit = maxv

    def __call__(self):
        v = self.i
        self.i += 1
        if self.i > self.upper_limit:
            self.i = self.lower_limit
        return v

ticket_number_issuer=RingCounter()

def comfortable_sorted_built_dicts(ordered_product_item):
    dicts = build_dicts_from_ordered_product_item(ordered_product_item, ticket_number_issuer=ticket_number_issuer)
    return sorted(dicts, key=compare_by_comfortable_order)
