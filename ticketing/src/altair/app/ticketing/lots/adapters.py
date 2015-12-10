# -*- coding:utf-8 -*-
import logging
from pyramid.decorator import reify
from sqlalchemy import sql
from datetime import datetime, timedelta
from webhelpers.containers import correlate_objects
from altair.app.ticketing.models import (
    DBSession,
    )
from altair.app.ticketing.core.models import (
    Performance,
    StockType,
    Product,
    PaymentDeliveryMethodPair,
    )
from altair.app.ticketing.core.interfaces import (
    IOrderLike,
    IShippingAddress,
    )
from altair.app.ticketing.orders.models import (
    Order,
    )
from .models import (
    LotEntry,
    LotEntryWish,
    LotElectWork,
    LotElectedEntry,
    LotEntryProduct,
    )
from zope.interface import implementer
from altair.app.ticketing.payments.interfaces import IPaymentCart

logger = logging.getLogger(__name__)


@implementer(IOrderLike)
class LotEntryCart(object):
    def __init__(self, entry):
        self.entry = entry

    @property
    def cart_setting(self):
        return self.entry.cart_setting

    @property
    def attributes(self):
        return self.entry.attributes

    @property
    def sales_segment(self):
        return self.entry.lot.sales_segment

    @property
    def payment_delivery_pair(self):
        return self.entry.payment_delivery_method_pair

    @property
    def order_no(self):
        return self.entry.entry_no

    @property
    def total_amount(self):
        # オーソリ時は申し込みの最大金額を使う
        return self.entry.max_amount

    @property
    def name(self):
        return "LOT" + str(self.entry.lot.id)

    @property
    def user_point_accounts(self):
        return []


@implementer(IShippingAddress)
class LotSessionShippingAddress(object):
    def __init__(self, dict):
        self.dict = dict

    @property
    def user_id(self):
        return self.dict['user_id']

    @property
    def tel_1(self):
        return self.dict['tel_1']

    @property
    def tel_2(self):
        return self.dict['tel_2']

    @property
    def first_name(self):
        return self.dict['first_name']

    @property
    def last_name(self):
        return self.dict['last_name']

    @property
    def first_name_kana(self):
        return self.dict['first_name_kana']

    @property
    def last_name_kana(self):
        return self.dict['last_name_kana']

    @property
    def zip(self):
        return self.dict['zip']

    @property
    def email_1(self):
        return self.dict['email_1']

    @property
    def email_2(self):
        return self.dict['email_2']

    @property
    def email(self):
        return self.email_1 or self.email_2

