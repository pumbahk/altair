# coding: utf-8

import optparse
import sys
import logging
from datetime import datetime
import sqlahelper
from pyramid.paster import bootstrap, setup_logging
from altair.multilock import AlreadyStartUpError, MultiStartLock

logger = logging.getLogger(__name__)

def main(argv=sys.argv):
    if len(sys.argv) < 2:
        print "usage: python sej_notification.py development.ini"
        sys.exit()

    ini_file = sys.argv[1]
    setup_logging(ini_file)
    env = bootstrap(ini_file)

    try:
        with MultiStartLock(__name__, 1):
            request = env['request']
            registry = env['registry']
            settings = registry.settings

            import transaction
            from altair.app.ticketing.orders.api import get_order_by_order_no
            from ..notification.api import fetch_notifications
            from ..notification.processor import SejNotificationProcessor, SejNotificationProcessorError
            now = datetime.now()
            processor = SejNotificationProcessor(request, now)
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
    main(sys.argv)
