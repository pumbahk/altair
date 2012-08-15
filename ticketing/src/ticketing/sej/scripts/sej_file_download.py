# -*- coding:utf-8 -*-

#
# 通知ファイルをダウンロードする
#

import sys
import sqlahelper
from sqlalchemy.orm.exc import NoResultFound
import optparse, textwrap

from os.path import abspath, dirname

from pyramid.paster import bootstrap
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


def file_get_and_import(date, shop_id, secret_key, hostname, file_dest):

    for notification_type in SejNotificationType:
        try:
            body = request_fileget(
                notification_type,
                date)

            date_str = date.strftime('%Y%m%d')
            sej_output_path = "%s/%s" % (file_dest, date_str)
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

    description = """\
    """
    usage = "usage: %prog config_uri --date 2012070"
    parser = optparse.OptionParser(
        usage=usage,
        description=textwrap.dedent(description)
        )
    parser.add_option(
        '-d', '--date',
        dest='date',
        metavar='YYYYMMDD',
        type="string",
        help=("target date")
        )

    options, args = parser.parse_args(sys.argv[1:])
    if not len(args) >= 2:
        print('You must provide at least one argument')
        return 2

    config_uri = args[0]
    env = bootstrap(config_uri)
    request = env['request']
    registry = env['registry']
    settings = registry.settings

    date = options.date
    session = sqlahelper.get_session()
    session.configure(autocommit=True, extension=[])

    if len(sys.argv) < 2:
        print "usage: python sej_notification.py development.ini"
        sys.exit()

    hostname = settings['sej.inticket_api_url']
    shop_id = settings['sej.shop_id']
    secret_key = settings['sej.api_key']
    file_dest = settings['sej.file_dest_path']

    file_get_and_import(date, shop_id, secret_key, hostname, file_dest)

if __name__ == u"__main__":
    main(sys.argv)
