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

@implementer(IPaymentCart)
class LotWishCart(object):
    has_different_account = True  ## 差額(オーソリ時と売上確定処理で差額がある場合にTrue)

    def __init__(self, lot_wish):
        self.lot_wish = lot_wish

    @property
    def performance(self):
        return None

    @property
    def sales_segment(self):
        return None

    @property
    def payment_delivery_pair(self):
        return None

    @property
    def order_no(self):
        return None

    @property
    def total_amount(self):
        return None

    def finish(self):
        """ finish cart lifecycle"""

    @property
    def different_account(self):
        return 0

@task_config(root_factory=WorkerResource)
def elect_lots_task(context, message):
    """ 当選確定処理 """
    

    lot = context.lot
    if lot is None:
        logger.warning("lot is not found: lot_id = {0}".format(context.lot_id))
        return

    logger.info('start electing task: lot_id = {0}'.format(lot.id))

    wishes = lot.get_elected_wishes()

    for wish in wishes:
        cart = LotWishCart(wish)
        try:
            # payment_plugin 売上確定など
            # delivery_plugin
            # 在庫処理
            payment = Payment(cart)
            payment.call_payment()
        except Exception as e:
            logger.warning('lot_id, order_no, wish_no, wish_id')
            # 売上確定などできないものは別にまわす

        # ここでいったんトランザクション
    
        transaction.commit()
