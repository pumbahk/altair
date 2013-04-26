# -*- coding:utf-8 -*-


""" mqワーカー
"""

import logging
import transaction
from .models import Lot
from zope.interface import implementer
from ticketing.payments.payment import Payment
from ticketing.payments.interfaces import IPaymentCart
from altair.mq.decorators import task_config
from ticketing.cart.models import Cart, CartedProduct
from ticketing.cart.stockeri import Stocker

logger = logging.getLogger(__name__)

def includeme(config):
    # payment
    config.include('ticketing.payments')
    # マルチ決済
    config.include('ticketing.payments.plugins.multicheckout')
    # QRコード
    config.include('ticketing.payments.plugins.qr')
    # 配送
    config.include('ticketing.payments.plugins.shipping')


def lot_wish_cart(wish):
    cart = Cart(performance=wish.performance,
                shipping_address=wish.lot_entry.shipping_address,
                payment_delivery_pair=wish.lot_entry.payment_delivery_method_pair,
                _order_no=wish.lot_entry.entry_no,
                sales_segment=wish.lot_entry.lot.sales_segment,
                system_fee=wish.lot_entry.lot.system_fee,
                products=[
                    CartedProduct(product=p.product,
                                  quantity=p.quantity)
                    for p in wish.products
                    ],
                )
    cart.has_different_amount = True
    cart.different_amount = wish.lot_entry.max_amount - wish.total_amount
    return cart

class WorkerResource(object):
    def __init__(self, message):
        self.message = message

    @property
    def lot_id(self):
        lot_id = self.message.params.get('lot_id')
        return lot_id

    @property
    def lot(self):
        return Lot.query.filter(Lot.id==self.lot_id).first()


@task_config(root_factory=WorkerResource)
def elect_lots_task(context, message):
    """ 当選確定処理 """
    

    lot = context.lot
    if lot is None:
        logger.warning("lot is not found: lot_id = {0}".format(context.lot_id))
        return

    logger.info('start electing task: lot_id = {0}'.format(lot.id))

    wishes = lot.get_elected_wishes()
    orders = []
    for wish in wishes:
        order = elect_lot_wish(wish)
        orders.append(order)

    return len(orders)

def elect_lot_wish(wish):
        cart = lot_wish_cart(wish)
        payment = Payment(cart)
        stocker = Stocker()
        try:
            # 在庫処理
            performance = cart.performance
            product_requires = [(p.product_id, p.quantity)
                                for p in cart.products]
            stocked = stocker.take_stock(performance,
                                         product_requires)
            # TODO: 確保数確認


            # payment_plugin 売上確定など
            # delivery_plugin
            order = payment.call_payment()
            wish.order = order
            return order

        except Exception as e:
            logger.warning('lot_id, order_no, wish_no, wish_id')
            # 売上確定などできないものは別にまわす

        # ここでいったんトランザクション
    
        transaction.commit()
