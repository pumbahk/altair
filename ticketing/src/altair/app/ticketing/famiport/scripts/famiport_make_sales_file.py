# -*- coding:utf-8 -*-

import argparse
import sys
import os
import logging
from datetime import datetime, timedelta
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import orm
from sqlalchemy import sql
from pyramid.paster import bootstrap, setup_logging
from dateutil.parser import parse as parsedatetime
from altair.sqlahelper import get_global_db_session
from ..accounting.sales_report import build_sales_record
from ..datainterchange.api import get_famiport_file_manager_factory
from ..datainterchange.utils import make_room

def parse_start_and_end_date(args, now):
    start_date = None
    end_date = None

    if args.start_date:
        try:
            start_date = parsedatetime(args.start_date)
        except:
            sys.stderr.write("Invalid date: %s\n" % args.start_date)
            sys.stderr.flush()
            sys.exit(255)

    if args.end_date:
        try:
            end_date = parsedatetime(args.end_date)
        except:
            sys.stderr.write("Invalid date: %s\n" % args.end_date)
            sys.stderr.flush()
            sys.exit(255)

    if args.date:
        if start_date is not None or end_date is not None:
            sys.stderr.write("(--start-date|--end-date) and --date are mutually exclusive")
            sys.exit(255)
        try:
            date = parsedatetime(args.date)
        except:
            sys.stderr.write("Invalid date: %s\n" % args.date)
            sys.stderr.flush()
            sys.exit(255)
    else:
        if start_date is None and end_date is None:
            date = now - timedelta(days=1)

    if start_date is None and end_date is None:
        start_date = date
        end_date = date + timedelta(days=1)

    return start_date, end_date

logger = logging.getLogger(__name__)

def main(argv=sys.argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('-C', '--config', metavar='config', type=str, dest='config', required=True, help='config file')
    parser.add_argument('-s', '--start-date', required=False)
    parser.add_argument('-e', '--end-date', required=False)
    parser.add_argument('-d', '--date', required=False)
    args = parser.parse_args(argv[1:])

    now = datetime.now().replace(hour=0, minute=0, second=0)
    start_date, end_date = parse_start_and_end_date(args, now)

    setup_logging(args.config)
    env = bootstrap(args.config)
    registry = env['registry']
    settings = registry.settings

    factory = get_famiport_file_manager_factory(registry)
    c = factory.get_configuration('sales')

    pending_dir = c['stage_dir']
    filename = c['filename']
    encoding = c['encoding'] or 'CP932'
    eor = c['eor'] or '\r\n'

    session = get_global_db_session(registry, 'famiport')

    datetime_dir_name = now.strftime("%Y%m%d")
    base_dir = os.path.join(pending_dir, datetime_dir_name)
    from ..models import FamiPortRefundEntry

    make_room(base_dir)
    try:
        os.mkdir(base_dir)
    except Exception as e:
        logger.error('failed to create directory %s (%s)' % (base_dir, e.message))
    path = os.path.join(base_dir, filename)
    from ..models import FamiPortOrder, FamiPortReceipt
    try:
        orders = session.query(FamiPortOrder) \
            .options(orm.joinedload(FamiPortOrder.famiport_receipts)) \
            .join(FamiPortOrder.famiport_receipts) \
            .filter(
                sql.or_(
                    sql.and_(
                        FamiPortReceipt.completed_at >= start_date,
                        FamiPortReceipt.completed_at < end_date
                        ),
                    sql.and_(
                        FamiPortReceipt.canceled_at >= start_date,
                        FamiPortReceipt.canceled_at < end_date
                        )
                    )
                ) \
            .all()
        with open(path, 'w') as f:
            logger.info('writing sales records to %s...' % path)
            receipts = build_sales_record(f, orders, start_date, end_date, encoding=encoding, eor=eor)
            logger.info('finished writing sales records')
            logger.info('reflecting changes to the database')
            for receipt in receipts:
                receipt.report_generated_at = now
            for order in orders:
                order.report_generated_at = now
            session.commit()
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


