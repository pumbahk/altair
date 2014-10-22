# -*- coding:utf-8 -*-

import os
import sys
import logging
import transaction
import argparse

from pyramid.paster import bootstrap, setup_logging
from sqlalchemy.sql import and_
from sqlalchemy.sql.expression import not_
from sqlalchemy.orm import join

from altair.app.ticketing.core import models as m
from altair.app.ticketing.cart import models as m_cart
from altair.app.ticketing.orders import models as m_order
from altair.app.ticketing.checkout import models as m_checkout
from altair.app.ticketing.payments.plugins import CHECKOUT_PAYMENT_PLUGIN_ID
from altair.app.ticketing.payments.plugins.checkout import CheckoutPlugin

def rakuten_checkout_sales():
    ''' 楽天ID決済の売上処理
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument('config')
    args = parser.parse_args()

    setup_logging(args.config)
    env = bootstrap(args.config)
    request = env['request']

    logging.info('start checkout sales batch')

    orders_to_skip = set()
    while True:
        # 楽天ID決済でオーソリ済みになっているOrderを売上済みにする
        query = m_order.Order.query \
            .join(m_checkout.Checkout, m_checkout.Checkout.orderCartId == m_order.Order.order_no) \
            .filter(m_order.Order.canceled_at==None) \
            .filter(m_checkout.Checkout.sales_at==None)

        if orders_to_skip:
            query = query.filter(not_(m_order.Order.id.in_(orders_to_skip)))
        order = query.first()

        if order is None:
            logging.info('not found checkout auth order')
            break
        orders_to_skip.add(order.id)

        if order.payment_delivery_pair.payment_method.payment_plugin_id == CHECKOUT_PAYMENT_PLUGIN_ID:
            try:
                logging.info('target order: %s' % order.order_no)
                plugin = CheckoutPlugin()
                plugin.sales(request, order)
                order.save()
                transaction.commit()
                logging.info('success')
            except Exception as e:
                logging.exception('failed checkout sales')

    logging.info('end checkout sales  batch')
