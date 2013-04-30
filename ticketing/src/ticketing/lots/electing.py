# -*- coding:utf-8 -*-
""" 当選落選

publisher呼び出しをticketing.events.lotsに置いて、こちらにはworkers内の実装をおいてしまうべきか？
"""

import json
from zope.interface import implementer
from altair.mq.interfaces import IPublisher
from .interfaces import IElecting

@implementer(IElecting)
class Electing(object):
    def __init__(self, lot, request):
        self.request = request
        self.lot = lot

    @property
    def publisher(self):
        return self.request.registry.getUtility(IPublisher)

    def elect_lot_entries(self):
        publisher = self.publisher
        body = {"lot_id": self.lot.id}
        publisher.publish(exchange="lot.electing",
                          body=json.dumps(body))
