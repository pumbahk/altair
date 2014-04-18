# encoding: utf-8
import sys
import itertools
import logging
import argparse
import re

import sqlahelper
import transaction
from sqlalchemy.sql.expression import desc
from paste.deploy import loadapp
from pyramid.paster import bootstrap, setup_logging

from altair.app.ticketing.orders.api import refresh_order

logger = logging.getLogger(__name__)

def message(msg, auxiliary=False):
    logger.log(auxiliary and logging.DEBUG or logging.INFO, msg)
    pad = '  ' if auxiliary else ''
    print >>sys.stderr, pad + msg

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

    from altair.app.ticketing.orders.models import Order
    try:
        orders = []
        for order_no in args.order_no:
            order = session.query(Order).filter_by(order_no=order_no).order_by(desc(Order.branch_no)).first()
            if order is None:
                raise Exception('Order %s could not be found' % order_no)
            if order.canceled_at is not None:
                raise Exception('order %s has already been calceled' % order_no)
            orders.append(order_no)

        for order_no in orders:
            order = session.query(Order).filter_by(order_no=order_no).order_by(desc(Order.branch_no)).first()
            try:
                refresh_order(request, session, order)
            except Exception as e:
                message('failed to refresh order %s: %s' % (order_no, e))
                logger.exception(u'failed to refresh order %s' % order_no)
            finally:
                transaction.commit()

    except Exception as e:
        raise
        message(e.message)

if __name__ == '__main__':
    main()
