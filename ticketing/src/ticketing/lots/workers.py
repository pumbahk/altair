# -*- coding:utf-8 -*-


""" mqワーカー
"""

import logging
import transaction
from ticketing.payments.payment import Payment
from altair.mq.decorators import task_config
from ticketing.cart.models import Cart, CartedProduct
from ticketing.cart.stocker import Stocker
from pyramid.interfaces import IRequest
from ticketing.cart.interfaces import (
    IStocker, IReserving, ICartFactory,
)
from ticketing.cart.reserving import Reserving
from ticketing.cart.carting import CartFactory

from .models import Lot, LotElectWork

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

    reg = config.registry
    reg.adapters.register([IRequest], IStocker, "", Stocker)
    reg.adapters.register([IRequest], IReserving, "", Reserving)
    reg.adapters.register([IRequest], ICartFactory, "", CartFactory)
    config.scan(".workers")


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
        self.request = message.request

    @property
    def lot_id(self):
        lot_id = self.message.params.get('lot_id')
        return lot_id

    @property
    def lot(self):
        return Lot.query.filter(Lot.id==self.lot_id).first()

    @property
    def work(self):
        entry_no = self.message.params.get('entry_no')
        wish_order = self.message.params.get('wish_order')
        logger.debug("{entry_no}-{wish_order}".format(entry_no=entry_no,
                                                      wish_order=wish_order))
        return LotElectWork.query.filter(
            LotElectWork.lot_entry_no==entry_no
        ).filter(
            LotElectWork.wish_order==wish_order
        ).one()

def dummy_task(context, message):
    logger.info("got message")
    try:
        print message.params
    except Exception as e:
        print e

@task_config(root_factory=WorkerResource,
             queue="lots")
def elect_lots_task(context, message):
    """ 当選確定処理 """

    try:
        lot = context.lot
        work = context.work
    except Exception as e:
        logger.exception(e)
        # workにエラー記録
        return


    logger.info("start electing lot_id = {lot_id}".format(lot_id=lot.id))
    if lot is None:
        logger.warning("lot is not found: lot_id = {0}".format(context.lot_id))
        return

    logger.info('start electing task: lot_id = {0}'.format(lot.id))
    request = context.request
    wish = work.wish
    order = elect_lot_wish(request, wish)
    if order:
        logger.info("ordered: order_no = {0.order_no}".format(order))
        work.delete()
    transaction.commit()


def elect_lot_wish(request, wish):
    cart = lot_wish_cart(wish)
    payment = Payment(cart, request)
    stocker = Stocker(request)
    try:
        # 在庫処理
        performance = cart.performance
        product_requires = [(p.product, p.quantity)
                            for p in cart.products]
        stocked = stocker.take_stock(performance.id,
                                     product_requires)
        logger.debug("lot elected: entry_no = {0}, stocks = {1}".format(wish.lot_entry.entry_no, stocked))
        # TODO: 確保数確認
        wish.lot_entry.elect(wish)
        order = payment.call_payment()
        wish.order_id = order.id

        return order

    except Exception as e:
        logger.exception(e)

    

    # def elect_lot_entries(self):
    #     """ 抽選申し込み確定
    #     申し込み番号と希望順で、当選確定処理を行う
    #     ワークに入っているものから当選処理をする
    #     それ以外を落選処理にする
    #     """

    #     elected_wishes = self.lot.get_elected_wishes()

    #     for ew in elected_wishes:
    #         ew.entry.elect(ew)

    #     # 落選処理
    #     rejected_wishes = self.lot.get_rejected_wishes()

    #     for rw in rejected_wishes:
    #         rw.entry.reject()

    #     self.lot.finish_lotting()
