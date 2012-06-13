# -*- coding:utf-8 -*-

#
# SEJとの外部結合の為に使ったスクリプト
#

import optparse
import sys
import sqlahelper

from dateutil.parser import parse
from os.path import abspath, dirname

from ticketing.sej.models import SejCancelEvent
from ticketing.sej.payment import request_fileget, request_cancel_event
from ticketing.sej.resources import SejNotificationType, code_from_notification_type, SejServerError

sys.path.append(abspath(dirname(dirname(__file__))))

from paste.deploy import loadapp

import logging

logging.basicConfig()
log = logging.getLogger(__file__)

import os

def cancel_event():

    request_cancel_event(SejCancelEvent.all())




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

    sej_hostname = settings['sej.inticket_api_hostname']

    cancel_event()

if __name__ == u"__main__":
    main(sys.argv)