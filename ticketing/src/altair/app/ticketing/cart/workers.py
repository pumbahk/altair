# -*- coding:utf-8 -*-


""" mqワーカー
"""
import transaction
import logging
from altair.mq.decorators import task_config

logger = logging.getLogger(__name__)

class WorkerResource(object):
    def __init__(self, request):
        self.request = request

    @property
    def cart_id(self):
        return self.request.params.get('cart_id')

@task_config(root_factory=WorkerResource, name="cart", consumer="cart", queue="cart")
def cart_release(context, request):
    from .models import Cart
    from altair.app.ticketing.models import DBSession
    DBSession.remove()
    cart_id = context.cart_id
    try:
        cart = Cart.query.filter(Cart.id == cart_id).with_lockmode('update').first()
        if cart is not None:
            cart.release()
        transaction.commit()
    except Exception as e:
        logger.exception("oops")
        transaction.abort()
