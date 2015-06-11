# -*- coding:utf-8 -*-

import argparse
import sys
import logging
from pyramid.paster import bootstrap, setup_logging
from ..datainterchange.filetransfer import FamiPortFileManager, FamiPortFileType

logger = logging.getLogger(__name__)

def main(argv=sys.argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('-C', '--config')
    args = parser.parse_args()

    setup_logging(args.config)
    env = bootstrap(args.config)
    registry = env['registry']

    sales_file_manager = FamiPortFileManager(registry, FamiPortFileType.SALES)
    try:
        logger.info("sending sales file.")
        sales_file_manager.send_staged_file(FamiPortFileType.SALES)
        sales_file_manager.mark_file_sent()
    except:
        sales_file_manager.mark_file_pending()

if __name__ == u"__main__":
    main(sys.argv)
