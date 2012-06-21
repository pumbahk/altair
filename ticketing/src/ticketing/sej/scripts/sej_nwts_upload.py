# -*- coding:utf-8 -*-

#
# NWTS for python
#

import optparse
import sys
import sqlahelper

from datetime import datetime
from dateutil import parser as date_parser
from os.path import abspath, dirname

from ticketing.sej.nwts import nws_data_send
sys.path.append(abspath(dirname(dirname(__file__))))

from paste.deploy import loadapp

import logging

logging.basicConfig()
log = logging.getLogger(__file__)

def main(argv=sys.argv):

    session = sqlahelper.get_session()
    session.configure(autocommit=True, extension=[])

    parser = optparse.OptionParser(
        description=__doc__,
        usage='%prog [options]',
    )

    parser.add_option('-t', '--type',
        dest='type',
        help='tpayback.asp or ttemplate.asp',
        metavar='FILE'
    )
    parser.add_option('-f', '--file',
        dest='file',
        help='select',
        metavar='FILE'
    )
    options, args = parser.parse_args(argv[1:])

    parser.add_option('-c', '--config',
        dest='config',
        help='Path to configuration file (defaults to $CWD/development.ini)',
        metavar='FILE'
    )
    type = options.type

    if type is None or (type != 'tpayback.asp' and type != 'ttemplate.asp'):
        print 'You must set type tpayback.asp or ttemplate.asp'
        return

    # configuration
    config = options.config
    if config is None:
        print 'You must give a config file'
        return

    file = options.file
    if file is None:
        print 'You must set filename'
        return

    data = open(file).read()

    app = loadapp('config:%s' % config, 'main')
    settings = app.registry.settings

    nwts_hostname           = settings['sej.nwts.hostname ']
    terminal_id             = settings['sej.terminal_id']
    password                = settings['sej.password']

    url = nwts_hostname + "/" + type
    nws_data_send(url=url, data=data, file_id='SDMT010U', terminal_id=terminal_id, password=password)

if __name__ == u"__main__":
    main(sys.argv)