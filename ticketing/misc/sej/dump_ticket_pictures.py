# encoding: utf-8

from pyramid.paster import bootstrap
from sqlalchemy.orm import aliased
from altair.sqlahelper import get_db_session
from datetime import datetime

class ApplicationError(Exception):
    pass

def main(env, args):
    from altair.app.ticketing.tickets.preview.api import SEJPreviewCommunication
    from altair.app.ticketing.core.models import (
        Performance, Event, ProductItem,
        TicketBundle, Ticket, TicketFormat, DeliveryMethod,
        TicketFormat_DeliveryMethod, PaymentDeliveryMethodPair,
        )
    from altair.app.ticketing.orders.models import (
        Order,
        OrderedProduct,
        OrderedProductItem,
        )
    from altair.app.ticketing.payments.plugins import SEJ_DELIVERY_PLUGIN_ID
    from altair.app.ticketing.payments.plugins.sej import get_tickets, get_ticket_template_id_from_ticket_format
    from altair.app.ticketing.sej.api import get_ticket_template_record
    request = env['request']
    settings = env['registry'].settings
    comm = SEJPreviewCommunication(settings['altair.preview.sej.post_url'])
    session = get_db_session(request, 'slave')
    ticket_template_id_to_ticket_format_map = dict(
        (get_ticket_template_id_from_ticket_format(ticket_format), ticket_format)
        for ticket_format in \
            session.query(TicketFormat) \
            .join(TicketFormat.delivery_methods) \
            .filter(DeliveryMethod.delivery_plugin_id == SEJ_DELIVERY_PLUGIN_ID)
        )
    try:
        _DeliveryMethod = aliased(DeliveryMethod)
        orders = session.query(Order) \
            .join(Order.items) \
            .join(Order.performance) \
            .join(Order.payment_delivery_pair) \
            .join(_DeliveryMethod, PaymentDeliveryMethodPair.delivery_method_id == _DeliveryMethod.id) \
            .join(Performance.event) \
            .join(OrderedProduct.elements) \
            .join(OrderedProductItem.product_item) \
            .join(ProductItem.ticket_bundle) \
            .join(TicketBundle.tickets) \
            .join(Ticket.ticket_format) \
            .join(TicketFormat.delivery_methods) \
            .filter(_DeliveryMethod.delivery_plugin_id == SEJ_DELIVERY_PLUGIN_ID) \
            .filter(DeliveryMethod.delivery_plugin_id == SEJ_DELIVERY_PLUGIN_ID) \
            .filter(Performance.start_on >= datetime.now()) \
            .filter(Event.organization_id.in_(args)) \
            .group_by(TicketBundle.id) \
            .order_by(Order.id) \
            .all()
        print '%d orders' % len(orders)
        for order in orders:
            try:
                ticket_descs = get_tickets(request, order)
                for i, ticket_desc in enumerate(ticket_descs):
                    out_file = 'out/%s-%d.png' % (order.order_no, i)
                    print 'rendering %s ...' % out_file,
                    ticket_format = ticket_template_id_to_ticket_format_map[ticket_desc['ticket_template_id']]
                    ticket_record = get_ticket_template_record(request, ticket_desc['ticket_template_id'])
                    png = comm.communicate(request, ('<?xml version="1.0" encoding="Shift_JIS" ?>' + unicode(ticket_desc['xml']).encode('cp932'), ticket_record), ticket_format)
                    open(out_file, 'wb').write(png)
                    print 'done'
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
