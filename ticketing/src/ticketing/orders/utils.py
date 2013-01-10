
# -*- coding:utf-8 -*-
import logging
import pystache
from ticketing.tickets.utils import build_dicts_from_ordered_product_item
from ticketing.core.models import TicketPrintQueueEntry
from ticketing.core.utils import ApplicableTicketsProducer
from ticketing.payments.plugins import SEJ_DELIVERY_PLUGIN_ID
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
    dicts = build_dicts_from_ordered_product_item(ordered_product_item)
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
