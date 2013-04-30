# -*- coding:utf-8 -*-
""" 当選落選

publisher呼び出しをticketing.events.lotsに置いて、こちらにはworkers内の実装をおいてしまうべきか？
"""

import json
from zope.interface import implementer
from altair.mq.interfaces import IPublisher
from .interfaces import IElecting


import pika

@implementer(IPublisher)
class Publisher(object):
    def __init__(self, url):
        self.parameters = pika.URLParameters(url)

    def publish(self, exchange="", routing_key="",
                body="", properties={}, mandatory=False,
                immediate=False):

        connection = pika.BlockingConnection(self.parameters)

        try:
            channel = connection.channel()

            channel.basic_publish(exchange=exchange,
                                  routing_key=routing_key,
                                  body=body,
                                  mandatory=mandatory,
                                  immediate=immediate,
                                  properties=pika.BasicProperties(**properties))

        finally:
            connection.close()


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
