# -*- coding:utf-8 -*-


""" mqワーカー
"""
import transaction
import logging
from altair.app.ticketing.payments.payment import Payment
from altair.mq.decorators import task_config
from altair.sqlahelper import named_transaction
from altair.app.ticketing.cart.models import Cart, CartedProduct, CartedProductItem
from altair.app.ticketing.cart.stocker import Stocker
from pyramid.interfaces import IRequest
from altair import multicheckout
from altair.app.ticketing.cart.interfaces import (
    IStocker, IReserving, ICartFactory,
)
from altair.app.ticketing.models import DBSession
from altair.app.ticketing.core.models import Order
from altair.app.ticketing.cart.reserving import Reserving
from altair.app.ticketing.cart.carting import CartFactory
from .events import LotElectedEvent

from .models import Lot, LotElectWork, LotEntryWish, LotEntry, LotWorkHistory
from altair.app.ticketing.payments.api import (
    is_finished_payment,
    is_finished_delivery,
)

logger = logging.getLogger(__name__)

def on_delivery_error(event):
    import sys
    import traceback
    import StringIO

    e = event.exception
    order = event.order
    exc_info = sys.exc_info()
    out = StringIO.StringIO()
    traceback.print_exception(*exc_info, file=out)
    logger.error(out.getvalue())
    entry = LotEntry.query.filter(LotEntry.entry_no==order.order_no).first()
    order.note = str(e)
    if entry is not None:
        entry.order = order
    transaction.commit()


def includeme(config):
    # payment
    config.include('altair.app.ticketing.payments')
    config.include('altair.app.ticketing.payments.plugins')
    config.include('altair.app.ticketing.cart.setup_renderers')
    config.include(".sendmail")

    reg = config.registry
    reg.adapters.register([IRequest], IStocker, "", Stocker)
    reg.adapters.register([IRequest], IReserving, "", Reserving)
    reg.adapters.register([IRequest], ICartFactory, "", CartFactory)
    config.add_publisher_consumer('lots', 'altair.ticketing.lots.mq')
    config.add_subscriber('.workers.on_delivery_error',
                          'altair.app.ticketing.payments.events.DeliveryErrorEvent')
    #config.scan(".workers")
    #config.scan(".subscribers")


def lot_wish_cart(wish):
    organization_id = wish.performance.event.organization_id
    cart = Cart(performance=wish.performance,
                organization_id=organization_id,
                shipping_address=wish.lot_entry.shipping_address,
                payment_delivery_pair=wish.lot_entry.payment_delivery_method_pair,
                _order_no=wish.lot_entry.entry_no,
                sales_segment=wish.lot_entry.lot.sales_segment,
                products=[
                    CartedProduct(product=p.product,
                                  organization_id=organization_id,
                                  quantity=p.quantity,
                                  items=[
                                      CartedProductItem(
                                          organization_id=organization_id,
                                          quantity=p.quantity * ordered_product_item.quantity,
                                          product_item=ordered_product_item)
                                      for ordered_product_item in p.product.items
                                  ])
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
             consumer="lots",
             queue="lots")
@multicheckout.multicheckout_session
def elect_lots_task(context, message):
    DBSession.remove()
    try:
        lot = context.lot
        work = context.work
    except Exception as e:
        logger.exception(e)
        # workにエラー記録
        return
    with named_transaction(context.request, "lot_work_history") as s:
        history = LotWorkHistory(lot_id=lot.id, # 別トランザクションなのでID指定
                                 entry_no=work.lot_entry_no,
                                 wish_order=work.wish_order)
        s.add(history)
        return _elect_lots_task(context, message, lot, work, history)

def _elect_lots_task(context, message, lot, work, history):
    """ 当選確定処理 """

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
    pdmp = wish.lot_entry.payment_delivery_method_pair

    order = wish.lot_entry.order
    if order:
        payment_finished = is_finished_payment(request, pdmp, order)
        delivery_finished = is_finished_delivery(request, pdmp, order)

        if payment_finished and delivery_finished:
            lot_entry = wish.lot_entry
            logger.warning("lot entry {0} is already ordered.".format(lot_entry.entry_no))
            event = LotElectedEvent(request, wish)
            request.registry.notify(event)
            return
    try:
        order = elect_lot_wish(request, wish, order)
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
        history.error = work.error = str(e).decode('utf-8')
        logger.error(work.error)
        transaction.commit()



def elect_lot_wish(request, wish, order=None):
    cart = lot_wish_cart(wish)
    payment = Payment(cart, request)
    stocker = Stocker(request)

    try:
        # 在庫処理
        performance = cart.performance
        product_requires = [(p.product, p.quantity)
                    for p in cart.items]
        if order is None:
            order = Order.query.filter(Order.order_no==wish.lot_entry.entry_no).first()
        if order is None:
            stocked = stocker.take_stock(performance.id,
                                         product_requires)
            order = payment.call_payment()

        else:
            payment.call_delivery(order)
        # TODO: 確保数確認

        return order

    except Exception as e:
        logger.exception(e)
        raise
