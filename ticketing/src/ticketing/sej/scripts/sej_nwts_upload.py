# -*- coding:utf-8 -*-

#
# NWTS for python
#

import optparse
import sys

from datetime import datetime
from dateutil import parser as date_parser
from os.path import abspath, dirname

from ticketing.sej.nwts import nws_data_send
from pyramid.paster import bootstrap

import logging.config

def main(argv=sys.argv):
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
    parser.add_option('-c', '--config',
        dest='config',
        help='Path to configuration file (defaults to $CWD/development.ini)',
        metavar='FILE'
    )

    options, args = parser.parse_args(argv[1:])

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

    env = bootstrap(config)
    logging.config.fileConfig(config)

    settings = env['registry'].settings

    nwts_hostname           = settings['sej.nwts.hostname']
    terminal_id             = settings['sej.terminal_id']
    password                = settings['sej.password']

    url = nwts_hostname + "/" + type
    nws_data_send(url=url, data=data, file_id='SDMT010U', terminal_id=terminal_id, password=password)

if __name__ == u"__main__":
    main(sys.argv)
