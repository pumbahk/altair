# -*- coding:utf-8 -*-


""" mqワーカー
"""
import transaction
import logging
from ticketing.payments.payment import Payment
from altair.mq.decorators import task_config
from ticketing.cart.models import Cart, CartedProduct
from ticketing.cart.stocker import Stocker
from pyramid.interfaces import IRequest
from ticketing.cart.interfaces import (
    IStocker, IReserving, ICartFactory,
)
from ticketing.models import DBSession
from ticketing.cart.reserving import Reserving
from ticketing.cart.carting import CartFactory
from ticketing import multicheckout
from .events import LotElectedEvent

from .models import Lot, LotElectWork, LotEntryWish

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
    config.include(".sendmail")

    reg = config.registry
    reg.adapters.register([IRequest], IStocker, "", Stocker)
    reg.adapters.register([IRequest], IReserving, "", Reserving)
    reg.adapters.register([IRequest], ICartFactory, "", CartFactory)
    config.scan(".workers")
    #config.scan(".subscribers")


def lot_wish_cart(wish):
    cart = Cart(performance=wish.performance,
                shipping_address=wish.lot_entry.shipping_address,
                payment_delivery_pair=wish.lot_entry.payment_delivery_method_pair,
                _order_no=wish.lot_entry.entry_no,
                sales_segment=wish.lot_entry.lot.sales_segment,
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
@multicheckout.multicheckout_session
def elect_lots_task(context, message):
    """ 当選確定処理 """
    DBSession.remove()
    try:
        lot = context.lot
        work = context.work
    except Exception as e:
        logger.exception(e)
        # workにエラー記録
        return
    work_id = work.id

    logger.info("start electing lot_id = {lot_id}".format(lot_id=lot.id))
    if lot is None:
        logger.warning("lot is not found: lot_id = {0}".format(context.lot_id))
        return

    logger.info('start electing task: lot_id = {0}'.format(lot.id))
    request = context.request
    ## XXX: ワーカーがシングルスレッドなので使えるが...
    request.session['order'] = {'order_no': work.lot_entry_no}
    request.altair_checkout3d_override_shop_name = lot.event.organization.setting.multicheckout_shop_name
    wish = work.wish
    wish_id = wish.id
    if wish.lot_entry.order:
        lot_entry = wish.lot_entry
        logger.warning("lot entry {0} is already ordered.".format(lot_entry.entry_no))
        return
    try:
        order = elect_lot_wish(request, wish)
        if order:
            logger.info("ordered: order_no = {0.order_no}".format(order))
            # トランザクション分離のため、再ロード
            wish = LotEntryWish.query.filter(LotEntryWish.id==wish_id).one()
            work.delete()

            wish.lot_entry.elect(wish)
            wish.order_id = order.id
            wish.lot_entry.order_id = order.id
            wish = LotEntryWish.query.filter(LotEntryWish.id==wish_id).one()
            event = LotElectedEvent(request, wish)
            request.registry.notify(event)


    except Exception as e:
        transaction.abort()
        work = LotElectWork.query.filter(LotElectWork.id==work_id).first()
        work.error = str(e).decode('utf-8')
        logger.error(work.error)
        transaction.commit()
        raise
    finally:
        pass

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
        order = payment.call_payment()

        return order

    except Exception as e:
        logger.exception(e)
