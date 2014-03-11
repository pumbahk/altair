# encoding: utf-8
import sys
import itertools
import logging
import argparse
import re
import csv

from sqlalchemy.orm import aliased
from sqlalchemy.sql import expression as sqlexpr
from sqlalchemy.sql.expression import func
from sqlalchemy.engine.base import Connection as _Connection
import sqlahelper
from paste.deploy import loadapp
from pyramid.paster import bootstrap, setup_logging

logger = logging.getLogger(__name__)

eagles_seat_types = {
    u'プレステージ': u'プレステージ',
    u'プレステージ･プラチナ': u'プレステージ・プラチナ',
    u'プレステージ・プラチナ': u'プレステージ・プラチナ',
    u'プレステージ･ラウンジ': u'プレステージ･ラウンジ',
    u'プレステージ・ラウンジ': u'プレステージ・ラウンジ',
    u'プレステージ･ラウンジBOX4': u'ラウンジBOX4',
    u'プレステージ・ラウンジBOX4': u'ラウンジBOX4',
    u'ラウンジBOX4': u'ラウンジBOX4',
    u'プレステージ･エキサイト': u'プレステージ・エキサイト',
    u'プレステージ・エキサイト': u'プレステージ・エキサイト',
    u'プレステージ･エキサイトセブン': u'プレステージ・エキサイトセブン',
    u'プレステージ・エキサイトセブン': u'プレステージ・エキサイトセブン',
    u'ゴールデンシート1塁側': u'ゴールデンシート1塁側',
    u'ゴールデンシート3塁側': u'ゴールデンシート3塁側',
    u'フィールドシート1塁側': u'フィールドシート1塁側',
    u'フィールドシート3塁側': u'フィールドシート3塁側',
    u'イーグルシート1塁側': u'イーグルシート1塁側',
    u'イーグルシート3塁側': u'イーグルシート3塁側',
    u'3階スーパーイーグルシート1塁側': u'3階スーパーイーグルシート1塁側',
    u'3階スーパーイーグルシート3塁側': u'3階スーパーイーグルシート3塁側',
    u'4階クラブシート1塁側': u'4階クラブシート1塁側',
    u'4階クラブシート3塁側': u'4階クラブシート3塁側',
    u'5階クラブシート1塁側': u'5階クラブシート1塁側',
    u'5階車椅子席1塁側': u'内野車椅子席1塁側',
    u'セブン-イレブン・グループシート5': u'セブン-イレブン・グループシート5',
    u'コカ･コーラボックスシート5': u'コカ・コーラボックスシート5',
    u'コカ・コーラボックスシート5': u'コカ・コーラボックスシート5',
    u'レフトEウィングペアシート': u'レフトEウイングペアシート',
    u'レフトEウイングペアシート': u'レフトEウイングペアシート',
    u'ライトEウィング4': u'ライトEウイング4',
    u'ライトEウイング4': u'ライトEウイング4',
    u'内野1塁側ペアシート': u'内野1塁側ペアシート',
    u'内野指定席1塁側A': u'内野指定席1塁側A',
    u'内野席1塁側A': u'内野指定席1塁側A',
    u'内野指定席1塁側B': u'内野指定席1塁側B',
    u'内野席1塁側B': u'内野指定席1塁側B',
    u'内野指定席1塁側S': u'内野指定席1塁側S',
    u'内野席1塁側S': u'内野指定席1塁側S',
    u'内野指定席3塁側A': u'内野指定席3塁側A',
    u'内野席3塁側A': u'内野指定席3塁側A',
    u'内野指定席3塁側B': u'内野指定席3塁側B',
    u'内野席3塁側B': u'内野指定席3塁側B',
    u'内野指定席3塁側S': u'内野指定席3塁側S',
    u'内野席3塁側S': u'内野指定席3塁側S',
    u'内野指定席3塁側上段': u'内野指定席3塁側上段',
    u'内野席3塁側上段': u'内野指定席3塁側上段',
    u'内野車椅子席1塁側': u'内野車椅子席1塁側',
    u'内野車椅子席3塁側': u'内野車椅子席3塁側',
    u'外野ライトペアシート': u'外野ライト・ペアシート',
    u'外野ライト･ペアシート': u'外野ライト・ペアシート',
    u'外野ライト・ペアシート': u'外野ライト・ペアシート',
    u'外野ライトトリプルシート': u'外野ライトトリプルシート',
    u'外野ライト･トリプルシート': u'外野ライト・トリプルシート',
    u'外野ライト・トリプルシート': u'外野ライト・トリプルシート',
    u'外野指定席レフト': u'外野指定席レフト',
    u'外野指定席ライト': u'外野指定席ライト',
    u'外野車椅子席レフト': u'外野車椅子席レフト',
    u'外野自由エリア': u'外野自由エリア',
    u'バックネット裏ペアシート': u'バックネット裏ペアシート',
    u'バックネット裏ボックスシート5上段': u'バックネット裏ボックスシート5',
    u'バックネット裏ボックスシート5中段': u'バックネット裏ボックスシート5',
    }


