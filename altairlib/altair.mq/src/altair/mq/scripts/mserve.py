import sys
import logging
import argparse
from pyramid.paster import bootstrap, setup_logging

from tornado import ioloop
from .. import get_consumer

logger = logging.getLogger(__name__)

class MServeCommand(object):
    def __init__(self):
        self.parser = self.build_option_parser()

    def build_option_parser(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("config")
        parser.add_argument("consumer", default='pika')
        return parser


    def run(self, args):
        args = self.parser.parse_args(args)

        app = bootstrap(args.config)
        setup_logging(args.config)

        request = app['request']
        request.browserid = "mserve worker"
        consumer = get_consumer(request, args.consumer)

        logger.info("into loop")
        io_loop = ioloop.IOLoop.instance()
        io_loop.add_timeout(500, consumer.connect)
        io_loop.start()
        return 0

def main(args=sys.argv[1:]):
    sys.exit(MServeCommand().run(args))


if __name__ == '__main__':
    main()
