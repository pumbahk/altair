# -*- coding:utf-8 -*-

#
# NWTS for python
#

import optparse
import sys
import logging.config
from dateutil import parser as date_parser
from pyramid.paster import bootstrap
from altair.app.ticketing.sej.nwts import nws_data_send


def main(argv=sys.argv):
    '''
    NWTS アップローダー
      ex) 払戻ファイル転送
        python sej_nwts_upload.py payback.zip -c ticketing.ini -t tpayback.asp -f SEIT020U
      ex) テンプレートファイル転送
        python sej_nwts_upload.py payback.zip -c ticketing.ini -t tpayback.asp -f SDMT010U
    '''

    parser = optparse.OptionParser(
        description=__doc__,
        usage='%prog [options]',
    )

    parser.add_option('-t', '--type',
        dest='type',
        help='tpayback.asp or ttemplate.asp',
        metavar='TYPE'
    )
    parser.add_option('-f', '--file',
        dest='file',
        help='File ID (SDMT010U|SEIT020U|TEST010U)',
        metavar='FILEID'
    )
    parser.add_option('-c', '--config',
        dest='config',
        help='Path to configuration file (defaults to $CWD/development.ini)',
        metavar='CONFIG'
    )

    options, args = parser.parse_args(argv[1:])

    type = options.type

    if type is None or type not in ('tpayback.asp', 'ttemplate.asp'):
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

    if file not in ('SDMT010U', 'SEIT020U', 'TEST010U'):
        print 'File ID must be SDMT010U (template upload), SEIT020U (refund) or TEST010U (test)'
        return

    data = open(args[0]).read()

    env = bootstrap(config)
    logging.config.fileConfig(config)

    settings = env['registry'].settings

    nwts_url                = settings['sej.nwts.url']
    terminal_id             = settings['sej.terminal_id']
    password                = settings['sej.password']
    ca_certs                = settings.get('sej.nwts.ca_certs', None)
    cert_file               = settings.get('sej.nwts.cert_file', None)
    key_file                = settings.get('sej.nwts.key_file', None)

    url = nwts_url + "/" + type
    nws_data_send(url=url, data=data, file_id=options.file, terminal_id=terminal_id, password=password, ca_certs=ca_certs, cert_file=cert_file, key_file=key_file)

if __name__ == u"__main__":
    main(sys.argv)
