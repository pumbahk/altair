# -*- coding:utf-8 -*-

import sys
import logging
from datetime import datetime, timedelta
from pyramid.paster import bootstrap
import transaction
from ..orders import models as o_m
from ..multicheckout import api as a
from . import models as m

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# copied from ticketing.cart.plugins.multicheckout
def get_order_no(request, cart):
    
    if request.registry.settings.get('multicheckout.testing', False):
        return "%012d" % cart.id + "00"
    return cart.order_no

def inquiry_demo():
    config_file = sys.argv[1]
    app_env = bootstrap(config_file)
    request = app_env['request']
    order_no = sys.argv[2]
    inquiry = a.checkout_inquiry(request, order_no)

    print inquiry.Status

    a.checkout_auth_cancel(request, order_no)

def cancel_auth_expired_carts():
    """ 期限切れカートのオーソリをキャンセルする
    """

    config_file = sys.argv[1]

    app_env = bootstrap(config_file)
    request = app_env['request']
    registry = app_env['registry']
    settings = registry.settings
    expire_time = int(settings['altair_cart.expire_time'])

    logger.debug("start auth cancel batch")
    while True:
        now = datetime.now()
        # 期限切れカート取得 1件ずつ処理
        cart = m.Cart.query.filter(
            m.Cart.created_at < now - timedelta(minutes=expire_time)
        ).filter(
            m.Cart.finished_at == None
        ).filter(
            m.Cart.deleted_at == None
        ).first()

        if cart is None:
            logging.info('not found unfinished cart')
            break

        order_no = get_order_no(request, cart)
        # 状態確認
        logger.debug('check for order_no=%s' % order_no)
        inquiry = a.checkout_inquiry(request, order_no)

        # オーソリOKだったらキャンセル
        if inquiry.Status == m.MULTICHECKOUT_AUTH_OK:
            logger.info("cancel auth for order_no=%s" % order_no)
            a.checkout_auth_cancel(request, order_no)
        else:
            logger.info("Order(order_no = %s) status = %s " % (order_no, inquiry.Status))

        cart.finished_at = now
        transaction.commit()
    logger.debug("end auth cancel batch")
