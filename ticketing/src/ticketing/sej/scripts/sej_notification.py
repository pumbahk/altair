# -*- coding:utf-8 -*-

#
# SEJとの外部結合の為に使ったスクリプト
#

import optparse
import sys
import sqlahelper

from datetime import datetime
from dateutil import parser as date_parser
from os.path import abspath, dirname

from ticketing.sej.resources import SejNotificationType, code_from_notification_type
from ticketing.sej.models import SejNotification, SejOrder

sys.path.append(abspath(dirname(dirname(__file__))))

from paste.deploy import loadapp

import logging

logging.basicConfig()
log = logging.getLogger(__file__)

from sqlalchemy import and_

def reflect_ticketing_and_payment(notification):
    print (

    )
    order = SejOrder.filter(
        and_(
            SejOrder.order_id==notification.order_id,
            SejOrder.exchange_number==notification.exchange_number,
            SejOrder.billing_number==notification.billing_number
        )
    ).one()

    print order

def dummy(notification):
    pass

def process_notification():
    reflected_at = datetime.now()
    list = SejNotification.filter(SejNotification.reflected_at==None).limit(500).all()
    for row in list:
        {
            '1'  : reflect_ticketing_and_payment,
            '31' : dummy,
            '72' : dummy,
            '73' : dummy
        }.get(row.notification_type,dummy)(row)




def main(argv=sys.argv):

    session = sqlahelper.get_session()
    session.configure(autocommit=True, extension=[])

    parser = optparse.OptionParser(
        description=__doc__,
        usage='%prog [options]',
    )
    parser.add_option('-c', '--config',
        dest='config',
        help='Path to configuration file (defaults to $CWD/development.ini)',
        metavar='FILE'
    )

    options, args = parser.parse_args(argv[1:])

    # configuration
    config = options.config
    if config is None:
        print 'You must give a config file'
        return

    app = loadapp('config:%s' % config, 'main')
    settings = app.registry.settings
    process_notification()

if __name__ == u"__main__":
    main(sys.argv)