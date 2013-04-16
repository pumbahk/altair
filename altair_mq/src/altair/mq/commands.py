import logging
#import pika

from cliff.command import Command
from tornado import ioloop
#from .consumer import PikaClient
from . import get_consumer

logger = logging.getLogger(__name__)

class ServeCommand(Command):
    def take_action(self, parsed_args):
        #settings = self.app.app['registry'].settings
        request = self.app.app['request']

        #url = settings['altair.mq.url']
        #parameters = pika.URLParameters(url)
        #consumer = PikaClient(sample_task, parameters)
        consumer = get_consumer(request)

        logger.info("into loop")
        io_loop = ioloop.IOLoop.instance()
        io_loop.add_timeout(500, consumer.connect)
        io_loop.start()
