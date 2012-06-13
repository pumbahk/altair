# -*- coding:utf-8 -*-

#
# SEJとの外部結合の為に使ったスクリプト
#

import optparse
import sys
import sqlahelper

from dateutil.parser import parse
from os.path import abspath, dirname

from ticketing.sej.payment import request_fileget
from ticketing.sej.resources import SejNotificationType, code_from_notification_type, SejServerError

sys.path.append(abspath(dirname(dirname(__file__))))

from paste.deploy import loadapp

import logging

logging.basicConfig()
log = logging.getLogger(__file__)

import os

def file_get_and_import(date, notification_type = None):

    for notification_type in [
        # 5-1.入金速報
        SejNotificationType.FileInstantPaymentInfo,
        # 5-2.支払期限切れ
        SejNotificationType.FilePaymentExpire,
        # 5-3.発券期限切れ
        SejNotificationType.FileTicketingExpire,
        # 5-4.払戻速報
        SejNotificationType.FileRefundExpire,
        # 6-1.支払い案内
        SejNotificationType.FileCheckInfo,
        # 6-2.会計取消(入金)
        SejNotificationType.FilePaymentCancel,
        # 6-3.会計取消(発券)
        SejNotificationType.FileTicketingCancel,
    ]:
        try:
            body = request_fileget(
                notification_type,
                date)

            date_str = date.strftime('%Y%m%d')
            sej_output_path = "/tmp/sej/%s" % date_str
            if not os.path.exists(sej_output_path):
                os.makedirs(sej_output_path)
            file_path = '%s/SEITIS%02d_%s.txt' % (sej_output_path, notification_type.v)
            print file_path
            f = open(file_path , 'w')
            f.write(body)
            f.close()

        except SejServerError, e:
            print "No Data"


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
    parser.add_option('-d', '--date',
        dest='date',
        help='must be set date',
        metavar='FILE'
    )
    options, args = parser.parse_args(argv[1:])

    # configuration
    config = options.config
    if config is None:
        print 'You must give a config file'
        return

    date = options.date
    if date is None:
        print 'You must give a config file'
        return

    date = parse(date)

    app = loadapp('config:%s' % config, 'main')
    settings = app.registry.settings

    sej_hostname = settings['sej.inticket_api_hostname']

    file_get_and_import(date)

if __name__ == u"__main__":
    main(sys.argv)