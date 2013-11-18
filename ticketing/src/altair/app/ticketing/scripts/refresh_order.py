# encoding: utf-8
import sys
import itertools
import logging
import argparse
import re

import sqlahelper
from sqlalchemy.sql.expression import desc
from paste.deploy import loadapp
from pyramid.paster import bootstrap, setup_logging
import transaction

logger = logging.getLogger(__name__)

def message(msg, auxiliary=False):
    logger.log(auxiliary and logging.DEBUG or logging.INFO, msg)
    pad = '  ' if auxiliary else ''
    print >>sys.stderr, pad + msg

def refresh_orders(request, session, orders):
    from altair.app.ticketing.core.models import OrganizationSetting, Event, SalesSegmentGroup, SalesSegment, Order
    from altair.app.ticketing.payments.api import lookup_plugin
    for order in orders:
        session.add(order)
        message('Trying to refresh order %s (id=%d, payment_delivery_pair={ payment_method=%s, delivery_method=%s })...' % (order.order_no, order.id, order.payment_delivery_pair.payment_method.name, order.payment_delivery_pair.delivery_method.name))
        os = session.query(OrganizationSetting) \
            .join(Event, Event.organization_id == OrganizationSetting.organization_id) \
            .join(SalesSegmentGroup, SalesSegmentGroup.event_id == Event.id) \
            .join(SalesSegment, SalesSegment.sales_segment_group_id == SalesSegmentGroup.id) \
            .join(Order) \
            .filter(Order.id == order.id) \
            .one()
        request.altair_checkout3d_override_shop_name = os.multicheckout_shop_name
        payment_delivery_plugin, payment_plugin, delivery_plugin = lookup_plugin(request, order.payment_delivery_pair)
        if payment_delivery_plugin is not None:
            try:
                payment_delivery_plugin.refresh(request, order)
                print 'OK'
            finally:
                transaction.commit()
        else:
            try:
                payment_plugin.refresh(request, order)
            finally:
                transaction.commit()
            session.add(order)
            try:
                delivery_plugin.refresh(request, order)
            finally:
                transaction.commit()
        session.add(order)
        message('Finished refreshing order %s (id=%d)' % (order.order_no, order.id))

def main(argv=sys.argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('config_uri', metavar='config', type=str,
                        help='config file')
    parser.add_argument('order_no', metavar='order_no', type=str, nargs='*',
                        help='order_no')

    args = parser.parse_args()

    setup_logging(args.config_uri)
    env = bootstrap(args.config_uri)
    request = env['request']

    session = sqlahelper.get_session()

    from altair.app.ticketing.core.models import Order
    try:
        orders = []
        for order_no in args.order_no:
            order = session.query(Order).filter_by(order_no=order_no).order_by(desc(Order.branch_no)).first()
            if order is None:
                raise Exception('Order %s could not be found' % order_no)
            orders.append(order)
        refresh_orders(request, session, orders)
    except Exception as e:
        raise
        message(e.message)

if __name__ == '__main__':
    main()
