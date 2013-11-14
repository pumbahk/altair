def main():
    import sys
    from argparse import ArgumentParser
    from ConfigParser import ConfigParser, NoSectionError
    from .bot import CartBot
    import logging
    import logging.config

    logging.basicConfig(level=logging.INFO)

    class LoggableCartBot(CartBot):
        log_output = False

        def print_(self, *msgs):
            if self.log_output:
                logging.info(u' '.join(msgs))
            else:
                super(LoggableCartBot, self).print_(*msgs)

    parser = ArgumentParser()
    parser.add_argument('-c', '--config', dest='config',
                        help='config')
    parser.add_argument('-l', '--logging', dest='logging', action='store_true',
                        help="Use Python's logging facility instead of print")
    parser.add_argument('url', nargs=1, help='cart url')
    options = parser.parse_args()
    if not options.config:
        print >>sys.stderr, "configuration file is not specified"
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
    bot = LoggableCartBot(
        url = options.url[0],
        rakuten_auth_credentials=rakuten_auth_credentials,
        fc_auth_credentials=fc_auth_credentials,
        shipping_address=dict(config.items('shipping_address')),
        credit_card_info=dict(config.items('credit_card_info')),
        http_auth_credentials=http_auth_credentials
        )
    bot.log_output = options.logging
    while True:
        order_no = bot.buy_something()
        if order_no is None and not bot.all_sales_segments:
            break
        if order_no is not None:
            print order_no

