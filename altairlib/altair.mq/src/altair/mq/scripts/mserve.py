import sys
import logging
import argparse
from pyramid.config import global_registries

from pyramid.paster import get_app, setup_logging

from tornado import ioloop
from .. import get_consumer

logger = logging.getLogger(__name__)

class MServeCommand(object):
    def __init__(self):
        self.parser = self.build_option_parser()

    def build_option_parser(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("config")
        parser.add_argument("consumers", nargs='+', default=['pika'])
        return parser


    def run(self, args):
        args = self.parser.parse_args(args)

        setup_logging(args.config)
        app = get_app(args.config)
        registry = global_registries.last

        io_loop = ioloop.IOLoop.instance()
        for consumer_name in args.consumers:
            consumer = get_consumer(registry, consumer_name)
            if consumer is None:
                sys.stderr.write("no such consumer: %s\n" % consumer_name)
                sys.stderr.flush()
                return 1
            io_loop.add_timeout(500, consumer.connect)
        logger.info("into loop")
        io_loop.start()
        return 0

def main(args=sys.argv[1:]):
    sys.exit(MServeCommand().run(args))


if __name__ == '__main__':
    main()
