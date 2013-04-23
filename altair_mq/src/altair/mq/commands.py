import logging

from cliff.command import Command
from tornado import ioloop
from . import get_consumer

logger = logging.getLogger(__name__)

class ServeCommand(Command):
    def take_action(self, parsed_args):
        request = self.app.app['request']

        consumer = get_consumer(request)

        logger.info("into loop")
        io_loop = ioloop.IOLoop.instance()
        io_loop.add_timeout(500, consumer.connect)
        io_loop.start()
