# -*- coding:utf-8 -*-

import argparse
import sys
import os
import logging
from datetime import datetime
from sqlalchemy.orm.exc import NoResultFound
from pyramid.paster import bootstrap, setup_logging
from altair import multilock
from altair.sqlahelper import get_global_db_session
from ..accounting.refund_report import (
    LOCK_NAME,
    build_refund_file,
    )
from ..datainterchange.api import get_famiport_file_manager_factory
from ..datainterchange.utils import make_room

logger = logging.getLogger(__name__)

def main(argv=sys.argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('-C', '--config', metavar='config', type=str, dest='config', required=True, help='config file')
    args = parser.parse_args(argv[1:])

    setup_logging(args.config)
    env = bootstrap(args.config)
    registry = env['registry']
    settings = registry.settings

    factory = get_famiport_file_manager_factory(registry)
    c = factory.get_configuration('refund')

    pending_dir = c['stage_dir']
    filename = c['filename']
    encoding = c['encoding'] or 'CP932'
    eor = c['eor'] or '\r\n'

    session = get_global_db_session(registry, 'famiport')

    now = datetime.now()

    datetime_dir_name = now.strftime("%Y%m%d")
    base_dir = os.path.join(pending_dir, datetime_dir_name)
    from ..models import FamiPortRefundEntry

    make_room(base_dir)
    try:
        os.mkdir(base_dir)
    except Exception as e:
        logger.error('failed to create directory %s (%s)' % (base_dir, e.message))
    path = os.path.join(base_dir, filename)
    try:
        with multilock.MultiStartLock(LOCK_NAME, engine=session.bind):
            refund_entries = session \
                .query(FamiPortRefundEntry) \
                .filter_by(report_generated_at=None) \
                .filter(FamiPortRefundEntry.refunded_at.isnot(None)) \
                .all()
            with open(path, 'w') as f:
                logger.info('writing refund records to %s...' % path)
                build_refund_file(f, refund_entries, encoding=encoding, eor=eor)
                logger.info('finished writing refund records')
                logger.info('reflecting changes to the database')
                for refund_entry in refund_entries:
                    refund_entry.report_generated_at = now
                session.commit()
    except multilock.AlreadyStartUpError as err:
        logger.warn('multi lock: {}'.format(repr(err)))
    except:
        import sys
        exc_info = sys.exc_info()
        try:
            logger.info('removing %s' % path)
            os.unlink(path)
        except:
            logger.exception('ignored exception')
        session.rollback()
        raise exc_info[1], None, exc_info[2]

if __name__ == u"__main__":
    main(sys.argv)
