# coding: utf-8

import argparse
import sys
import logging
from datetime import datetime
import sqlahelper
from sqlalchemy.orm.session import Session
from pyramid.paster import bootstrap, setup_logging
from altair.multilock import AlreadyStartUpError, MultiStartLock

logger = logging.getLogger(__name__)

def main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser()
    parser.add_argument('-C', '--config', metavar='config', type=str, dest='config', required=True, help='config file')
    args = parser.parse_args(argv)

    setup_logging(args.config)
    env = bootstrap(args.config)

    try:
        with MultiStartLock(__name__, 1):
            request = env['request']
            registry = env['registry']
            settings = registry.settings

            import transaction
            from ..api import fetch_notifications
            from ..processor import AltairFamiPortNotificationProcessor, AltairFamiPortNotificationProcessorError
            processor = AltairFamiPortNotificationProcessor(request)
            notification_session = Session(bind=sqlahelper.get_engine(), expire_on_commit=False)
            for notification in fetch_notifications(notification_session):
                logger.info("Processing notification: type=%s, order_no=%s, payment_reserve_number=%s, ticketing_reserve_number=%s" % (
                    notification.type,
                    notification.order_no,
                    notification.payment_reserve_number,
                    notification.ticketing_reserve_number))
                trans = transaction.begin()
                try:
                    processor(notification, now=datetime.now())
                    trans.commit()
                    notification_session.commit()
                    logger.info("Finsihed processing notification: type=%s, order_no=%s, payment_reserve_number=%s, ticketing_reserve_number=%s" % (
                        notification.type,
                        notification.order_no,
                        notification.payment_reserve_number,
                        notification.ticketing_reserve_number))
                except AltairFamiPortNotificationProcessorError as e:
                    logger.exception("Error processing notification: type=%s, order_no=%s, payment_reserve_number=%s, ticketing_reserve_number=%s" % (
                        notification.type,
                        notification.order_no,
                        notification.payment_reserve_number,
                        notification.ticketing_reserve_number))
    except AlreadyStartUpError:
        logger.error('another instance of sej_notification is running')

if __name__ == u"__main__":
    main(sys.argv[1:])