class ApplicationException(Exception):
    pass

import locale
charset = locale.getpreferredencoding()

def message(msg, auxiliary=False):
    logger.log(auxiliary and logging.DEBUG or logging.INFO, msg)
    pad = '  ' if auxiliary else ''
    print >>sys.stderr, (pad + msg).encode(charset)

class MySet(set):
    def __init__(self, iterable, id=None, row_l0_id=None):
        super(MySet, self).__init__(iterable)
        self.id = id
        self.row_l0_id = row_l0_id

    def __hash__(self):
        return reduce(lambda x, y: x ^ hash(y), self, 0)

    # def add(self, item):
    #     self.append(item)

def parse_eagles_seat_name(name):
    g = re.match(ur'^(?P<gate>(?:HP|[LR][A-Z0-9]+)(?:/(?:HP|[LR][A-Z0-9]+))*)\s+(?P<block>[0-9A-Za-z]+)(?:\s+(?P<row_1>[0-9]+|車椅子)列\s+(?P<column_1>[0-9]+)番|(?:\s+|-)?(?P<row_2>[0-9]+)-(?P<column_2>[0-9]+))', name)
    if g is None:
        raise ApplicationException(u'Unsupported seat name format: %s' % name)
    return dict(
        gate=g.group('gate'),
        block=g.group('block'),
        row=g.group('row_1') or g.group('row_2'),
        column=g.group('column_1') or g.group('column_2')
        )

def compose_seat_locator(parsed_name):
    return u'%s-%s-%s' % (
        parsed_name['block'],
        parsed_name['row'],
        parsed_name['column'],
        )

