# -*- coding:utf-8 -*-
from pyramid.decorator import reify
from sqlalchemy import sql
from webhelpers.containers import correlate_objects
from ticketing.models import (
    DBSession,
)
from ticketing.core.models import (
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
from ticketing.payments.interfaces import IPaymentCart

@implementer(IPaymentCart)
class LotEntryCart(object):
    def __init__(self, entry):
        self.entry = entry

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


class LotEntryStatus(object):
    def __init__(self, lot, request):
        self.lot = lot
        self.request = request

    @property
    def performances(self):
        return correlate_objects(self.lot.performances, 'id')

    @property
    def entries(self):
        return self.lot.entries



    ## いらん
    @property
    def total_wishes(self):
        total_wishes = LotEntryWish.query.filter(
            LotEntry.lot_id==self.lot.id
        ).filter(
            LotEntryWish.lot_entry_id==LotEntry.id
        ).count()

        return total_wishes

    @property
    def sub_counts(self):
        sub_counts = [dict(performance=self.performances[r[1]],
                           wish_order=r[2] + 1,
                           count=r[0])
                      for r in sql.select([sql.func.count(LotEntryWish.id), LotEntryWish.performance_id, LotEntryWish.wish_order]
                                          ).where(sql.and_(LotEntryWish.lot_entry_id==LotEntry.id,
                                                           LotEntry.lot_id==self.lot.id)
                                                  ).group_by(LotEntryWish.performance_id, LotEntryWish.wish_order
                                                             ).execute()]
        return sub_counts

    @property
    def total_entries(self):
        """ 申込件数 """
        total_entries = LotEntry.query.filter(LotEntry.lot_id==self.lot.id).count()
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
            LotEntry.order_id==Order.id
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
            LotEntry.order_id==Order.id
        ).filter(
            Order.paid_at!=None
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


class LotEntryWishStatus(object):
    def __init__(self, wish_order, quantity):
        self.wish_order = wish_order
        self.quantity = quantity
