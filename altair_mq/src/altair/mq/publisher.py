import logging
from altair.mq.interfaces import IPublisher
from zope.interface import implementer

import pika

logger = logging.getLogger(__name__)


@implementer(IPublisher)
class Publisher(object):
    def __init__(self, url):
        self.parameters = pika.URLParameters(url)

    def publish(self, exchange="", routing_key="",
                body="", properties={}, mandatory=False,
                immediate=False):
        logger.debug("publish body={body} exchange={exchange} queue={routing_key}".format(body=body,
                                                                                          exchange=exchange,
                                                                                          routing_key=routing_key))
        connection = pika.BlockingConnection(self.parameters)

        try:
            channel = connection.channel()

            channel.basic_publish(exchange=exchange,
                                  routing_key=routing_key,
                                  body=body,
                                  mandatory=mandatory,
                                  immediate=immediate,
                                  properties=pika.BasicProperties(**properties))
            logger.debug("published")

        except Exception as e:
            logger.exception(e)
        finally:
            pass
            #connection.close()