@implementer(IPaymentCart)
class LotSessionCart(object):
    def __init__(self, entry_dict, request, lot):
        self.entry_no = entry_dict['entry_no']
        self.wishes = entry_dict['wishes']
        self.payment_delivery_method_pair_id = entry_dict['payment_delivery_method_pair_id']
        self.shipping_address_dict=entry_dict['shipping_address']
        self.gender = entry_dict['gender']
        self.birthday = entry_dict['birthday']
        self.memo = entry_dict['memo']
        self.extra = entry_dict.get('extra', [])
        self.request = request
        self.lot = lot
        self._product_cache = {}
        self.now = datetime.now()
        logger.debug("LotSessionCart(entry_no={0.entry_no})".format(self))

    @property
    def organization_id(self):
        return self.lot.organization_id

    @property
    def sales_segment(self):
        return self.lot.sales_segment

    @property
    def payment_delivery_pair(self):
        return PaymentDeliveryMethodPair.query.filter(
            PaymentDeliveryMethodPair.id==self.payment_delivery_method_pair_id
        ).first()

    @property
    def shipping_address(self):
        return LotSessionShippingAddress(self.shipping_address_dict)

    @property
    def order_no(self):
        return self.entry_no

    def _p(self, product_id):
        product = self._product_cache.get(product_id)
        if product is None:
            product = self._product_cache[product_id] = Product.query.filter(Product.id==product_id).one()
        return product

    @property
    def total_amount(self):
        # オーソリ時は申し込みの最大金額を使う
        return max(
            self.sales_segment.get_amount(
                self.payment_delivery_pair,
                [
                    (product, product.price, quantity)
                    for product, quantity in (
                        (self._p(wp['product_id']), wp['quantity'])
                        for wp in wish['wished_products']
                        )
                    ]
                )
            for wish in self.wishes
            )

    @property
    def delivery_fee(self):
        # オーソリ時は申し込みの最大金額を使う
        return max(
            self.sales_segment.get_delivery_fee(
                self.payment_delivery_pair,
                [
                    (product, quantity)
                    for product, quantity in (
                        (self._p(wp['product_id']), wp['quantity'])
                        for wp in wish['wished_products']
                        )
                    ]
                )
            for wish in self.wishes
            )

    @property
    def transaction_fee(self):
        # オーソリ時は申し込みの最大金額を使う
        return max(
            self.sales_segment.get_transaction_fee(
                self.payment_delivery_pair,
                [
                    (product, quantity)
                    for product, quantity in (
                        (self._p(wp['product_id']), wp['quantity'])
                        for wp in wish['wished_products']
                        )
                    ]
                )
            for wish in self.wishes
            )

    @property
    def system_fee(self):
        # オーソリ時は申し込みの最大金額を使う
        return max(
            self.sales_segment.get_system_fee(
                self.payment_delivery_pair,
                [
                    (product, quantity)
                    for product, quantity in (
                        (self._p(wp['product_id']), wp['quantity'])
                        for wp in wish['wished_products']
                        )
                    ]
                )
            for wish in self.wishes
            )

    @property
    def special_fee(self):
        # オーソリ時は申し込みの最大金額を使う
        return max(
            self.sales_segment.get_special_fee(
                self.payment_delivery_pair,
                [
                    (product, quantity)
                    for product, quantity in (
                        (self._p(wp['product_id']), wp['quantity'])
                        for wp in wish['wished_products']
                        )
                    ]
                )
            for wish in self.wishes
            )

    @property
    def name(self):
        return "LOT" + str(self.lot.id)

    @property
    def issuing_start_at(self):
        # オーソリの際にしか使われないのでこれは None でよい
        return None

    @property
    def issuing_end_at(self):
        # オーソリの際にしか使われないのでこれは None でよい
        return None

    @property
    def payment_start_at(self):
        return self.sales_segment.start_at

    @property
    def payment_due_at(self):
        payment_period_days = self.payment_delivery_pair.payment_period_days
        if payment_period_days is not None and self.lot.lotting_announce_datetime is not None:
            payment_due_at = self.lot.lotting_announce_datetime + timedelta(days=payment_period_days)
            payment_due_at = payment_due_at.replace(hour=23, minute=59, second=59)
        else:
            payment_due_at = self.now.replace(hour=23, minute=59, second=59) + timedelta(days=365)
        return payment_due_at

    @property
    def items(self):
        # 決済時は商品も券面も決まっていないので、空のリストを返せばよいはず...
        return []

    @property
    def user_point_accounts(self):
        return []


