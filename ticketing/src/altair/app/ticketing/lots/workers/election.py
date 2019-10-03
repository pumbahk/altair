# -*- coding:utf-8 -*-


""" mqワーカー
"""
import transaction
import logging
from pyramid.decorator import reify
from altair.app.ticketing.core.models import SalesSegment
from altair.app.ticketing.payments.payment import Payment
from altair.mq.decorators import task_config
from altair.sqlahelper import named_transaction

from altair.app.ticketing.models import DBSession

from altair.app.ticketing.orders import models as order_models
from altair.app.ticketing.cart import models as cart_models
from altair.app.ticketing.core import models as core_models
from altair.app.ticketing.cart import api as cart_api

from .. import models as lot_models
from ..events import LotElectedEvent
from altair.app.ticketing.lots.models import (
    Lot
)

from altair.app.ticketing.payments.api import (
    is_finished_payment,
    is_finished_delivery,
)

logger = logging.getLogger(__name__)

def lot_wish_cart(wish):
    event = wish.performance.event
    organization = event.organization
    organization_id = organization.id
    cart_setting_id = (event.setting and event.setting.cart_setting_id) or organization.setting.cart_setting_id
    sales_segment_group_id = wish.lot_entry.lot.sales_segment.sales_segment_group_id
    sales_segment = SalesSegment.query.filter(SalesSegment.performance_id == wish.performance_id)\
        .filter(SalesSegment.sales_segment_group_id == sales_segment_group_id).first()
    cart = cart_models.Cart(
        performance=wish.performance,
        organization_id=organization_id,
        cart_setting_id=cart_setting_id,
        shipping_address=wish.lot_entry.shipping_address,
        payment_delivery_pair=wish.lot_entry.payment_delivery_method_pair,
        _order_no=wish.lot_entry.entry_no,
        sales_segment=sales_segment,
        channel=wish.lot_entry.channel,
        membership_id=wish.lot_entry.membership_id,
        user_point_accounts=wish.lot_entry.user_point_accounts,
        products=[
            cart_models.CartedProduct(
                product=p.product,
                organization_id=organization_id,
                quantity=p.quantity,
                items=[
                    cart_models.CartedProductItem(
                        organization_id=organization_id,
                        quantity=p.quantity * ordered_product_item.quantity,
                        product_item=ordered_product_item
                        )
                    for ordered_product_item in p.product.items
                    ]
                )
            for p in wish.products
            ]
        )
    return cart

# 当選処理
class ElectionWorkerResource(object):
    def __init__(self, request):
        self.request = request
        self.lot_id = self.request.params.get('lot_id')
        self.entry_no = self.request.params.get('entry_no')
        self.wish_order = self.request.params.get('wish_order')
        logger.debug("{entry_no}-{wish_order}".format(entry_no=self.entry_no, wish_order=self.wish_order))

    @reify
    def lot(self):
        return lot_models.Lot.query.filter(lot_models.Lot.id==self.lot_id).first()

    @reify
    def work(self):
        return lot_models.LotElectWork.query.filter(
            lot_models.LotElectWork.lot_entry_no == self.entry_no
        ).filter(
            lot_models.LotElectWork.wish_order == self.wish_order
        ).first()


def elect_lot_wish(request, wish, order=None):
    from altair.app.ticketing.models import DBSession
    stocker = cart_api.get_stocker(request, DBSession)

    if order is None:
        order = order_models.Order.query.filter(order_models.Order.order_no==wish.lot_entry.entry_no).first()

    # 在庫処理
    if order is None:
        cart = lot_wish_cart(wish)
        payment = Payment(cart, request, cancel_payment_on_failure=False)
        lot_entry_lock = request.params.get('lot_entry_lock')
        if not lot_entry_lock:
            performance = cart.performance
            product_requires = [(p.product, p.quantity) for p in cart.items]
            stocked = stocker.take_stock(performance.id, product_requires)
        order = payment.call_payment()
        order.user_point_accounts = cart.user_point_accounts
        order.attributes = wish.lot_entry.attributes
        order.cart_setting = wish.lot_entry.cart_setting

    else:
        pdmp = wish.lot_entry.payment_delivery_method_pair
        payment_finished = is_finished_payment(request, pdmp, order)
        delivery_finished = is_finished_delivery(request, pdmp, order)

        if payment_finished and delivery_finished:
            logger.warning("lot entry {0} is already ordered.".format(wish.lot_entry.entry_no))
        elif payment_finished and not delivery_finished:
            payment = Payment(order.cart, request)
            payment.call_delivery(order)
        else:
            # 決済エラーでOrderが残ることはない
            logger.error("lot entry {0} cannot elect. please recover payment status.".format(wish.lot_entry.entry_no))
    # TODO: 確保数確認

    return order

def get_updated_orion_ticket_phone(entry_no):
    orion_ticket_phone = core_models.OrionTicketPhone.filter_by(entry_no=entry_no).first()
    if orion_ticket_phone:
        orion_ticket_phone.order_no = entry_no
    return orion_ticket_phone

@task_config(root_factory=ElectionWorkerResource,
             name="lots.election",
             consumer="lots.election",
             queue="lots.election",
             timeout=600)
def elect_lots_task(context, request):
    with named_transaction(request, "lot_work_history") as s:
        if not context.work:
            logger.info("nothing electing task: lot_id={lot_id}, entry_no={entry_no}".format(lot_id=context.lot.id, entry_no=context.entry_no))
            return

        history = lot_models.LotWorkHistory(
            lot_id=context.lot.id, # 別トランザクションなのでID指定
            entry_no=context.work.lot_entry_no,
            wish_order=context.work.wish_order
            )
        s.add(history)
        try:
            logger.info("start electing task: lot_id={lot_id}, work_id={work_id}".format(lot_id=context.lot.id, work_id=context.work.id))
            if context.lot is None:
                logger.warning("lot is not found: lot_id = {0}".format(context.lot_id))
                return

            request.session['order'] = {'order_no': context.work.lot_entry_no}
            wish = context.work.wish
            wish_id = wish.id

            order = wish.lot_entry.order
            order = elect_lot_wish(request, wish, order)
            if order:
                logger.info("ordered: order_no = {0.order_no}".format(order))
                orion_ticket_phone = get_updated_orion_ticket_phone(context.entry_no)
                if orion_ticket_phone:
                    DBSession.add(orion_ticket_phone)
                DBSession.delete(context.work)
                wish.lot_entry.elect(wish, request.params.get('lot_entry_lock'))
                wish.order_id = order.id
                wish.lot_entry.order_id = order.id
                wish.lot_entry.order = order
        except Exception as e:
            work = s.query(lot_models.LotElectWork).filter_by(id=context.work.id).one()
            history.error = work.error = str(e).decode('utf-8')
            raise
