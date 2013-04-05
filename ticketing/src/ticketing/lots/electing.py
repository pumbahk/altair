# -*- coding:utf-8 -*-
""" 当選落選
"""
from zope.interface import implementer
from ticketing.models import DBSession
from .models import (
    LotEntry, 
    LotEntryWish, 
    LotElectWork, 
    LotStatusEnum, 
    LotElectedEntry,
    LotRejectedEntry,
)
from .interfaces import IElecting

@implementer(IElecting)
class Electing(object):
    def __init__(self, lot, request):
        self.request = request
        self.lot = lot


    def elect_lot_entries(self):
        """ 抽選申し込み確定 
        申し込み番号と希望順で、当選確定処理を行う
        ワークに入っているものから当選処理をする
        それ以外を落選処理にする
        """

        elected_wishes = DBSession.query(LotEntryWish).filter(
            LotEntryWish.lot_entry_id==LotEntry.id
        ).filter(
            LotEntry.lot_id==self.lot.id
        ).filter(
            LotElectWork.lot_entry_no==LotEntry.entry_no
        ).filter(
            (LotElectWork.wish_order-1)==LotEntryWish.wish_order
        )
    
        for ew in elected_wishes:
            self.elect_entry(self.lot, ew)
            # TODO: 再選処理
    
    
    
        # 落選処理
        q = DBSession.query(LotEntry).filter(
            LotEntry.elected_at==None
        ).filter(
            LotEntry.rejected_at==None
        ).all()
    
        for entry in q:
            self.reject_entry(self.lot, entry)
    
        self.lot.status = int(LotStatusEnum.Elected)
        LotElectWork.query.filter(LotElectWork.lot_id==self.lot.id).delete()


    def reject_entry(self, lot, entry):
        now = datetime.now()
        entry.rejected_at = now
        rejected = LotRejectedEntry(lot_entry=entry)
        DBSession.add(rejected)
        return rejected
    
    def elect_entry(self, lot, elected_wish):
        """ 個々の希望申し込みに対する処理 
        :return: 当選情報
        """
        now = datetime.now()
        elected_wish.elected_at = now
        elected_wish.lot_entry.elected_at = now
        elected = LotElectedEntry(lot_entry=elected_wish.lot_entry,
            lot_entry_wish=elected_wish)
        DBSession.add(elected)
        return elected
    
