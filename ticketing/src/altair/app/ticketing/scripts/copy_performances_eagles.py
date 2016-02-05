#!/usr/bin/env python
# encoding: utf-8
import os
import sys
import logging
import transaction
import itertools
import logging
import argparse
import re
import csv
import locale
from datetime import time, date, datetime, timedelta
from dateutil.parser import parse as parsedate

from pyramid.paster import bootstrap, setup_logging

from sqlalchemy import func, or_, and_
from sqlalchemy.sql.expression import not_
from sqlalchemy.orm.exc import NoResultFound

import sqlahelper

from altair.app.ticketing.events.sales_segments.resources import SalesSegmentAccessor

logger = logging.getLogger(__name__)

formats = {
    'csv': csv.excel,
    'tsv': csv.excel_tab,
    }

class ApplicationException(Exception):
    pass

charset = locale.getpreferredencoding()

def message(msg, auxiliary=False):
    logger.log(auxiliary and logging.DEBUG or logging.INFO, msg)
    pad = '  ' if auxiliary else ''
    print >>sys.stderr, (pad + msg).encode(charset)

class RecordError(ApplicationException):
    @property
    def message(self):
        return self.args[0]
 
    @property
    def lineno(self):
        return self.args[1]
 
    def __str__(self):
        return '%s at line %d' % (self.message, self.lineno)

def combine_date_time(date_, time_):
    return datetime(year=date_.year, month=date_.month, day=date_.day,
                    hour=time_.hour, minute=time_.minute, second=time_.second,
                    microsecond=time_.microsecond)

def do_performance_copy(request, session, file_, encoding, format, dry_run=False):
    from altair.app.ticketing.core.models import Performance, PerformanceSetting
    now = datetime.now()
    f = open(file_)
    r = csv.reader(f, dialect=format)
    headers = [col.decode(encoding) for col in r.next()]
    l = 0

    def new_record_error(msg):
        raise RecordError(msg, l)

    def parse_int(s, msg):
        s = s.strip()
        if not s:
            return None
        try:
            return int(s)
        except (ValueError, TypeError):
            raise new_record_error('%s: %s' % (msg, s))

    def parse_long(s, msg):
        s = s.strip()
        if not s:
            return None
        try:
            return long(s)
        except (ValueError, TypeError):
            raise new_record_error('%s: %s' % (msg, s))

    def parse_date(s, msg, default_year=None):
        s = s.strip()
        if not s:
            return None
        g = re.match(u'(?:(?P<year>\d+)年)?(?P<month>\d+)月(?P<day>\d+)日', s)
        if g is not None:
            return date(
                year=parse_int(g.group('year'), msg) if g.group('year') else default_year,
                month=parse_int(g.group('month'), msg),
                day=parse_int(g.group('day'), msg)
                )
        try:
            return parsedate(s).date()
        except:
            raise new_record_error('%s: %s' % (msg, s))

    def parse_time(s, msg):
        s = s.strip()
        if not s:
            return None
        g = re.match(u'(?P<hour>\d+)時(?P<minute>\d+)分?', s)
        if g is not None:
            return time(
                hour=parse_int(g.group('hour'), msg),
                minute=parse_int(g.group('minute'), msg),
                second=0
                )
        try:
            return parsedate(s).time()
        except:
            raise new_record_error('%s: %s' % (msg, s))

    def get_performance(performance_id, title=None):
        try:
            perf = session.query(Performance).filter_by(id=performance_id).one()
        except NoResultFound:
            raise new_record_error('no such performance: %d' % performance_id)
        if title and perf.name != title:
            raise new_record_error('performance(id=%d).title differs from %s' % (performance_id, title))
        return perf

    def generate_performance_code(performance):
        return '%s%02d%02dZ' % (performance.code[0:7], performance.start_on.month, performance.start_on.day)

    for l, row in enumerate(r, 2):
        try:
            cols = dict((headers[i], col.decode(encoding)) for i, col in enumerate(row))
            src_performance_name = cols[u'コピー元公演名']
            src_performance_id = parse_long(cols[u'コピー元パフォーマンスID'], 'invalid performance id')
            new_performance_name = cols[u'公演名']
            new_performance_code = cols.get(u'公演コード')
            new_performance_date = parse_date(cols[u'試合開催日'], 'invalid performance date', default_year=now.year)
            new_performance_open_time = parse_time(cols[u'開場時間'], 'invalid open time')
            new_performance_start_time = parse_time(cols[u'開演時間'], 'invalid start time')
            new_performance_open_at = combine_date_time(new_performance_date, new_performance_open_time)
            new_performance_start_at = combine_date_time(new_performance_date, new_performance_start_time)
            new_performance_abbreviated_title = cols[u'公演名略称']
            new_performance_subtitle = cols[u'公演名副題']
            new_performance_subtitle4 = cols[u'公演名副題4']
            new_note = cols[u'公演名備考']
            new_performance_display_order = parse_int(cols[u'表示順'], 'invalid display order')
            new_performance_max_orders = parse_int(cols[u'購入回数制限'], 'invalid max orders')
            new_performance_max_quantity_per_user = parse_int(cols[u'購入上限枚数 (購入者毎)'], 'invalid max quantity')

            src_performance = get_performance(src_performance_id, title=src_performance_name)
            src_performance_name = src_performance.name

            if new_performance_code is None:
                new_performance_code = generate_performance_code(src_performance)

            message('copying Performance(id=%d, title=%s)' % (src_performance_id, src_performance_name))

            if not dry_run:
                new_performance = Performance.clone(src_performance)
                new_performance.original_id = src_performance.id
                new_performance.venue_id = src_performance.venue.id
                new_performance.create_venue_id = src_performance.venue.id
                new_performance.open_on = new_performance_open_at
                new_performance.start_on = new_performance_start_at
                new_performance.name = new_performance_name
                new_performance.subtitle = new_performance_subtitle
                new_performance.subtitle4 = new_performance_subtitle4
                new_performance.note = new_note
                new_performance.abbreviated_title = new_performance_abbreviated_title
                new_performance.code = new_performance_code
                new_performance.display_order = new_performance_display_order
                new_performance.setting = PerformanceSetting(
                    order_limit=new_performance_max_orders,
                    max_quantity_per_user=new_performance_max_quantity_per_user
                    )
                new_performance.save()
                accessor = SalesSegmentAccessor()
                for sales_segment in new_performance.sales_segments:
                    accessor.update_sales_segment(sales_segment)
                session.flush()
                message('new performance: Performance(id=%d, title=%s, code=%s)' % (new_performance.id, new_performance.name, new_performance.code))
            message('end copying Performance(id=%d, title=%s)' % (src_performance_id, src_performance_name))
            transaction.commit()
        except:
            transaction.abort()
            raise

def main(argv=sys.argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('file', metavar='file', type=str)
    parser.add_argument('--config', metavar='config', type=str)
    parser.add_argument('--encoding', metavar='encoding', type=str)
    parser.add_argument('--format', metavar='format', type=str, default='csv')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()

    setup_logging(args.config)
    env = bootstrap(args.config)
    request = env['request']

    session = sqlahelper.get_session()

    format = formats.get(args.format)
    if format is None:
        message("unknown format: %s" % format)
        return 255

    try:
        try:
            do_performance_copy(
                request,
                session,
                file_=args.file,
                encoding=args.encoding,
                format=formats[args.format],
                dry_run=args.dry_run
                )
        except ApplicationException as e:
            message(str(e))
            raise
    except:
        raise
    return 0

if __name__ == '__main__':
    sys.exit(main())

# vim: sts=4 sw=4 ts=4 et ai
