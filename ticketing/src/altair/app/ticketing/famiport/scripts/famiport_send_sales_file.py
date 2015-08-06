# -*- coding:utf-8 -*-

import argparse
import sys
import logging
from pyramid.paster import bootstrap, setup_logging
from altair import multilock
from altair.sqlahelper import get_global_db_session
from ..datainterchange.api import get_famiport_file_manager_factory
from .famiport_make_sales_file import LOCK_NAME

logger = logging.getLogger(__name__)

def main(argv=sys.argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('-C', '--config', required=True)
    args = parser.parse_args()

    setup_logging(args.config)
    env = bootstrap(args.config)
    registry = env['registry']
    session = get_global_db_session(registry, 'famiport')
    timeout = 60 * 60  # 1H

    sales_file_manager = get_famiport_file_manager_factory(registry)('sales')
    logger.info("sending sales file.")
    try:
        with multilock.MultiStartLock(LOCK_NAME, timeout=timeout, engine=session.bind):
            sales_file_manager.send_staged_file()
    except multilock.AlreadyStartUpError as err:
        logger.warn('multi lock: {}'.format(repr(err)))
    except:
        logger.exception('error occurred during sending file.')
        raise

if __name__ == u"__main__":
    main(sys.argv)
