# -*- coding:utf-8 -*-
from pyramid.paster import bootstrap
import sqlahelper

session = sqlahelper.get_session()

import datetime

from ticketing.sej.payment import request_order, request_update_order, request_cancel_order
from ticketing.sej.payment import SejTicketDataXml, SejPaymentType, SejTicketType, SejOrderUpdateReason
from ticketing.sej.models import SejOrder

import optparse
import sys

from os.path import abspath, dirname
sys.path.append(abspath(dirname(dirname(__file__))))

from paste.deploy import loadapp

import logging

logging.basicConfig()
log = logging.getLogger(__file__)

def test_get_file_payment_info():


    from ticketing.sej.payment import request_fileget
    from ticketing.sej.resources import SejNotificationType
    from ticketing.sej.file import SejInstantPaymentFileParser

    file = request_fileget(
        date=datetime.datetime(2012,6,6),
        notification_type=SejNotificationType.InstantPaymentInfo)

    parser = SejInstantPaymentFileParser()
    data = parser.parse(file)

    for row in data:
        print row


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

    test_get_file_payment_info()

if __name__ == u"__main__":
    main(sys.argv)
