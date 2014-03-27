#!/usr/bin/env python
# encoding: utf-8
import os
import sys
import transaction
import re
import argparse
import locale
import logging
import time

import transaction

from pyramid.paster import get_app, bootstrap

from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from sqlalchemy.orm.attributes import manager_of_class
from sqlalchemy.orm.properties import ColumnProperty, RelationshipProperty

from datetime import datetime
from dateutil.parser import parse

logger = logging.getLogger(__name__)

def populate(env):
    from altair.app.ticketing.models import DBSession
    from altair.app.ticketing.core import models as c_models
    from altair.app.ticketing.cart import models as cart_models
    from altair.app.ticketing.lots import models as lots_models

    class LotEntryAdapter(c_models.CartMixin):
        def __init__(self, entry):
            self.entry = entry

        @property
        def payment_delivery_pair(self):
            return self.entry.payment_delivery_method_pair

        @property
        def created_at(self):
            return self.entry.created_at

    order_no_list = DBSession.query(c_models.Order.order_no).all()
    print 'Orders to process: %d' % len(order_no_list)

    i = 0
    last = time.time()
    for order_no, in order_no_list:
        i += 1
        if i % 100 == 0:
            now = time.time()
            print 'Estimated remaining time: %g seconds' % ((len(order_no_list) - i) * (now - last) / 100.)
            last = now
        print 'Processing %s...' % order_no,
        try:
            order = DBSession.query(c_models.Order).filter_by(order_no=order_no).one()
        except Exception as e:
            print e
            continue
        cart = DBSession.query(cart_models.Cart).filter_by(order_id=order.id).first()
        if cart is not None:
            order.issuing_start_at = cart.issuing_start_at
            order.issuing_end_at = cart.issuing_end_at
            order.payment_start_at = cart.payment_start_at
            order.payment_due_at = cart.payment_due_at
            transaction.commit()
            print 'done'
            continue

        lot_entry = DBSession.query(lots_models.LotEntry).filter_by(entry_no=order_no).first()
        if lot_entry is not None:
            x = LotEntryAdapter(lot_entry)
            order.issuing_start_at = x.issuing_start_at
            order.issuing_end_at = x.issuing_end_at
            order.payment_start_at = x.payment_start_at
            order.payment_due_at = x.payment_due_at
            transaction.commit()
            print 'done'
            continue

        print 'corresponding Cart / LotEntry not found'

def main():
    parser = argparse.ArgumentParser(description='check multicheckout orders')
    parser.add_argument('config_uri', metavar='config', type=str, nargs=1,
                        help='config file')
    parsed_args = parser.parse_args()

    try:
        populate(bootstrap(parsed_args.config_uri[0]))
        transaction.commit()
    finally:
        transaction.abort()

if __name__ == '__main__':
    main()

