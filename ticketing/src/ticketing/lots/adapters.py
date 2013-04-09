# -*- coding:utf-8 -*-

from sqlalchemy import sql
from webhelpers.containers import correlate_objects
from .models import (
    LotEntry,
    LotEntryWish,
    LotElectWork,
    LotElectedEntry,
)

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