class LotEntryStatus(object):
    def __init__(self, lot, request=None):
        self.lot = lot
        self.request = request # いらない

    @property
    def performances(self):
        return correlate_objects(self.lot.performances, 'id')

    @property
    def entries(self):
        return self.lot.entries

    @property
    def sub_counts(self):
        sub_counts = [dict(performance=self.performances[r[1]],
                           wish_order=r[2] + 1,
                           count=r[0])
                      for r in sql.select([sql.func.count(LotEntryWish.id), LotEntryWish.performance_id, LotEntryWish.wish_order]
                                          ).where(sql.and_(LotEntryWish.lot_entry_id==LotEntry.id,
                                                           LotEntryWish.deleted_at==None,
                                                           LotEntry.lot_id==self.lot.id,
                                                           LotEntry.canceled_at==None,
                                                           LotEntry.entry_no!=None,
                                                           LotEntry.deleted_at==None
                                                           )
                                                  ).group_by(LotEntryWish.performance_id, LotEntryWish.wish_order
                                                             ).execute()]
        return sub_counts

    @property
    def total_entries(self):
        """ 申込件数 """
        total_entries = LotEntry.query.filter(
            LotEntry.lot_id==self.lot.id
        ).filter(
            LotEntry.canceled_at==None
        ).filter(
            LotEntry.withdrawn_at==None
        ).filter(
            LotEntry.entry_no!=None
        ).count()
        return total_entries

    @property
    def electing_count(self):
        electing_count = LotElectWork.query.filter(
            LotElectWork.lot_id==self.lot.id
        ).count()

        return electing_count

    @property
    def elected_count(self):
        """ 当選件数 当選フラグON """

        elected_count = LotElectedEntry.query.filter(
            LotElectedEntry.lot_entry_id==LotEntry.id
        ).filter(
            LotEntry.lot_id==self.lot.id
        ).filter(
            LotEntry.canceled_at==None
        ).filter(
            LotEntry.entry_no!=None
        ).filter(
            LotEntry.elected_at!=None
        ).count()

        return elected_count

    @property
    def ordered_count(self):
        """ 決済件数 注文があって決済済みのもの"""

        ordered_count = LotElectedEntry.query.filter(
            LotElectedEntry.lot_entry_id==LotEntry.id
        ).filter(
            LotEntry.lot_id==self.lot.id
        ).filter(
            LotEntry.canceled_at==None
        ).filter(
            LotEntry.entry_no != None
        ).filter(
            LotEntry.order_id != None
        ).count()
        return ordered_count

    @property
    def canceled_count(self):
        """ キャンセル件数 キャンセル済みの注文を持っているもの"""

        canceled_count = LotElectedEntry.query.filter(
            LotElectedEntry.lot_entry_id==LotEntry.id
        ).filter(
            LotEntry.lot_id==self.lot.id
        ).filter(
            LotEntry.canceled_at==None
        ).filter(
            LotEntry.canceled_at==None
        ).filter(
            LotEntry.entry_no != None
        ).filter(
            Order.id==LotEntry.order_id
        ).filter(
            Order.canceled_at!=None
        ).count()
        return canceled_count

    @property
    def reserved_count(self):
        """ 予約件数 注文があって未決済のもの """
        reserved_count = LotElectedEntry.query.filter(
            LotElectedEntry.lot_entry_id==LotEntry.id
        ).filter(
            LotEntry.lot_id==self.lot.id
        ).filter(
            LotEntry.canceled_at==None
        ).filter(
            LotEntry.order_id==Order.id
        ).filter(
            LotEntry.entry_no != None
        ).filter(
            Order.id==LotEntry.order_id
        ).filter(
            Order.paid_at==None
        ).count()
        return reserved_count

    @property
    def total_quantity(self):
        total_quantity = DBSession.query(
            sql.func.sum(LotEntryProduct.quantity)
        ).filter(
            LotEntryProduct.lot_wish_id==LotEntryWish.id
        ).filter(
            LotEntryWish.lot_entry_id==LotEntry.id
        ).filter(
            LotEntry.lot_id==self.lot.id
        ).filter(
            LotEntry.canceled_at==None
        ).filter(
            LotEntry.withdrawn_at==None
        ).filter(
            LotEntry.entry_no != None
        ).scalar()
        return total_quantity

    ## 希望ごとの情報
    @reify
    def wish_statuses(self):
        wishes = DBSession.query(
            LotEntryWish.wish_order,
            sql.func.sum(LotEntryProduct.quantity)
        ).filter(
            LotEntryProduct.lot_wish_id==LotEntryWish.id
        ).filter(
            LotEntryWish.lot_entry_id==LotEntry.id
        ).filter(
            LotEntry.lot_id==self.lot.id
        ).filter(
            LotEntry.canceled_at==None
        ).filter(
            LotEntry.withdrawn_at==None
        ).filter(
            LotEntry.entry_no != None
        ).group_by(LotEntryWish.wish_order).all()
        results = {}
        for wish_order, quantity in wishes:
            results[wish_order] = LotEntryWishStatus(wish_order, quantity)

        # 穴埋め
        for i in range(self.lot.limit_wishes):
            if i in results:
                continue
            results[i] = LotEntryWishStatus(i, 0)

        return results

    ## 公演・席種ごとの情報
    @reify
    def performance_seat_type_statuses(self):

        from sqlalchemy.sql.expression import case, and_

        inner = DBSession.query(
            Performance.id.label('performance_id'),
            StockType.id.label('stock_type_id'),
            LotEntryWish.wish_order.label('wish_order'),
            case([
                (LotEntry.withdrawn_at == None,
                 LotEntryProduct.quantity)
            ],
            else_=0).label('entry_quantity'),
            case([
                (and_(LotEntry.elected_at != None,
                      LotEntryWish.elected_at != None),
                 LotEntryProduct.quantity)
            ],
            else_=0).label('elected_quantity'),
            case([
                (and_(LotEntry.order_id != None, Order.paid_at != None,
                      LotEntryWish.elected_at != None),
                 LotEntryProduct.quantity)
            ],
            else_=0).label('ordered_quantity'),
            case([
                (and_(LotEntry.order_id != None, Order.paid_at == None,
                      LotEntryWish.elected_at != None),
                 LotEntryProduct.quantity)
            ],
            else_=0).label('reserved_quantity'),
            case([
                (and_(LotEntry.order_id != None, Order.canceled_at != None,
                      LotEntryWish.elected_at != None),
                 LotEntryProduct.quantity)
            ],
            else_=0).label('canceled_quantity'),
        ).join(
            Product,
            Product.performance_id==Performance.id
        ).join(
            StockType,
            StockType.id==Product.seat_stock_type_id
        ).join(
            LotEntryProduct,
            LotEntryProduct.product_id==Product.id
        ).join(
            LotEntryWish,
            LotEntryWish.id==LotEntryProduct.lot_wish_id
        ).join(
            LotEntry,
            LotEntry.id==LotEntryWish.lot_entry_id
        ).outerjoin(Order, Order.id==LotEntry.order_id
        ).filter(
            LotEntry.lot_id==self.lot.id
        ).filter(
            LotEntry.canceled_at==None
        ).filter(
            LotEntry.entry_no != None
        ).subquery()

        results = DBSession.query(
            Performance,
            StockType,
            sql.func.sum(inner.c.entry_quantity),
            sql.func.sum(inner.c.elected_quantity),
            sql.func.sum(inner.c.ordered_quantity),
            sql.func.sum(inner.c.reserved_quantity),
            sql.func.sum(inner.c.canceled_quantity),
        ).filter(
            inner.c.performance_id==Performance.id
        ).filter(
            inner.c.stock_type_id==StockType.id
        ).group_by(inner.c.performance_id, inner.c.stock_type_id).all()

        wishes_results = DBSession.query(
            Performance,
            StockType,
            inner.c.wish_order,
            sql.func.sum(inner.c.entry_quantity),
        ).filter(
            inner.c.performance_id==Performance.id
        ).filter(
            inner.c.stock_type_id==StockType.id
        ).group_by(
            inner.c.performance_id, inner.c.stock_type_id, inner.c.wish_order
        ).all()

        wishes_statuses = [LotEntryPerformanceSeatTypesWishStatus(performance,
                                                                  stock_type,
                                                                  wish_order,
                                                                  entry_quantity)
                           for (performance, stock_type, wish_order,entry_quantity)
                           in wishes_results]


        wishes_statuses_ = {}
        for w in wishes_statuses:
            ww = wishes_statuses_.get(w.performance_seat_type, {})
            ww[w.wish_order] = w
            wishes_statuses_[w.performance_seat_type] = ww

        for (performance, stock_type), ww in wishes_statuses_.items():
            for i in range(self.lot.limit_wishes):
                if i in ww:
                    continue
                ww[i] = LotEntryPerformanceSeatTypesWishStatus(performance,
                                                               stock_type,
                                                               i, 0)

        return [LotEntryPerformanceSeatTypeStatus(performance,
                                                  stock_type,
                                                  entry_quantity,
                                                  elected_quantity,
                                                  ordered_quantity,
                                                  reserved_quantity,
                                                  canceled_quantity,
                                                  wishes_statuses_[(performance, stock_type)],
                                              )
                for (performance, stock_type, entry_quantity, elected_quantity, ordered_quantity,
                     reserved_quantity, canceled_quantity) in results]

