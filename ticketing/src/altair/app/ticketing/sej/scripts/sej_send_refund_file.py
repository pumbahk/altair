# -*- coding:utf-8 -*-

import argparse
import sys
import logging.config
from dateutil import parser as date_parser
from datetime import datetime
from pyramid.paster import bootstrap, setup_logging
from pyramid.request import Request

def main(argv=sys.argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('-C', '--config')
    args = parser.parse_args()

    setup_logging(args.config)
    env = bootstrap(args.config)
    registry = env['registry']
    from ..refund import send_refund_files
    now = datetime.now()
    send_refund_files(registry, now)

if __name__ == u"__main__":
    main(sys.argv)
