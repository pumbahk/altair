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

        elected_wishes = self.lot.get_elected_wishes()

        for ew in elected_wishes:
            ew.entry.elect(ew)

        # 落選処理
        rejected_wishes = self.lot.get_rejected_wishes()
    
        for rw in rejected_wishes:
            rw.entry.reject()
    
        self.lot.finish_lotting()
