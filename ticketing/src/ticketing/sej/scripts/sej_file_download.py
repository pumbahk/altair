# -*- coding:utf-8 -*-

#
# SEJとの外部結合の為に使ったスクリプト
#

import optparse
import sys
import sqlahelper
from sqlalchemy.orm.exc import NoResultFound

from datetime import datetime, timedelta
from dateutil.parser import parse
from os.path import abspath, dirname

from ticketing.sej.payment import request_fileget
from ticketing.sej.models import SejFile
from ticketing.sej.resources import SejNotificationType, code_from_notification_type
from ticketing.sej.exceptions import SejServerError

sys.path.append(abspath(dirname(dirname(__file__))))

from paste.deploy import loadapp

import logging

logging.basicConfig()
log = logging.getLogger(__file__)

import os

DBSession = sqlahelper.get_session()

def file_get_and_import(date, notification_type = None):

    for notification_type in SejNotificationType:
        try:
            body = request_fileget(
                notification_type,
                date)

            date_str = date.strftime('%Y%m%d')
            sej_output_path = "/tmp/sej/%s" % date_str
            if not os.path.exists(sej_output_path):
                os.makedirs(sej_output_path)
            file_path = '%s/SEITIS%02d_%s.txt' % (sej_output_path, notification_type.v,date_str)

            try :
                file = SejFile.filter(SejFile.file_date == date and SejFile.notification_type == notification_type.v).one()
            except NoResultFound, e:
                file = SejFile()
                DBSession.add(file)

            file.file_url = "file://%s" % file_path
            file.file_date = date
            file.notification_type = notification_type.v
            DBSession.flush()

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
        date = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")

    date = parse(date)
    print date

    app = loadapp('config:%s' % config, 'main')
    settings = app.registry.settings

    sej_hostname = settings['sej.inticket_api_url']

    file_get_and_import(date)

if __name__ == u"__main__":
    main(sys.argv)
