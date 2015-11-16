# encoding: utf-8
from gevent import monkey
monkey.patch_time()
monkey.patch_socket()
monkey.patch_ssl()
monkey.patch_select()
monkey.patch_thread()

import sys
import time
from argparse import ArgumentParser
from configparser import ConfigParser, NoSectionError
from cookielib import CookieJar
from lxmlmechanize import Mechanize
from .bot import CartBot
from urllib2 import HTTPError
import threading
import time
import logging
import logging.config

HUMANIC_SLEEP_SECOND = 37 # 5 minutes / 1 order, is humanic
THREAD_START_INTERVAL = 1

class LoggableCartBot(CartBot):
    logger = logging.getLogger('altair.cartbot')
    log_output = False

    def print_(self, *msgs):
        if self.log_output:
            self.logger.info(u' '.join(msgs))
        else:
            super(LoggableCartBot, self).print_(*msgs)

    def __init__(self, *args, **kwargs):
        self._cj = cj = CookieJar()

        def browserid():
            try:
                return cj._cookies['.tstar.jp']['/']['browserid'].value
            except (KeyError, AttributeError) as err:
                return 'NO BROWSER ID'
        
        kwargs['cookiejar'] =  self._cj
        retry_count = kwargs.pop('retry_count', 1)

        class RetryingMechanize(Mechanize):
            logger = logging.getLogger('mechanize')

            def create_loader(self, request):
                fn = super(RetryingMechanize, self).create_loader(request)
                def _():
                    s = time.time()
                    i = 0
                    while True:
                        try:
                            self.logger.info("making %s request to %s", request.get_method(), request.get_full_url())
                            for header_name, header_value in request.header_items():
                                self.logger.debug("[HEADER] %s: %s", header_name, header_value)
                            self.logger.debug("[REQUEST BODY] %r", request.data)
                            retval = fn()
                        except HTTPError as e:
                            if e.code >= 500 and e.code <= 599:
                                i += 1
                                if i >= retry_count:
                                    raise
                                else:
                                    self.logger.info("got error %s for %s. attempt to retry in %g seconds", e.code, e.url, 1.)
                                    time.sleep(1)
                                    continue
                            else:
                                continue
                        except Exception as err:
                            i += 1
                            if i >= retry_count:
                                raise
                            else:
                                self.logger.exception("oops")
                                continue
                        break
                    elapsed = time.time() - s
                    self.logger.info("%s processed in %g seconds (%s)", request.get_full_url(), elapsed, browserid())
                    return retval
                return _

        self.Mechanize = RetryingMechanize
        super(LoggableCartBot, self).__init__(*args, **kwargs)


def main():
    logging.basicConfig(level=logging.INFO)

    parser = ArgumentParser()
    parser.add_argument('-c', '--config', dest='config',
                        help='config')
    parser.add_argument('-l', '--logging', dest='logging', action='store_true',
                        help="Use Python's logging facility instead of print")
    parser.add_argument('-n', '--repeat', dest='repeat', help="Repeat n times")
    parser.add_argument('-f', '--fail_percent', dest='fail_percent', help="Fail Percent 0 - 100, default = 0")
    parser.add_argument('-C', '--concurrency', dest='concurrency', help="Stress mode; make n concurrent requests")
    parser.add_argument('-r', '--retry-count', dest='retry_count', help='retry count')
    parser.add_argument('-s', '--sleep', dest='sleep_sec', type=float, default=HUMANIC_SLEEP_SECOND,
                        help='sleep second.(default: {0})'.format(HUMANIC_SLEEP_SECOND))
    parser.add_argument('-i', '--interval', dest='interval', type=float, default=THREAD_START_INTERVAL,
                        help='threads start interval.(default: {0})'.format(THREAD_START_INTERVAL))
    parser.add_argument('url', nargs=1, help='cart url')
    options = parser.parse_args()
    if not options.config:
        print >>sys.stderr, "configuration file is not specified"
        sys.exit(255)
    repeat = 1
    concurrency = 1
    retry_count = None
    fail_percent = 0

    if options.repeat:
        try:
            repeat = int(options.repeat)
        except:
            parser.print_help()
            sys.exit(255)

    if options.concurrency:
        try:
            concurrency = int(options.concurrency)
        except:
            parser.print_help()
            sys.exit(255)

    if options.retry_count:
        try:
            retry_count = int(options.retry_count)
        except:
            parser.print_help()
            sys.exit(255)

    if options.fail_percent:
        try:
            fail_percent = int(options.fail_percent)
            if fail_percent < 0 or fail_percent > 100:
                parser.print_help()
                sys.exit(255)
        except:
            parser.print_help()
            sys.exit(255)

    if options.logging:
        if options.config:
            try:
                logging.config.fileConfig(options.config)
            except Exception as e:
                print >>sys.stderr, 'WARNING: failed to configure logger with the configuration file (%s)' % e.message

    config = ConfigParser()
    config.read(options.config, encoding='utf-8')

    http_auth_credentials = None

    try:
        http_auth_credentials = dict(config.items('http_auth'))
    except:
        pass
    rakuten_auth_credentials = None
    fc_auth_credentials = None
    extauth_credentials = None
    try:
        rakuten_auth_credentials = dict(config.items('rakuten_auth'))
    except NoSectionError:
        pass
    try:
        fc_auth_credentials = dict(config.items('fc_auth'))
    except NoSectionError:
        pass
    try:
        extauth_credentials = dict(config.items('extauth'))
    except NoSectionError:
        pass

    def run():
        for _ in range(repeat):
            bot = LoggableCartBot(
                url = options.url[0],
                rakuten_auth_credentials=rakuten_auth_credentials,
                fc_auth_credentials=fc_auth_credentials,
                extauth_credentials=extauth_credentials,
                shipping_address=dict(config.items('shipping_address')),
                credit_card_info=dict(config.items('credit_card_info')),
                http_auth_credentials=http_auth_credentials,
                retry_count=retry_count,
                sleep_sec=options.sleep_sec,
                fail_percent=fail_percent,
                )
            bot.log_output = options.logging 
            order_no = bot.buy_something()

    threads = [threading.Thread(target=run, name='%d' % i) for i in range(concurrency)]
    for thread in threads:
        thread.start()
        time.sleep(options.interval)

    for thread in threads:
        thread.join()
