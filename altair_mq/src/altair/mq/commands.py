import logging
import pika

from cliff.command import Command
from tornado import ioloop
from . import PikaClient

logger = logging.getLogger(__name__)

class ServeCommand(Command):
    def take_action(self, parsed_args):
        logger.info("")
        settings = self.app.app['registry'].settings
        url = settings['altair.mq.url']
        parameters = pika.URLParameters(url)
        consumer = PikaClient(self.app.app, parameters)

        io_loop = ioloop.IOLoop.instance()
        io_loop.add_timeout(500, consumer.connect)
        io_loop.start()
