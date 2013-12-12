# encoding: utf-8

from pyramid.paster import bootstrap

class ApplicationError(Exception):
    pass

def main(env, args):
    from altair.app.ticketing.tickets.preview.api import SEJPreviewCommunication
    from altair.app.ticketing.core.models import (
        Performance, Event, ProductItem,
        Order, OrderedProduct, OrderedProductItem,
        TicketBundle, Ticket, TicketFormat, DeliveryMethod,
        Stock
        )
    from altair.app.ticketing.payments.plugins import SEJ_DELIVERY_PLUGIN_ID
    from altair.app.ticketing.payments.plugins.sej import get_tickets
    request = env['request']
    settings = env['registry'].settings
    comm = SEJPreviewCommunication(settings['altair.preview.sej.post_url'])
    try:
        orders = Order.query \
            .join(Order.items) \
            .join(Order.performance) \
            .join(Performance.event) \
            .join(OrderedProduct.ordered_product_items) \
            .join(OrderedProductItem.product_item) \
            .join(ProductItem.ticket_bundle) \
            .join(ProductItem.stock) \
            .join(TicketBundle.tickets) \
            .join(Ticket.ticket_format) \
            .join(TicketFormat.delivery_methods) \
            .filter(DeliveryMethod.delivery_plugin_id == SEJ_DELIVERY_PLUGIN_ID) \
            .filter(Event.organization_id.in_(args)) \
            .filter(Stock.stock_holder_id != None) \
            .group_by(Order.sales_segment_id) \
            .all()
        for order in orders:
            try:
                ticket_descs = get_tickets(order)
                for i, ticket_desc in enumerate(ticket_descs):
                    png = comm.communicate(request, unicode(ticket_desc['xml']).encode('cp932'))
                    open('out/%s-%d.png' % (order.order_no, i), 'wb').write(png)
            except Exception as e:
                print order.order_no, unicode(e).encode('utf-8')
    except ApplicationError as e:
        sys.stderr.write(e.message + "\n")
        sys.stderr.flush()

if __name__ == '__main__':
    import sys
    config_file = sys.argv[1]
    env = bootstrap(config_file)
    main(env, sys.argv[2:])
