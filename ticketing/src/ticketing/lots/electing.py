# -*- coding:utf-8 -*-
""" 当選落選

publisher呼び出しをticketing.events.lotsに置いて、こちらにはworkers内の実装をおいてしまうべきか？
"""
import logging
import json
from pyramid.decorator import reify
from zope.interface import implementer
from altair.mq.interfaces import IPublisher
from .interfaces import IElecting


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

        return blockers

    def check_product_items(self):
        """ 所属する商品すべてが商品明細を持っているか"""

        for product in self.lot.products:
            if not product.items:
                yield product



    @property
    def publisher(self):
        return self.request.registry.getUtility(IPublisher)

    def elect_lot_entries(self):
        publisher = self.publisher
        # TODO すでにOrderがあるworkは排除すべき
        works = self.lot.elect_works
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
                              routing_key="lots",
                              properties=dict(content_type="application/json"))
