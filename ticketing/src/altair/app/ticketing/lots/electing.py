# -*- coding: utf-8 -*-
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
    Lot,
    LotEntry,
    LotEntryWish,
    LotEntryProduct,
    LotElectWork,
    LotRejectWork,
    LotElectedEntry,
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
    def election_mail_publisher(self):
        return get_publisher(self.request, 'lots.election_mail')

    @property
    def rejection_publisher(self):
        return get_publisher(self.request, 'lots.rejection')

    @property
    def rejection_mail_publisher(self):
        return get_publisher(self.request, 'lots.rejection_mail')

    def elect_lot_entries(self):
        publisher = self.election_publisher
        works = self.lot.electing_works
        logger.info("publish electing lot: lot_id = {0} : count = {1}".format(
            self.lot.id,
            len(works),
        ))
        lot_entry_lock = self.request.lot_entry_lock
        if lot_entry_lock:
            for stock, stock_status, product_item, performance, quantity, count in self.required_stocks:
                # stockerのLockを使わない場合、事前に在庫数を確認、足りない場合に例外発生
                if stock_status.quantity < quantity:
                    from altair.app.ticketing.cart import api as cart_api
                    raise cart_api.NotEnoughStockException(stock, stock_status.quantity, quantity)

        for work in works:
            logger.info("publish entry_wish = {0}".format(work.entry_wish_no))
            body = {"lot_id": self.lot.id,
                    "entry_no": work.lot_entry_no,
                    "wish_order": work.wish_order,
                    "lot_entry_lock":lot_entry_lock,
            }
            publisher.publish(body=json.dumps(body),
                              routing_key="lots.election",
                              properties=dict(content_type="application/json"))

    def send_election_mails(self):
        """メール送信taskをworkerに送信"""
        publisher = self.election_mail_publisher
        lot_elected_entries = LotElectedEntry \
            .query \
            .join(LotEntryWish) \
            .join(LotEntry) \
            .join(Lot) \
            .filter(Lot.id == self.lot.id) \
            .filter(LotEntry.ordered_mail_sent_at == None) \
            .all()

        logger.info('publish send election mail: Lot.id={}: count={}'.format(
            self.lot.id, len(lot_elected_entries)))

        for lot_elected_entry in lot_elected_entries:
            wish = lot_elected_entry.lot_entry_wish
            logger.info('publish entry_wish = {0}'.format(wish.entry_wish_no))
            publisher.publish(
                body=json.dumps({'lot_elected_entry_id': lot_elected_entry.id}),
                routing_key='lots.election_mail',
                properties=dict(content_type='application/json'),
                )

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

    def get_election_mail_target_lot_elected_entries(self, lot_id):
        return LotElectedEntry \
            .query \
            .join(LotEntryWish) \
            .join(LotEntry) \
            .join(Lot) \
            .filter(Lot.id == lot_id) \
            .filter(LotEntry.ordered_mail_sent_at == None) \
            .all()

    def get_rejection_mail_target_lot_rejected_entries(self, lot_id):
        return LotRejectedEntry \
            .query \
            .join(LotEntry) \
            .join(Lot) \
            .filter(Lot.id == lot_id) \
            .filter(LotEntry.withdrawn_at == None) \
            .filter(LotEntry.ordered_mail_sent_at == None) \
            .all()

    def send_election_mails(self):
        """当選メール送信taskをworkerに送信"""
        publisher = self.election_mail_publisher
        lot_elected_entries = self.get_election_mail_target_lot_elected_entries(self.lot.id)
        total_count = len(lot_elected_entries)
        logger.info('publish send election mail: Lot.id={}: count={}'.format(self.lot.id, total_count))

        for lot_elected_entry in lot_elected_entries:
            wish = lot_elected_entry.lot_entry_wish
            logger.info('publish entry_wish = {0}'.format(wish.entry_wish_no))
            publisher.publish(
                body=json.dumps({'lot_elected_entry_id': lot_elected_entry.id}),
                routing_key='lots.election_mail',
                properties=dict(content_type='application/json'),
                )
        return total_count

    def send_rejection_mails(self):
        """落選メール送信taskをworkerに送信"""
        publisher = self.rejection_mail_publisher
        lot_rejected_entries = self.get_rejection_mail_target_lot_rejected_entries(self.lot.id)
        total_count = len(lot_rejected_entries)
        logger.info('publish send rejection mail: Lot.id={}: count={}'.format(
            self.lot.id, total_count))

        for lot_rejected_entry in lot_rejected_entries:
            logger.info('publish LotRejectedEntry.id = {0}'.format(lot_rejected_entry.id))
            publisher.publish(
                body=json.dumps({'lot_rejected_entry_id': lot_rejected_entry.id}),
                routing_key='lots.rejection_mail',
                properties=dict(content_type='application/json'),
                )
        return total_count
