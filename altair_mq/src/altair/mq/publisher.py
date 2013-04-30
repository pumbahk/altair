from altair.mq.interfaces import IPublisher
from zope.interface import implementer

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

