# -*- coding:utf-8 -*-

""" カートリリースバッチ

"""

import logging
import argparse
import transaction
from datetime import datetime, timedelta
from pyramid.paster import bootstrap, setup_logging
from altair.app.ticketing.models import DBSession
from altair.app.ticketing.cart.models import Cart

logger = logging.getLogger(__name__)

def release_carts(request):
    """ 期限切れカートを解放する
    """

    logger.debug("trace release_carts")
    registry = request.registry
    settings = registry.settings
    expire_time = int(settings['altair_cart.expire_time'])

    carts_to_skip = set()
    count = 0 # 処理数カウンタ

    logger.debug("trace into loop")
    while True:
        logger.debug("trace in the loop")
        now = datetime.now()
        # 期限切れカート取得 1件ずつ処理
        cart_q = Cart.query.filter(
            Cart.created_at < now - timedelta(minutes=expire_time)
        ).filter(
            Cart.finished_at == None
        ).filter(
            Cart.deleted_at == None
        )
        if carts_to_skip:
            cart_q = cart_q.filter(not_(Cart.id.in_(carts_to_skip)))
        logger.debug("remains %d carts" % cart_q.count())
        cart = cart_q.first()

        if cart is None:
            logger.info('not found unfinished cart')
            break

        cart_id = cart.id
        logger.info("begin releasing cart (id=%d)" % (cart_id))
        if not cart.release():
            logging.warning('failed to release cart (id=%d). transaction will be aborted shortly' % cart_id)
            transaction.abort()
            carts_to_skip.add(cart_id)
            continue

        logger.info("released cart (id=%d)" % (cart_id))
        cart.finished_at = now
        transaction.commit()
        logger.info("commited released cart (id=%d)" % (cart_id))
        count += 1

        # logging.info('verifying if the cart in question (id=%d) still exists' % cart_id)
        # cart = m.Cart.query.filter_by(id=cart_id).first()
        # if cart is None:
        #     logging.info('cart (id=%d) IS GONE FOR SOME REASONS. SIGH.')
        #     continue
    return count


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('config')
    args = parser.parse_args()

    setup_logging(args.config)
    env = bootstrap(args.config)
    request = env['request']

    logger.info("start release cart")
    count = release_carts(request)
    logger.info("proccessed %s cart(s)" % count)
    logger.info("end release cart")
