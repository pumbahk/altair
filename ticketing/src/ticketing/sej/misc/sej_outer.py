# -*- coding:utf-8 -*-

#
# SEJとの外部結合の為に使ったスクリプト
#

from pyramid.paster import bootstrap
import sqlahelper

session = sqlahelper.get_session()

import datetime
# -*- coding:utf-8 -*-
from ticketing.sej.payment import request_order, request_update_order, request_cancel_order
from ticketing.sej.payment import SejTicketDataXml, SejPaymentType, SejTicketType, SejOrderUpdateReason
from ticketing.sej.models import SejOrder

import time

import csv
import optparse
import sys

from os.path import abspath, dirname
sys.path.append(abspath(dirname(dirname(__file__))))

from paste.deploy import loadapp

import logging

logging.basicConfig()
log = logging.getLogger(__file__)


def main(argv=sys.argv):
    session.configure(autocommit=True, extension=[])

    parser = optparse.OptionParser(
        description=__doc__,
        usage='%prog [options]',
    )
    parser.add_option('-C', '--config',
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

    log.debug('test')

#    payment_test_pre_r_c_c()
#    payment_test_paid_r_c_c()
#    payment_test_p_only_r_c_c()
#    payment_test()
#    payment_test_pre_2()
#    payment_test_pay()
#    payment_order_update_test_001()
#    payment_order_update_test_002()
#    payment_order_update_test_003()

if __name__ == u"__main__":
    main(sys.argv)