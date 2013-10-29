# -*- coding:utf-8 -*-


""" mqワーカー
"""
import transaction
import logging
from altair import multicheckout
from altair.mq.decorators import task_config
from altair.sqlahelper import named_transaction

logger = logging.getLogger(__name__)

def includeme(config):
    config.include('altair.sqlahelper')
    config.include('.setup_components')
    config.include('.import_mail_module')
    config.include('altair.app.ticketing.qr')
    config.include('altair.app.ticketing.users')
    config.include('altair.app.ticketing.organization_settings')
    config.include('altair.app.ticketing.checkout')
    config.include('altair.app.ticketing.multicheckout')
    config.include('altair.app.ticketing.payments')
    config.include('altair.app.ticketing.payments.plugins')
    config.add_subscriber('altair.app.ticketing.payments.events.cancel_on_delivery_error',
                          'altair.app.ticketing.payments.events.DeliveryErrorEvent')
    config.set_cart_getter('.api.get_cart_safe')

    config.include('.setup_mq')
    config.scan('.workers')

class WorkerResource(object):
    def __init__(self, message):
        self.message = message
        self.request = message.request

    @property
    def cart_id(self):
        return self.message.params.get('cart_id')

@task_config(root_factory=WorkerResource, consumer="cart", queue="cart")
@multicheckout.multicheckout_session
def cart_release(context, message):
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
