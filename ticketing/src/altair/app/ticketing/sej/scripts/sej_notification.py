# coding: utf-8

import argparse
import logging
import sys

from datetime import datetime
from pyramid.paster import bootstrap, setup_logging
from pyramid.config import Configurator


from altair.multilock import AlreadyStartUpError, MultiStartLock

logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="SEJ Notification")
    parser.add_argument('conf', nargs='?', help='Please provide altair.ticketing.batch.ini')
    args = parser.parse_args()

    setup_logging(args.conf)
    env = bootstrap(args.conf)

    try:
        with MultiStartLock(__name__, 1):
            request = env['request']
            config = Configurator()
            registry = config.registry
            registry.settings = env['registry'].settings
            config.include('altair.point')

            import transaction
            from altair.app.ticketing.orders.api import get_order_by_order_no
            from ..notification.api import fetch_notifications
            from ..notification.processor import SejNotificationProcessor, SejNotificationProcessorError
            now = datetime.now()
            processor = SejNotificationProcessor(request, registry, now)
            for sej_order, notification in fetch_notifications():
                logger.info("Processing notification: process_number=%s, order_no=%s, exchange_number=%s, billing_number=%s" % (
                    notification.process_number,
                    sej_order.order_no,
                    notification.exchange_number,
                    notification.billing_number))
                trans = transaction.begin()
                order = get_order_by_order_no(request, sej_order.order_no)
                try:
                    processor(sej_order, order, notification)
                    trans.commit()
                except SejNotificationProcessorError as e:
                    logger.exception("process_number=%s, order_no=%s, exchange_number=%s, billing_number=%s" % (
                        notification.process_number,
                        sej_order.order_no,
                        notification.exchange_number,
                        notification.billing_number))
    except AlreadyStartUpError:
        logger.error('another instance of sej_notification is running')

if __name__ == u"__main__":
    main()