class LotEntryWishStatus(object):
    def __init__(self, wish_order, quantity):
        self.wish_order = wish_order
        self.quantity = quantity

class LotEntryPerformanceSeatTypeStatus(object):
    def __init__(self, performance, seat_type,
                 entry_quantity, elected_quantity,
                 ordered_quantity,
                 reserved_quantity,
                 canceled_quantity,
                 wish_statuses):
         self.performance = performance
         self.seat_type = seat_type
         self.entry_quantity = entry_quantity
         self.elected_quantity = elected_quantity
         self.ordered_quantity = ordered_quantity
         self.reserved_quantity = reserved_quantity
         self.canceled_quantity = canceled_quantity
         self.wish_statuses = wish_statuses

class LotEntryPerformanceSeatTypesWishStatus(object):
    """ """

    def __init__(self, performance, seat_type, wish_order, entry_quantity):
        self.performance = performance
        self.seat_type = seat_type
        self.entry_quantity = entry_quantity
        self.wish_order = wish_order

        self.performance_seat_type = (performance, seat_type)

class LotEntryController(object):
    def __init__(self, request=None):
        self._request = request
        self._entry = None

    def load(self, obj_or_id):
        if isinstance(obj_or_id, LotEntry):
            self._entry = obj_or_id
        else:
            try:
                obj_or_id = int(obj_or_id)
            except (ValueError, TypeError) as err:
                raise ValueError(err)

            self._entry = LotEntry.query.filter(LotEntry.id == obj_or_id).one()

        return self._entry

    @property
    def lot(self):
        return self._entry and self._entry.lot

    def can_withdraw(self, now):
        """
        抽選申込がwithdrawできる状態かどうかを判定する
        当落が確定しておらず受付期間中の抽選申込のみ取消できる
        """
        return (
            self.lot.available_on(now) and
            self.lot.lot_entry_user_withdraw and
            not self._entry.is_elected and
            not self._entry.is_rejected and
            not self._entry.is_canceled and
            not self._entry.is_withdrawn and
            not self._entry.is_ordered
        )
