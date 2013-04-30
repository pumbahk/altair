# -*- coding:utf-8 -*-

from sqlalchemy import sql
from webhelpers.containers import correlate_objects
from .models import (
    LotEntry,
    LotEntryWish,
    LotElectWork,
    LotElectedEntry,
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
    """
    TODO
    #  メール送信済み
    #  決済済み
    """
    def __init__(self, lot, request):
        self.lot = lot
        self.request = request

    @property
    def performances(self):
        return correlate_objects(self.lot.performances, 'id')

    @property
    def entries(self):
        return self.lot.entries


    @property
    def total_entries(self):
        total_entries = LotEntry.query.filter(LotEntry.lot_id==self.lot.id).count()
        return total_entries

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
    def electing_count(self):
        electing_count = LotElectWork.query.filter(
            LotElectWork.lot_id==self.lot.id
        ).count()

        return electing_count

    @property
    def elected_count(self):
        elected_count = LotElectedEntry.query.filter(
            LotElectedEntry.lot_entry_id==LotEntry.id
        ).filter(LotEntry.lot_id==self.lot.id).count()
        return elected_count
