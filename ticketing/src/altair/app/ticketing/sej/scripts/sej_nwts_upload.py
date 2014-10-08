# -*- coding:utf-8 -*-

#
# NWTS for python
#

import optparse
import sys
import logging.config
from dateutil import parser as date_parser
from pyramid.paster import bootstrap, setup_logging

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
    setup_logging(config)
    registry = env['registry']

    from ..interfaces import ISejTenant
    from ..api import get_nwts_uploader_factory
    default_tenant = registry.queryUtility(ISejTenant)
    uploader = get_nwts_uploader_factory(env['registry'])(
        endpoint_url=default_tenant.nwts_endpoint_url,
        terminal_id=default_tenant.nwts_terminal_id,
        password=default_tenant.nwts_password
        )
    uploader(application=type, data=data, file_id=file)

if __name__ == u"__main__":
    main(sys.argv)
