from gevent import monkey
monkey.patch_time()
monkey.patch_socket()
monkey.patch_ssl()
monkey.patch_select()
monkey.patch_thread()

import sys
from argparse import ArgumentParser
from ConfigParser import ConfigParser, NoSectionError
from lxmlmechanize import Mechanize
from .bot import CartBot
from urllib2 import HTTPError
import threading
import time
import logging
import logging.config
from cookielib import CookieJar

class LoggableCartBot(CartBot):
    logger = logging.getLogger('altair.cartbot')
    log_output = False

    def print_(self, *msgs):
        if self.log_output:
            self.logger.info(u' '.join(msgs))
        else:
            super(LoggableCartBot, self).print_(*msgs)

    def __init__(self, *args, **kwargs):
        self._cookie = CookieJar()
        kwargs['cookie'] = self._cookie
        retry_count = kwargs.pop('retry_count', 1)
        if retry_count is not None:
            class RetryingMechanize(Mechanize):
                logger = logging.getLogger('mechanize')

                def reload(self):
                    i = 0
                    elapsed = None
                    while True:
                        try:
                            s = time.time() 
                            super(RetryingMechanize, self).reload()
                            elapsed = time.time() - s
                        except HTTPError as e:
                            if e.code >= 500 and e.code <= 599:
                                i += 1
                                if i >= retry_count:
                                    raise
                                else:
                                    time.sleep(1)
                                    continue
                            else:
                                raise
                        break
                    if elapsed is not None:
                        self.logger.info("%s processed in %g seconds", self.location, elapsed)
            self.Mechanize = RetryingMechanize
        else:
            self.Mechanize = Mechanize
        super(LoggableCartBot, self).__init__(*args, **kwargs)

def main():
    logging.basicConfig(level=logging.INFO)

    parser = ArgumentParser()
    parser.add_argument('-c', '--config', dest='config',
                        help='config')
    parser.add_argument('-l', '--logging', dest='logging', action='store_true',
                        help="Use Python's logging facility instead of print")
    parser.add_argument('-n', '--repeat', dest='repeat', help="Repeat n times")
    parser.add_argument('-C', '--concurrency', dest='concurrency', help="Stress mode; make n concurrent requests")
    parser.add_argument('-r', '--retry-count', dest='retry_count', help='retry count')
    parser.add_argument('url', nargs=1, help='cart url')
    options = parser.parse_args()
    if not options.config:
        print >>sys.stderr, "configuration file is not specified"
        sys.exit(255)
    repeat = 1
    concurrency = 1
    retry_count = None
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

    if options.retry_count:
        try:
            retry_count = int(options.retry_count)
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
            http_auth_credentials=http_auth_credentials,
            retry_count=retry_count
            )
        bot.log_output = options.logging

        for _ in range(repeat):
            while True:
                order_no = bot.buy_something()
                if order_no is None and not bot.all_sales_segments:
                    break
                if order_no is not None:
                    print order_no
                break

    import time
    threads = [threading.Thread(target=run, name='%d' % i) for i in range(concurrency)]
    for thread in threads:
        thread.start()
        #time.sleep(1)

    for thread in threads:
        thread.join()