def gen_sql(session, file, venue_id, src_stock_holder_names=None, dest_stock_holder_name=u'年間シート', encoding=None):
    from altair.app.ticketing.core.models import (
        Venue, Seat, Stock, StockType, StockHolder, StockStatus, Event, Performance,
        )
    if encoding is None:
        encoding = 'utf-8'
    venue = session.query(Venue).filter_by(id=venue_id).one()
    message(u'start processing venue(id=%s, name=%s)' % (venue.id, venue.name))
    stock_types_by_name = {}
    stock_types_by_id = {}
    q = session.query(StockType.id, StockType.name, StockType) \
        .join(Performance, Performance.event_id == StockType.event_id) \
        .join(Venue, Venue.performance_id == Performance.id) \
        .outerjoin(Stock, (Stock.stock_type_id == StockType.id) & (Stock.performance_id == Venue.performance_id)) \
        .filter(Venue.id == venue_id)
    for stock_type_id, stock_type_name, stock_type in q:
        stock_types_by_name[stock_type_name] = stock_type
        stock_types_by_id[stock_type_id] = stock_type

    src_seat_stock_sets = {}
    q = session.query(StockHolder.id, StockHolder.name, StockType.id, Stock) \
        .join(Stock.stock_type) \
        .outerjoin(Stock.stock_holder) \
        .join(Venue, Venue.performance_id == Stock.performance_id) \
        .filter(Venue.id == venue_id)
    if src_stock_holder_names is not None:
        q = q.filter(StockHolder.name.in_(src_stock_holder_names))
    for stock_holder_id, stock_holder_name, stock_type_id, stock in q:
        stocks = src_seat_stock_sets.get(stock_type_id)
        if stocks is None:
            stocks = src_seat_stock_sets[stock_type_id] = {}
        stocks[stock_holder_id] = (stock_holder_name, stock)

    dest_seat_stocks = dict(
        session.query(StockType.id, Stock) \
            .join(Stock.stock_type) \
            .outerjoin(Stock.stock_holder) \
            .join(Venue, Venue.performance_id == Stock.performance_id) \
            .filter(Venue.id == venue_id) \
            .filter(StockHolder.name == dest_stock_holder_name)
            )
    if not dest_seat_stocks:
        raise ApplicationException(u'no such stock holder named %s' % dest_stock_holder_name)

    stmts = []
    seats_by_locator = {}
    q = session.query(Seat.id, Seat.l0_id, Seat.name, Stock.id, StockHolder.id, StockHolder.name, StockType) \
        .join(Stock, Seat.stock_id == Stock.id) \
        .join(StockType, Stock.stock_type_id == StockType.id) \
        .join(StockHolder, Stock.stock_holder_id == StockHolder.id) \
        .filter(Seat.venue_id == venue_id)
    for seat_id, l0_id, name, stock_id, stock_holder_id, stock_holder_name, stock_type in q:
        locator = compose_seat_locator(parse_eagles_seat_name(name))
        record = seats_by_locator.get(locator)
        if record is not None:
            raise ApplicationException(u'seat with the same locator already exists: locator=%s, seat_id=%ld, l0_id=%s' % (locator, seat_id, l0_id))
        seats_by_locator[locator] = dict(
            id=seat_id,
            l0_id=l0_id,
            name=name,
            stock_id=stock_id,
            stock_holder_name=stock_holder_name,
            stock_type=stock_type
            )
    seats_to_move_per_stock_type = dict(
        (stock_type.id, [])
        for stock_type in stock_types_by_id.values()
        )
    f = open(file)
    r = csv.reader(f)
    try:
        headers = dict((i, col.decode(encoding)) for i, col in enumerate(r.next()))
        for line_no, csv_row in enumerate(r, 2):
            columns = dict((headers[i], csv_column.decode(encoding)) for i, csv_column in enumerate(csv_row))
            locator = columns[u'席番']
            seat_type_name = columns.get(u'席種') or columns.get(u'単券席種')
            message(u'processing line %d: seat_type=%s, locator=%s' % (line_no, seat_type_name, locator))
            seat = seats_by_locator.get(locator)
            if seat is None:
                message('cannot locate a seat by %s (%s) in %s at line %d. skip.' % (locator, seat_type_name, file, line_no))
                continue
            stock_type_name = eagles_seat_types.get(seat_type_name)
            stock_type = None
            if stock_type_name is not None:
                stock_type = stock_types_by_name.get(stock_type_name)
            if stock_type is None:
                message('cannot find a seat type named %s at line %d. skip.' % (seat_type_name, line_no))
                continue
            message('seat %s (stock_holder_name=%s) will be moved to %s' % (seat['name'], seat['stock_holder_name'], dest_stock_holder_name), auxiliary=True)
            seats_to_move_per_stock_type[stock_type.id].append(seat)
    finally:
        f.close()

    for stock_type_id, seats in seats_to_move_per_stock_type.items():
        message(u'number of seats to move for %s: %d' % (stock_types_by_id[stock_type_id].name, len(seats)))
        if not seats:
            continue
        stock_type = stock_types_by_id[stock_type_id]
        stmts.append(u'-- %s' % stock_type.name)
        src_seat_stocks = src_seat_stock_sets.get(stock_type_id)
        if src_seat_stocks is None:
            raise ApplicationException(u'%s has no corresponding source Stock' % stock_type.name)
        dest_seat_stock = dest_seat_stocks.get(stock_type_id)
        if dest_seat_stock is None:
            raise ApplicationException(u'%s has no corresponding destination Stock' % stock_type.name)
        moved_seats_per_stock = {}
        for seat in seats:
            applicable_seat_stocks = [stock for stock_holder_id, (stock_holder_name, stock) in src_seat_stocks.items() if seat['stock_id'] == stock.id]
            if len(applicable_seat_stocks) == 0:
                raise ApplicationException(u'seat (seat_id=%s, l0_id=%s) does not belong to any one of stock holders (name=%s) (actual: %s)' % (seat_id, l0_id, u', '.join(v[0] for v in src_seat_stocks.values()), seat['stock_holder_name']))
            assert len(applicable_seat_stocks) == 1
            applicable_seat_stock = applicable_seat_stocks[0]
            if applicable_seat_stock.id != dest_seat_stock.id:
                stmts.append(
                    render_sql(
                        sqlexpr.update(
                            Seat.__table__,
                            values=dict(stock_id=dest_seat_stock.id),
                            whereclause=(Seat.id == seat['id'])
                            )
                        )
                    )
                moved_seats_per_stock[seat['stock_id']] = moved_seats_per_stock.get(seat['stock_id'], 0) + 1
        for old_stock_id, moved_seat_count in moved_seats_per_stock.items():
            stmts.append(
                render_sql(
                    sqlexpr.update(
                        StockStatus.__table__,
                        values=dict(
                            quantity=(StockStatus.quantity - moved_seat_count)
                            ),
                        whereclause=(StockStatus.stock_id == old_stock_id)
                        )
                    )
                )
            stmts.append(
                render_sql(
                    sqlexpr.update(
                        Stock.__table__,
                        values=dict(
                            quantity=(Stock.quantity - moved_seat_count)
                            ),
                        whereclause=(Stock.id == old_stock_id)
                        )
                    )
                )
        total_number_of_moved_seats = sum(moved_seats_per_stock.values())
        stmts.append(
            render_sql(
                sqlexpr.update(
                    StockStatus.__table__,
                    values=dict(
                        quantity=(StockStatus.quantity + total_number_of_moved_seats)
                        ),
                    whereclause=(StockStatus.stock_id == dest_seat_stock.id)
                    )
                )
            )
        stmts.append(
            render_sql(
                sqlexpr.update(
                    Stock.__table__,
                    values=dict(
                        quantity=(Stock.quantity + len(seats))
                        ),
                    whereclause=(Stock.id == dest_seat_stock.id)
                    )
                )
            )
    return stmts

