from gevent import monkey
monkey.patch_socket()
monkey.patch_ssl()
monkey.patch_select()
monkey.patch_thread()

import sys
from argparse import ArgumentParser
from ConfigParser import ConfigParser, NoSectionError
from .bot import CartBot
import threading
import logging
import logging.config

class LoggableCartBot(CartBot):
    log_output = False

    def print_(self, *msgs):
        if self.log_output:
            logging.info(u' '.join(msgs))
        else:
            super(LoggableCartBot, self).print_(*msgs)

def main():
    logging.basicConfig(level=logging.INFO)

    parser = ArgumentParser()
    parser.add_argument('-c', '--config', dest='config',
                        help='config')
    parser.add_argument('-l', '--logging', dest='logging', action='store_true',
                        help="Use Python's logging facility instead of print")
    parser.add_argument('-n', '--repeat', dest='repeat', help="Repeat n times")
    parser.add_argument('-C', '--concurrency', dest='concurrency', help="Stress mode; make n concurrent requests")
    parser.add_argument('url', nargs=1, help='cart url')
    options = parser.parse_args()
    if not options.config:
        print >>sys.stderr, "configuration file is not specified"
        sys.exit(255)
    repeat = 1
    concurrency = 1
    if options.repeat:
        try:
            repeat = int(options.repeat)
        except:
            parse.help()
            sys.exit(255)

    if options.concurrency:
        try:
            concurrency = int(options.concurrency)
        except:
            parse.help()
            sys.exit(255)

    if options.logging:
        if options.config:
            try:
                logging.config.fileConfig(options.config)
            except Exception as e:
                print >>sys.stderr, 'WARNING: failed to configure logger with the configuration file (%s)' % e.message

    config = ConfigParser()
    config.read(options.config)

    http_auth_credentials = None

    try:
        http_auth_credentials = dict(config.items('http_auth'))
    except:
        pass
    rakuten_auth_credentials = None
    fc_auth_credentials = None
    try:
        rakuten_auth_credentials = dict(config.items('rakuten_auth'))
    except NoSectionError:
        pass
    try:
        fc_auth_credentials = dict(config.items('fc_auth'))
    except NoSectionError:
        pass

    def run():
        bot = LoggableCartBot(
            url = options.url[0],
            rakuten_auth_credentials=rakuten_auth_credentials,
            fc_auth_credentials=fc_auth_credentials,
            shipping_address=dict(config.items('shipping_address')),
            credit_card_info=dict(config.items('credit_card_info')),
            http_auth_credentials=http_auth_credentials
            )
        bot.log_output = options.logging

        for _ in range(repeat):
            while True:
                order_no = bot.buy_something()
                if order_no is None and not bot.all_sales_segments:
                    break
                if order_no is not None:
                    print order_no

    threads = [threading.Thread(target=run, name='%d' % i) for i in range(concurrency)]
    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()


