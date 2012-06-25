# -*- coding:utf-8 -*-

from ticketing.utils import StandardEnum

class OrderStatus(StandardEnum):
    PendingPayment   = 1
    UnPaid           = 2
    Paid             = 3
    PendingIssue     = 4
    Issued           = 5

def make_order_data(order) :

    performances = dict()
    for ordered_product in order.items:
        for ordered_product_item in ordered_product.ordered_product_items:
            product_item = ordered_product_item.product_item
            performance = product_item.performance
            performances[performance.id]=performance

    class OrderData:
        venue_names = u",".join([u"%s%s" % (p.venue.name, (u"(%s)" % p.venue.site.prefecture if p.venue.site.prefecture else '')) for p in performances.itervalues()])
        event_name = u",".join([p.event.title for p in performances.itervalues()])
        performance_names = u",".join([p.name for p in performances.itervalues()])
        performance_dates = [p.start_on for p in performances.itervalues()]
        id = order.id
        user = order.user
        shipping_address = order.shipping_address
        ordered_from = order.ordered_from

        items = order.items,

        total_amount = order.total_amount

        multicheckout_approval_no = order.multicheckout_approval_no
        payment_delivery_pair = order.payment_delivery_pair

        order_no = order.order_no
        total_amount = order.total_amount
        items = order.items

        created_at = order.created_at

    return OrderData()