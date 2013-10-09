def main():
    import sys
    from argparse import ArgumentParser
    from ConfigParser import ConfigParser
    from .bot import CartBot
    import logging
    logging.basicConfig(level=logging.INFO)

    parser = ArgumentParser()
    parser.add_argument('-c', '--config', dest='config',
                        help='config')
    parser.add_argument('url', nargs=1, help='cart url')
    options = parser.parse_args()
    if not options.config:
        print >>sys.stderr, "configuration file is not specified"
        sys.exit(255)
    config = ConfigParser()
    config.read(options.config)
    http_auth_credentials = None
    try:
        http_auth_credentials = dict(config.items('http_auth'))
    except:
        pass
    bot = CartBot(
        url = options.url[0],
        credentials=dict(config.items('credentials')),
        shipping_address=dict(config.items('shipping_address')),
        credit_card_info=dict(config.items('credit_card_info')),
        http_auth_credentials=http_auth_credentials
        )
    while bot.buy_something():
        pass
