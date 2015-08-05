# -*- coding:utf-8 -*-

import argparse
import sys
import logging
from pyramid.paster import bootstrap, setup_logging
from altair import multilock
from altair.sqlahelper import get_global_db_session
from ..datainterchange.api import get_famiport_file_manager_factory
from ..accounting.refund_report import LOCK_NAME

logger = logging.getLogger(__name__)
# TODO Test
def main(argv=sys.argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('-C', '--config', required=True)
    args = parser.parse_args()

    setup_logging(args.config)
    env = bootstrap(args.config)
    registry = env['registry']
    session = get_global_db_session(registry, 'famiport')
    refund_file_manager = get_famiport_file_manager_factory(registry)('refund')
    logger.info("sending refund file.")

    timeout = 60 * 60  # 1H
    try:
        with multilock.MultiStartLock(LOCK_NAME, timeout=timeout, engine=session.bind):
            refund_file_manager.send_staged_file()
    except multilock.AlreadyStartUpError as err:
        logger.warn('multi lock: {}'.format(repr(err)))
    except:
        logger.exception('error occurred during sending file.')
        raise

if __name__ == u"__main__":
    main(sys.argv)