def escape_param(dialect, value):
    if value is None:
        return "NULL"
    elif isinstance(value, basestring):
        return "'%s'" % value.replace("'", "''")
    else:
        return str(value) # XXX

def convert_placeholders(compiled_expr):
    stmt_str = str(compiled_expr)
    paramstyle = compiled_expr.dialect.paramstyle
    if paramstyle == 'named':
        named_param_re = r'\b(%s)\b' % '|'.join(compiled_expr.params)

    retval = []
    counter = itertools.count(0)
    for token in re.finditer(r"""([^`'"]+)|(`(?:[^`]|``)*`)|('(?:[^']|\\'|'')*')|("(?:[^"]|\\"|"")*")""", stmt_str):
        unquoted = token.group(1)
        if unquoted is not None:
            if paramstyle == 'pyformat':
                unquoted = re.sub(r'%\(([^)]+)\)s', lambda g: '{%s}' % g.group(1), unquoted)
            elif paramstyle == 'qmark':
                unquoted = re.sub(r'\?', lambda g: '{%d}' % counter.next(), unquoted)
            elif paramstyle == 'format':
                unquoted = re.sub(r'%s', lambda g: '{%d}' % counter.next(), unquoted)
            elif paramstyle == 'numeric':
                unquoted = re.sub(r':(\d+)', lambda g: '{%d}' % (int(g.group(1)) - 1), unquoted)
            elif paramstyle == 'named':
                unquoted = re.sub(named_param_re, lambda g: '{%s}' % g.group(1), unquoted)
            retval.append(unquoted)
        else:
            retval.append(token.group(0))

    return ''.join(retval)

def render_sql(expr):
    compiled_expr = expr.compile()
    params = compiled_expr.params
    if compiled_expr.dialect.positional:
        positional = [
            escape_param(compiled_expr.dialect, params[k])
            for k in compiled_expr.positiontup
            ]
        named = {}
    else:
        positional = ()
        named = dict(
            (k, escape_param(compiled_expr.dialect, v))
            for k, v in params.items()
            )

    return convert_placeholders(compiled_expr).format(*positional, **named)

def main(argv=sys.argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('file', metavar='file', type=str)
    parser.add_argument('venue_id', metavar='venue_id', type=long, nargs='*',
                        help='venue_id')
    parser.add_argument('--src-stock-holder-name', metavar='src_stock_holder_name', action='append', type=str, default=[])
    parser.add_argument('--dest-stock-holder-name', metavar='dest_stock_holder_name', type=str, default=u'年間シート'.encode(charset))
    parser.add_argument('--config', metavar='config', type=str)
    parser.add_argument('--encoding', metavar='encoding', type=str)
    args = parser.parse_args()

    setup_logging(args.config)
    env = bootstrap(args.config)
    request = env['request']

    session = sqlahelper.get_session()

    stmts = []
    if not args.src_stock_holder_name:
        src_stock_holder_names = None
    else:
        src_stock_holder_names = [
            unicode(src_stock_holder_name, charset)
            for src_stock_holder_name in args.src_stock_holder_name
            ]
    try:
        for venue_id in args.venue_id:
            stmts.extend(gen_sql(
                session,
                args.file,
                venue_id=venue_id,
                src_stock_holder_names=src_stock_holder_names,
                dest_stock_holder_name=unicode(args.dest_stock_holder_name, charset),
                encoding=args.encoding))
    except ApplicationException as e:
        message(e.message) 
        return
    print 'BEGIN;'
    for stmt in stmts:
        print stmt.encode(charset), ';'

if __name__ == '__main__':
    main()

# vim: sts=4 sw=4 ts=4 et ai
