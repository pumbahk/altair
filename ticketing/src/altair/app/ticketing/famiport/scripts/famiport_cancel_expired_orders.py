# encoding: utf-8
import sys
import logging
import argparse
from datetime import datetime
from pyramid.paster import bootstrap, setup_logging
from altair.multilock import (
    MultiStartLock,
    AlreadyStartUpError,
    )
from altair.sqlahelper import get_db_session
from altair.timeparse import parse_time_spec
from altair.app.ticketing.famiport.interfaces import IFamiPortOrderAutoCompleter
from altair.app.ticketing.famiport.canceller import FamiPortOrderCanceller

logger = logging.getLogger(__file__)

LOCK_NAME = __name__

def main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser()
    parser.add_argument('-C', '--config', metavar='config', type=str, dest='config', required=True, help='config file')
    args = parser.parse_args(argv)

    setup_logging(args.config)

    env = bootstrap(args.config)
    request = env['request']
    session = get_db_session(request, 'famiport')

    canceller = FamiPortOrderCanceller(request, session)
    logger.info('famiport order canceller start')
    try:
        now = datetime.now()
        with MultiStartLock(LOCK_NAME, engine=session.bind):
            canceller(now)
    except AlreadyStartUpError as err:
        logger.warn('{}'.format(repr(err)))
    logger.info('famiport order canceller end')

if __name__ == u"__main__":
    sys.exit(main())

