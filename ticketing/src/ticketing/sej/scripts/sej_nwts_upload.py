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

    type = options.type
    #print type == 'tpayback.asp'
    if type is None or (type != 'tpayback.asp' and type != 'ttemplate.asp'):
        print 'You must set type tpayback.asp or ttemplate.asp'
        return

    file = options.file
    if file is None:
        print 'You must set filename'
        return

    data = open(file).read()

    terminal_id = '60022000'
    password = '60022a'
    url = 'http://sv2.ticketstar.jp/test.php'
    #url = 'http://incp.r1test.com/cpweb/master/ul/ttemplate.asp'
    nws_data_send(url=url, data=data, file_id='SDMT010U', terminal_id=terminal_id, password=password)

if __name__ == u"__main__":
    main(sys.argv)