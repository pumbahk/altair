# -*- coding:utf-8 -*-

import argparse
import sys
import logging
from pyramid.paster import bootstrap, setup_logging
from ..datainterchange.api import get_famiport_file_manager_factory

logger = logging.getLogger(__name__)

def main(argv=sys.argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('-C', '--config', required=True)
    args = parser.parse_args()

    setup_logging(args.config)
    env = bootstrap(args.config)
    registry = env['registry']

    sales_file_manager = get_famiport_file_manager_factory(registry)('sales')
    try:
        logger.info("sending sales file.")
        sales_file_manager.send_staged_file()
        sales_file_manager.mark_file_sent()
    except:
        sales_file_manager.mark_file_pending()

if __name__ == u"__main__":
    main(sys.argv)
