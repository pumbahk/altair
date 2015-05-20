# -*- coding:utf-8 -*-

import argparse
import sys
import os
import logging
from datetime import date
from pyramid.paster import bootstrap, setup_logging
from altair.app.ticketing.famiport.data_interchange.file_transfer import FTPSFileSender

logger = logging.getLogger(__name__)

def main(argv=sys.argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('-C', '--config')
    args = parser.parse_args()

    setup_logging(args.config)
    env = bootstrap(args.config)
    registry = env['registry']
    settings = registry.settings
    sales_file_dir = settings['altair.famiport.sales_file.dir']

    today = date.today()
    sales_file_name = 'sales_file_' + str(today) + '.csv'
    sales_file_path = os.path.join(sales_file_dir, sales_file_name)

    host = settings['altair.famiport.send_file.ftp.host']
    username = settings['altair.famiport.send_file.ftp.username']
    password = settings['altair.famiport.send_file.ftp.password']
    upload_dir_path = settings['altair.famiport.send_file.ftp.upload_dir_path']

    logger.info('Sending sales file in %s to %s' % (sales_file_dir, host))
    with open(sales_file_path) as f:
        sender.send_file(os.path.join(upload_dir_path, sales_file_name), f)

if __name__ == u"__main__":
    main(sys.argv)
