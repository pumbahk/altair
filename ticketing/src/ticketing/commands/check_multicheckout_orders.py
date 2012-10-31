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

from pyramid.paster import get_app, bootstrap

from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from sqlalchemy.orm.attributes import manager_of_class
from sqlalchemy.orm.properties import ColumnProperty, RelationshipProperty

from datetime import datetime
from dateutil.parser import parse as parsedate

from ticketing.models import DBSession
from ticketing.core import models as c_models
from ticketing.multicheckout import models as mc_models
from ticketing.cart import models as cart_models
from ticketing.multicheckout.api import checkout_inquiry

logger = logging.getLogger(__name__)

io_encoding = locale.getpreferredencoding()

def get_columns(obj):
    manager = manager_of_class(type(obj))
    if manager is None:
        raise TypeError("No mapper is defined for %s" % type(obj))
    retval = []
    for property in manager.mapper.iterate_properties:
        if isinstance(property, ColumnProperty):
            retval.append(property.key)
    return retval

def dump(obj, indent=0):
    klass_name = type(obj).__name__
    print >>sys.stderr, ' ' * indent + klass_name
    print >>sys.stderr, ' ' * indent + '-' * len(klass_name)
    if obj is None:
        print >>sys.stderr, ' ' * indent + '(None)'
        return
    columns = get_columns(obj)
    for k in columns:
        print >>sys.stderr, (u' ' * indent + u'%s: %s' % (k, getattr(obj, k))).encode(io_encoding)

def check(env, start, end):
    request = env['request']
    q = DBSession.query(mc_models.MultiCheckoutResponseCard, c_models.Order) \
        .outerjoin(c_models.Order, mc_models.MultiCheckoutResponseCard.OrderNo == c_models.Order.order_no) \
        .filter(mc_models.MultiCheckoutResponseCard.Status.in_(
                [mc_models.MultiCheckoutStatusEnum.Settled.v,
                 mc_models.MultiCheckoutStatusEnum.Authorized.v]))
    if start is not None:
        q = q.filter(mc_models.MultiCheckoutResponseCard.ReqYmd >= parsedate(start).strftime("%Y%m%d"))
    if end is not None:
        q = q.filter(mc_models.MultiCheckoutResponseCard.ReqYmd <= parsedate(end).strftime("%Y%m%d"))
    for resp, order in q.all():
        logger.debug('Checking order %s...' % resp.OrderNo)
        if order is None:
            organization_id = mc_models.MulticheckoutSetting.query.filter_by(shop_id=resp.Storecd).first().organization_id
            request.host = c_models.Host.query.filter_by(organization_id=organization_id).first().host_name
            result = checkout_inquiry(request, resp.OrderNo)
            if result.Status == mc_models.MultiCheckoutStatusEnum.Settled.v:
                print >>sys.stderr, "%s: no corresponding order found!" % (resp.OrderNo, )
                try:
                    cart = cart_models.Cart.from_order_no(resp.OrderNo)
                    dump(cart, 4)
                    if cart.shipping_address is not None:
                        dump(cart.shipping_address, 4)
                except NoResultFound:
                    print >>sys.stderr, "%s: no cart that corresponds to the order found!" % (resp.OrderNo, )
                except MultipleResultsFound:
                    print >>sys.stderr, "%s: more than one carts with the same order number found!" % (resp.OrderNo, )

def main():
    parser = argparse.ArgumentParser(description='check multicheckout orders')
    parser.add_argument('config_uri', metavar='config', type=str, nargs=1,
                        help='config file')
    parser.add_argument('--start', metavar='startdate', type=str,
                        help='Orders made since startdate will be checked')
    parser.add_argument('--end', metavar='enddate', type=str,
                        help='Orders made till enddate will be checked')
    parsed_args = parser.parse_args()

    check(bootstrap(parsed_args.config_uri[0]), parsed_args.start, parsed_args.end)

if __name__ == '__main__':
    main()
