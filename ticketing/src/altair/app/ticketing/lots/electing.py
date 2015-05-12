# -*- coding:utf-8 -*-
""" 当選落選

publisher呼び出しをticketing.events.lotsに置いて、こちらにはworkers内の実装をおいてしまうべきか？
"""
import logging
import json
from sqlalchemy import sql
from pyramid.decorator import reify
from zope.interface import implementer
from altair.mq import get_publisher
from .interfaces import IElecting
from altair.app.ticketing.models import (
    DBSession,
)

from altair.app.ticketing.core.models import (
    Performance,
    ProductItem,
    Product,
    Stock,
    StockStatus,
)
from altair.app.ticketing.lots.models import (
    LotEntry,
    LotEntryWish,
    LotEntryProduct,
    LotElectWork,
    LotRejectWork,
    LotRejectedEntry,
)

logger = logging.getLogger(__name__)

@implementer(IElecting)
class Electing(object):
    def __init__(self, lot, request):
        self.request = request
        self.lot = lot

    @reify
    def blockers(self):
        """ 当選処理を行えない理由 """
        blockers = []

        # 商品明細
        for p in self.check_product_items():
            blockers.append(u"{0.name} に商品明細がありません。".format(p))
        # 在庫
        for p in self.check_stock():
            blockers.append(u"{0.name} の在庫が不足しています。".format(p))

        return blockers

    def check_product_items(self):
        """ 所属する商品すべてが商品明細を持っているか"""

        for product in self.lot.products:
            if not product.items:
                yield product

    def check_stock(self):
        """ 当選予定の在庫数が現在個数以下になっているか"""
        for stock, stock_status, product_item, performance, quantity, count in self.required_stocks:
            if quantity > stock_status.quantity:
                yield product_item

    @reify
    def required_stocks(self):
        """ 当選予定の在庫数を商品明細ごとに取得
        (stock_id, quantity)
        """
        s = [Stock, StockStatus, ProductItem, Performance,
             sql.func.sum(LotEntryProduct.quantity * ProductItem.quantity),
             sql.func.count(LotEntryWish.id)]
        q = DBSession.query(*s).filter(
            LotEntry.lot_id==self.lot.id
        ).filter(
            LotEntryWish.lot_entry_id==LotEntry.id
        ).filter(
            LotElectWork.entry_wish_no==LotEntryWish.entry_wish_no
        ).filter(
            LotEntryProduct.lot_wish_id==LotEntryWish.id
        ).filter(
            LotEntryProduct.product_id==Product.id
        ).filter(
            Product.id==ProductItem.product_id
        ).filter(
            Stock.id==ProductItem.stock_id
        ).filter(
            Stock.id==StockStatus.stock_id
        ).filter(
            Performance.id==ProductItem.performance_id
        ).filter(
            LotEntryWish.canceled_at==None
        ).filter(
            LotEntryWish.elected_at==None
        ).group_by(Stock.id).order_by(Performance.start_on, Performance.id)

        return q.all()


    @property
    def election_publisher(self):
        return get_publisher(self.request, 'lots.election')

    @property
    def rejection_publisher(self):
        return get_publisher(self.request, 'lots.rejection')

    def elect_lot_entries(self):
        publisher = self.election_publisher
        works = self.lot.electing_works
        logger.info("publish electing lot: lot_id = {0} : count = {1}".format(
            self.lot.id,
            len(works),
        ))
        for work in works:
            logger.info("publish entry_wish = {0}".format(work.entry_wish_no))
            body = {"lot_id": self.lot.id,
                    "entry_no": work.lot_entry_no,
                    "wish_order": work.wish_order,
            }
            publisher.publish(body=json.dumps(body),
                              routing_key="lots.election",
                              properties=dict(content_type="application/json"))

    def send_election_mails(self):
        publisher = self.election_publisher
        works = self.lot.electing_works
        logger.info("publish electing lot: lot_id = {0} : count = {1}".format(
            self.lot.id,
            len(works),
            ))
        for work in works:
            logger.info("publish entry_wish = {0}".format(work.entry_wish_no))
            body = {"lot_id": self.lot.id,
                    "entry_no": work.lot_entry_no,
                    "wish_order": work.wish_order,
                    }
            publisher.publish(body=json.dumps(body),
                              routing_key="lots.send_election_mail",
                              properties=dict(content_type="application/json"))

    def reject_lot_entries(self):
        publisher = self.rejection_publisher
        works = self.lot.reject_works
        logger.info("publish rejecting lot: lot_id = {0} : count = {1}".format(
            self.lot.id,
            len(works),
        ))
        for work in works:
            body = {
                "lot_id": self.lot.id,
                "entry_no": work.lot_entry_no,
                }
            publisher.publish(body=json.dumps(body),
                              routing_key="lots.rejection",
                              properties=dict(content_type="application/json"))
