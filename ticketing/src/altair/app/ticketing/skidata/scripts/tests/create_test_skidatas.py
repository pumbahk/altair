#! /usr/bin/env python
#-*- coding: utf-8 -*-

import argparse
import logging
from random import randrange
from datetime import datetime
import transaction

from pyramid.paster import bootstrap

from altair.app.ticketing.models import DBSession
from altair.app.ticketing.cart import api
from altair.app.ticketing.operators.models import Operator
from altair.app.ticketing.core.models import ShippingAddress, Product, ChannelEnum

from altair.app.ticketing.orders.api import create_inner_order
from altair.app.ticketing.payments.plugins import SKIDATA_QR_DELIVERY_PLUGIN_ID

logger = logging.getLogger(__name__)


def _get_pdmp(sales_segment):
    for pdmp in sales_segment.payment_delivery_method_pairs:
        if pdmp.delivery_method.delivery_plugin_id == SKIDATA_QR_DELIVERY_PLUGIN_ID:
            return pdmp


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', metavar='config', type=str, required=True)
    parser.add_argument('-pid', '--product_id', metavar='product_id', type=str, required=True)
    parser.add_argument('-ocount', '--order_count', metavar='order_count', type=str, required=True)

    args = parser.parse_args()
    env = bootstrap(args.config)
    request = env['request']
    session = DBSession()

    order_count = int(args.order_count)
    product_id = int(args.product_id)
    try:
        print ('create start batch')
        shipping_address = ShippingAddress()
        shipping_address.first_name = u'ラク'
        shipping_address.last_name = u'テスト'
        shipping_address.first_name_kana = u'ラク'
        shipping_address.last_name_kana = u'テスト'
        shipping_address.country = u'日本'
        shipping_address.zip = u'2160001'
        shipping_address.prefecture = u'神奈川県'
        shipping_address.city = u'川崎市'
        shipping_address.address_1 = u'中原区'
        shipping_address.address_2 = u'101'
        shipping_address.email_1 = u'1@1.com'
        shipping_address.tel_1 = u'09012341234'
        shipping_address.tel_2 = u"09012341235"

        for i in range(order_count):
            # タスクステータス更新
            transaction.begin()
            product = session.query(Product).filter_by(id=product_id).one()
            sales_segment = product.sales_segment
            if sales_segment.has_that_delivery(SKIDATA_QR_DELIVERY_PLUGIN_ID):
                pdmp = _get_pdmp(sales_segment)
            else:
                print ('order create failure')
                return
            operator = session.query(Operator).filter_by(id=product.performance.event.setting.event_operator_id).one()

            order_quantity = randrange(1, 11, 1)  # get random quantity from 1~10
            # create cart
            cart = api.order_products(request, sales_segment, [(product, order_quantity)])
            cart.payment_delivery_pair = pdmp
            cart.channel = ChannelEnum.INNER.v
            cart.operator = operator
            cart.shipping_address = shipping_address
            session.add(cart)

            # create order
            order = create_inner_order(request, cart, None)
            order.paid_at = datetime.now()
            session.add(order)
            session.flush()

            print(order.order_no, ':', order_quantity)
            transaction.commit()
        print ('create end batch:', order_count)
    except Exception as e:
        logger.error(e.message)
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
