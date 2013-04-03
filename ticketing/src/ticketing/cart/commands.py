# -*- coding:utf-8 -*-
import os
import sys
import logging
from datetime import datetime, timedelta
from pyramid.paster import bootstrap

import transaction
from ticketing.core import models as o_m
from ticketing.core.api import get_channel
from ticketing.multicheckout import api as multicheckout_api
from ticketing.checkout import api as checkout_api
from . import api
from ticketing.cart.exceptions import UnassignedOrderNumberError
from sqlalchemy.sql.expression import not_


# copied from ticketing.payments.plugins.multicheckout
def get_order_no(request, cart):
    
    if request.registry.settings.get('multicheckout.testing', False):
        #return "%012d" % cart.id + "00"
        return cart.order_no + "00"
    return cart.order_no

def inquiry_demo():
    logger = logging.getLogger(__name__)
    config_file = sys.argv[1]
    app_env = bootstrap(config_file)
    request = app_env['request']
    order_no = sys.argv[2]
    inquiry = multicheckout_api.checkout_inquiry(request, order_no)

    print inquiry.Status

    multicheckout_api.checkout_auth_cancel(request, order_no)

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

def cancel_auth_expired_carts():
    """ 期限切れカートのオーソリをキャンセルする
    """

    from . import models as m
    config_file = sys.argv[1]

    app_env = bootstrap(config_file)
    import sqlahelper
    assert sqlahelper.get_session().bind
    m.DBSession.bind = m.DBSession.bind or sqlahelper.get_session().bind
    
    logfile = os.path.abspath(sys.argv[2])
    logging.config.fileConfig(logfile)
    request = app_env['request']
    registry = app_env['registry']
    settings = registry.settings
    expire_time = int(settings['altair_cart.expire_time'])

    carts_to_skip = set()
    logging.info("start auth cancel batch")
    while True:
        now = datetime.now()
        # 期限切れカート取得 1件ずつ処理
        cart_q = m.Cart.query.filter(
            m.Cart.created_at < now - timedelta(minutes=expire_time)
        ).filter(
            m.Cart.finished_at == None
        ).filter(
            m.Cart.deleted_at == None
        )
        if carts_to_skip:
            cart_q = cart_q.filter(not_(m.Cart.id.in_(carts_to_skip)))

        cart = cart_q.first()

        if cart is None:
            logging.info('not found unfinished cart')
            break

        try:
            order_no = get_order_no(request, cart)
        except UnassignedOrderNumberError:
            order_no = None

        cart_id = cart.id
        logging.info("begin releasing cart (id=%d, order_no=%s)" % (cart_id, order_no))
        if not cart.release():
            logging.info('failed to release cart (id=%d). transaction will be aborted shortly' % cart_id)
            transaction.abort()
            carts_to_skip.add(cart_id)
            continue
        logging.info('TRANSACTION IS BEING COMMITTED...')
        transaction.commit()
        logging.info('verifying if the cart in question (id=%d) still exists' % cart_id)
        cart = m.Cart.query.filter_by(id=cart_id).first()
        if cart is None:
            logging.info('cart (id=%d) IS GONE FOR SOME REASONS. SIGH.')
            continue

        if api.is_multicheckout_payment(cart):
            # 状態確認
            logging.info('well, then trying to cancel the authorization request associated with the order (order_no=%s)' % order_no)
            logging.info('check for order_no=%s' % order_no)
            request.altair_checkout3d_override_shop_name = None
            try:
                request.altair_checkout3d_override_shop_name =  cart.performance.event.organization.setting.multicheckout_shop_name
            except:
                logging.info('can not detect shop_name for order_no = %s' % order_no)
                carts_to_skip.add(cart_id)
                continue
            if not request.altair_checkout3d_override_shop_name:
                logging.info('can not detect shop_name for order_no = %s' % order_no)
                carts_to_skip.add(cart_id)
                continue

            inquiry = multicheckout_api.checkout_inquiry(request, order_no)

            # オーソリOKだったらキャンセル
            if inquiry.Status == m.MULTICHECKOUT_AUTH_OK:
                logging.info("cancel auth for order_no=%s" % order_no)
                multicheckout_api.checkout_auth_cancel(request, order_no)
            else:
                logging.info("Order(order_no = %s) status = %s " % (order_no, inquiry.Status))

        cart.finished_at = now
        logging.info("TRANSACTION IS BEING COMMITTED AGAIN...")
        transaction.commit()

    logging.info("end auth cancel batch")
