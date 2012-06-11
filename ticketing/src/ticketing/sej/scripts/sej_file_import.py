# -*- coding:utf-8 -*-

#
# SEJとの外部結合の為に使ったスクリプト
#

import optparse
import sys
import sqlahelper

from dateutil import parser as date_parser
from os.path import abspath, dirname

from ticketing.sej.payment import request_fileget
from ticketing.sej.resources import SejNotificationType, code_from_notification_type

sys.path.append(abspath(dirname(dirname(__file__))))

from paste.deploy import loadapp

import logging

logging.basicConfig()
log = logging.getLogger(__file__)

def file_get_and_import(notification_type, date, hostname):


    request_fileget(
        notification_type,
        date)

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
    parser.add_option('-t', '--type',
        dest='type',
        help='Path to configuration file (defaults to $CWD/development.ini)',
        metavar='FILE'
    )
    parser.add_option('-d', '--date',
        dest='date',
        help='Path to configuration file (defaults to $CWD/development.ini)',
        metavar='FILE'
    )
    options, args = parser.parse_args(argv[1:])

    # configuration
    config = options.config
    if config is None:
        print 'You must give a config file'
        return
    type = options.type
    if type is None:

        for k,v in code_from_notification_type.items():
            print "%s %s" % (k,v)

        return
    date = options.date
    if date is None:
        print 'You must give a config file'
        return

    date = date_parser(date)
    type = code_from_notification_type.get(type)

    app = loadapp('config:%s' % config, 'main')
    settings = app.registry.settings

    sej_hostname = settings['sej.inticket_api_hostname']

    file_get_and_import(type, date, sej_hostname)

if __name__ == u"__main__":
    main(sys.argv)