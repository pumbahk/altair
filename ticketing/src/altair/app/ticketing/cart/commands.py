# -*- coding:utf-8 -*-
import os
import sys
import logging
import argparse
import sqlahelper
from datetime import datetime, timedelta
from pyramid.paster import bootstrap, setup_logging

import transaction
from altair.app.ticketing.core import models as o_m
from altair.app.ticketing.core.api import get_channel
from altair.multicheckout.exceptions import MultiCheckoutAPITimeoutError
from altair.app.ticketing.checkout import api as checkout_api
from . import api
from altair.app.ticketing.cart.exceptions import InvalidCartStatusError
from sqlalchemy.sql.expression import not_


# copied from altair.app.ticketing.payments.plugins.multicheckout
def get_order_no(request, cart):
    if request.registry.settings.get('multicheckout.testing', False):
        return cart.order_no + "00"
    return cart.order_no

def join_cart_and_order():
    """ 過去データのcart.orderを補正する
    """
    from . import models as m
    config_file = sys.argv[1]
    app_env = bootstrap(config_file)

    # 対象カート
    carts = m.Cart.query.filter(m.Cart.finished_at!=None).filter(m.Cart.order_id==None).with_lockmode('update').all()
    logging.info('process for %s carts' % len(carts))

    for cart in carts:
        order = o_m.Order.query.filter(o_m.Order.order_no==cart.order_no).with_lockmode('update').first()
        if order is None:
            continue
        cart.order = order
        logging.info('order_no = %s : cart[id=%s].order=order[%s]' % (cart.order_no, cart.id, order.id))
    transaction.commit()

def release_carts():
    """ 期限切れカートのオーソリをキャンセルする
    """
    from . import models as m

    fmt = '%Y-%m-%d %H:%M:%S'
    default_from = (datetime.datetime.now() - datetime.timedelta(minutes=30)).strftime(fmt)
    parser = argparse.ArgumentParser()
    parser.add_argument('config')
    parser.add_argument('--all', default=False, action='sture_true')
    parser.add_argument('--from', dest='from_', default=default_from)
    args = parser.parse_args()

    setup_logging(args.config)
    env = bootstrap(args.config)
    request = env['request']
    registry = env['registry']
    settings = registry.settings
    expire_time = int(settings['altair_cart.expire_time'])

    target_to = datetime.now() - timedelta(minutes=expire_time)
    target_from = None if args.all else datetime.strptime(args.from_, fmt)

    # 多重起動防止
    LOCK_NAME = release_carts.__name__
    LOCK_TIMEOUT = 10
    conn = sqlahelper.get_engine().connect()
    status = conn.scalar("select get_lock(%s,%s)", (LOCK_NAME, LOCK_TIMEOUT))
    if status != 1:
        logging.warn('lock timeout: already running process')
        return

    logging.info("start release_cart")

    # 期限切れカート取得
    query = m.Cart.query.filter(
        m.Cart.created_at < target_to,
        m.Cart.finished_at == None,
        m.Cart.deleted_at == None,
        m.Cart.order_id == None
    ).with_entities(
        m.Cart.id
    )
    if target_from:
        query = query.filter(m.Cart.created_at > target_from)

    count = 0
    for (cart_id,) in query.all():
        cart = m.Cart.query.filter_by(id=cart_id).with_lockmode('update').one()
        try:
            order_no = get_order_no(request, cart)
        except InvalidCartStatusError:
            order_no = None

        logging.info("begin releasing cart (id=%d, order_no=%s)" % (cart_id, order_no))
        if not cart.release():
            logging.info('failed to release cart (id=%d). transaction will be aborted shortly' % cart_id)
            transaction.abort()
            continue

        cart.finished_at = datetime.now()
        logging.info('TRANSACTION IS BEING COMMITTED...')
        transaction.commit()
        count += 1

    conn.close()
    logging.info('end release_cart (count={0})'.format(count))
