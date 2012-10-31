#!/usr/bin/env python
# encoding: utf-8
from lxml import etree
import os
import sys
import transaction
import re
import argparse
import locale
import logging

import transaction

from pyramid.paster import get_app, bootstrap

from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from sqlalchemy.orm.attributes import manager_of_class
from sqlalchemy.orm.properties import ColumnProperty, RelationshipProperty

from datetime import datetime
from dateutil.parser import parse

from ticketing.models import DBSession
from ticketing.core import models as c_models
from ticketing.cart import models as cart_models
from ticketing.utils import sensible_alnum_encode

logger = logging.getLogger(__name__)

io_encoding = locale.getpreferredencoding()

def calculate_order_no(cart):
    return cart.performance.event.organization.code + sensible_alnum_encode(cart.id).zfill(10)

def populate(env):
    q = DBSession.query(cart_models.Cart)
    for cart in q.all():
        calculated_order_no = calculate_order_no(cart)
        print 'Processing %s...' % calculated_order_no
        if cart.order is not None and calculated_order_no != cart.order.order_no:
            raise Exception('Validation failure! (%s != %s)' % (calculated_order_no, cart.order.order_no))
        cart._order_no = calculated_order_no

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
