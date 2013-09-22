#__table__ encoding: utf-8
import sys
import itertools
import logging
import argparse
import re

from sqlalchemy.orm import aliased
from sqlalchemy.sql import expression as sqlexpr
from sqlalchemy.sql.expression import func
from sqlalchemy.engine.base import Connection as _Connection
import sqlahelper
from paste.deploy import loadapp
from pyramid.paster import bootstrap, setup_logging

logger = logging.getLogger(__name__)

def message(msg, auxiliary=False):
    logger.log(auxiliary and logging.DEBUG or logging.INFO, msg)
    pad = '  ' if auxiliary else ''
    print >>sys.stderr, pad + msg

class MiniSeat(object):
    __slot__ = (
        'id',
        'l0_id',
        'venue_id',
        'row_l0_id',
        'seat_no',
        'name',
        )

    def __init__(self, id, l0_id, venue_id, row_l0_id, seat_no, name):
        self.id = id
        self.l0_id = l0_id
        self.venue_id = venue_id
        self.row_l0_id = row_l0_id
        self.seat_no = seat_no
        self.name = name

class MySet(set):
    def __init__(self, iterable, id=None, row_l0_id=None):
        super(MySet, self).__init__(iterable)
        self.id = id
        self.row_l0_id = row_l0_id

    def __hash__(self):
        return reduce(lambda x, y: x ^ hash(y), self, 0)

    # def add(self, item):
    #     self.append(item)

def get_pair_adjacencies_for(session, site):
    from altair.app.ticketing.core.models import SeatAdjacencySet, SeatAdjacency, Seat_SeatAdjacency, Venue, Seat
    i = session.query(Seat_SeatAdjacency.seat_adjacency_id, Seat.id, Seat.l0_id, Seat.venue_id, Seat.row_l0_id, Seat.seat_no, Seat.name) \
        .select_from(SeatAdjacencySet) \
        .join(SeatAdjacency, SeatAdjacencySet.id == SeatAdjacency.adjacency_set_id) \
        .join(Seat_SeatAdjacency, SeatAdjacency.id == Seat_SeatAdjacency.seat_adjacency_id) \
        .join(Venue, SeatAdjacencySet.site_id == Venue.site_id) \
        .join(Seat, (Venue.id == Seat.venue_id) & (Seat_SeatAdjacency.l0_id == Seat.l0_id)) \
        .filter(SeatAdjacencySet.site_id == site.id) \
        .filter(SeatAdjacencySet.seat_count == 2)

    seats = {}
    adjacencies = {}
    for record in i:
        pairs = adjacencies.setdefault(record[0], {})
        pair = pairs.setdefault(record[3], [])
        seat = seats.get(record[1])
        if seat is None:
            seat = seats[record[1]] = MiniSeat(*record[1:])
        pair.append(seat)

    return adjacencies

def numeric_seat_no(seat_no):
    # seat_no を数値に変換する
    # XXX: "10A" "10B" のような表記に対応できていない
    return long(seat_no)

def twenty_six(n):
    return reduce(lambda x, y: x * 26 + y, (int(d, 36) - 10 for d in n), 0)

def parse_l0_id_and_make_it_numeric(l0_id, prefix_base=26, num_base=10000, suffix_base=26):
    # s3-119-12 のような l0_id を数値に変換する
    value = 0L
    space = 1
    for g in re.finditer(r'([a-zA-Z]+)?([0-9]+)?([a-zA-Z]+)?', l0_id):
        prefix = g.group(1)
        num = g.group(2)
        suffix = g.group(3)

        if prefix:
            n = twenty_six(prefix)
            if n >= prefix_base:
                raise Exception('prefix_base too small')
            value = value * prefix_base + n
            space *= prefix_base
        if num:
            n = long(num, 10)
            if n >= num_base:
                raise Exception('num_base too small')
            value = value * num_base + n
            space *= num_base
        if suffix:
            n = twenty_six(suffix)
            if n >= suffix_base:
                raise Exception('prefix_base too small')
            value = value * suffix_base + n
            space *= suffix_base

    return value, space

def find_wrong_adjacencies(session, site):
    message('Getting adjacency data...')
    adjacencies = get_pair_adjacencies_for(session, site)
    message('Finding wrong adjacencies...')
    venues_to_be_compared = None
    wrong_adjacencies = {}
    used_venue_id = None
    for seat_adjacency_id, per_venue_adjacencies in adjacencies.iteritems():
        if venues_to_be_compared is None:
            venues_to_be_compared = set(per_venue_adjacencies)
        else:
            if venues_to_be_compared != set(per_venue_adjacencies):
                raise 'inconsistency found for SeatAdjacency.id={0}'.format(seat_adjacency_id)
        adjacency_to_be_compared = None
        for venue_id, adjacency in per_venue_adjacencies.iteritems():
            if adjacency_to_be_compared is None:
                if adjacency[0].row_l0_id != adjacency[1].row_l0_id:
                    raise 'inconsistency found for SeatAdjacency.id={0}'.format(seat_adjacency_id)
                adjacency_to_be_compared = set((seat.seat_no, seat.row_l0_id, seat.name, seat.l0_id) for seat in adjacency)
                used_venue_id = venue_id
            else:
                if adjacency_to_be_compared != set((seat.seat_no, seat.row_l0_id, seat.name, seat.l0_id) for seat in adjacency):
                    raise 'inconsistency found for SeatAdjacency.id={0}'.format(seat_adjacency_id)
        adjacency_to_be_compared = tuple(adjacency_to_be_compared)
        lhs_seat_no = numeric_seat_no(adjacency_to_be_compared[0][0])
        lhs_mapped_l0_id = parse_l0_id_and_make_it_numeric(adjacency_to_be_compared[0][3])
        rhs_seat_no = numeric_seat_no(adjacency_to_be_compared[1][0])
        rhs_mapped_l0_id = parse_l0_id_and_make_it_numeric(adjacency_to_be_compared[1][3])
        if lhs_seat_no > rhs_seat_no:
            if lhs_mapped_l0_id <= rhs_mapped_l0_id:
                raise 'discrepancy between l0_id and seat_no found for SeatAdjacency.id={0}'.format(seat_adjacency_id)
            adjacency_to_be_compared = (adjacency_to_be_compared[1], adjacency_to_be_compared[0])
            rhs_seat_no, lhs_seat_no = lhs_seat_no, rhs_seat_no 
        if rhs_seat_no - lhs_seat_no > 1:
            wrong_adjacencies.setdefault(adjacency_to_be_compared, []).append(seat_adjacency_id)
    return wrong_adjacencies, used_venue_id

def get_relevant_rows(session, used_venue_id, l0_id_list):
    from altair.app.ticketing.core.models import Seat
    relevant_rows = [
        row[0] for row in session.query(Seat.row_l0_id) \
            .select_from(Seat) \
            .filter(Seat.venue_id == used_venue_id) \
            .filter(Seat.l0_id.in_(l0_id_list)) \
            .distinct()
        ]
    return relevant_rows

def get_relevant_adjacencies(session, site, used_venue_id, relevant_rows):
    from altair.app.ticketing.core.models import SeatAdjacencySet, Seat_SeatAdjacency, SeatAdjacency, Seat
    q = session.query(SeatAdjacencySet.id, SeatAdjacencySet.seat_count, Seat_SeatAdjacency.seat_adjacency_id, Seat.l0_id, Seat.row_l0_id, Seat.seat_no) \
        .select_from(Seat_SeatAdjacency) \
        .join(SeatAdjacency, Seat_SeatAdjacency.seat_adjacency_id == SeatAdjacency.id) \
        .join(SeatAdjacencySet, SeatAdjacency.adjacency_set_id == SeatAdjacencySet.id) \
        .join(Seat, Seat_SeatAdjacency.l0_id == Seat.l0_id) \
        .filter(Seat.venue_id == used_venue_id) \
        .filter(SeatAdjacencySet.site_id == site.id) \
        .filter(Seat.row_l0_id.in_(relevant_rows))
    seat_adjacency_sets = {}
    for seat_adjacency_set_id, seat_count, seat_adjacency_id, l0_id, row_l0_id, seat_no in q:
        rec_per_seat_adjacency_set = seat_adjacency_sets.get(seat_adjacency_set_id)
        if rec_per_seat_adjacency_set is None:
            rec_per_seat_adjacency_set = seat_adjacency_sets[seat_adjacency_set_id] = {
                'id': seat_adjacency_set_id,
                'seat_count': seat_count,
                'adjacencies': {}
                }
        rec_per_row_l0_id = rec_per_seat_adjacency_set['adjacencies'].get(row_l0_id)
        if rec_per_row_l0_id is None:
            rec_per_row_l0_id = rec_per_seat_adjacency_set['adjacencies'][row_l0_id] = {}
        rec = rec_per_row_l0_id.get(seat_adjacency_id)
        if rec is None:
            rec = rec_per_row_l0_id[seat_adjacency_id] = MySet((), id=seat_adjacency_id, row_l0_id=row_l0_id)
        rec.add((l0_id, seat_no))

    for rec_per_seat_adjacency_set in seat_adjacency_sets.itervalues():
        for row_l0_id in rec_per_seat_adjacency_set['adjacencies']:
            x = rec_per_seat_adjacency_set['adjacencies'][row_l0_id] = list(rec_per_seat_adjacency_set['adjacencies'][row_l0_id].itervalues())
            assert all(len(y) == rec_per_seat_adjacency_set['seat_count'] for y in x), 'row_l0_id=%s, {%s}, seat_count=%d' % (row_l0_id, ', '.join('%s: %d' % (y.id, len(y)) for y in x), rec_per_seat_adjacency_set['seat_count'])

    return seat_adjacency_sets

def rebuild_adjacencies(relevant_adjacencies):
    l0_id_set_for_row_l0_id = {}
    seat_count_to_seat_adjacency_set = {}
    for rec_per_seat_adjacency_set in relevant_adjacencies.itervalues():
        seat_count_to_seat_adjacency_set[rec_per_seat_adjacency_set['seat_count']] = rec_per_seat_adjacency_set
        for row_l0_id, rec_per_row_l0_id in rec_per_seat_adjacency_set['adjacencies'].iteritems():
            l0_id_set = l0_id_set_for_row_l0_id.setdefault(row_l0_id, set())
            for adjacency in rec_per_row_l0_id:
                l0_id_set.update(adjacency)

    min_adjacency = min(seat_count_to_seat_adjacency_set)
    max_adjacency = max(seat_count_to_seat_adjacency_set)

    retval = {}
    for seat_count in range(min_adjacency, max_adjacency + 1):
        rec_per_seat_adjacency_set = seat_count_to_seat_adjacency_set[seat_count]
        seat_adjacency_set_id = rec_per_seat_adjacency_set['id']
        new_rec_per_seat_adjacency_set = retval.get(seat_adjacency_set_id)
        if new_rec_per_seat_adjacency_set is None:
            new_adjacencies = {}
            new_rec_per_seat_adjacency_set = retval[seat_adjacency_set_id] = {
                'id': rec_per_seat_adjacency_set['id'],
                'seat_count': seat_count,
                'adjacencies': new_adjacencies,
                }
        else:
            new_adjacencies = new_rec_per_seat_adjacency_set['adjacencies']

        for row_l0_id, seats_in_row in l0_id_set_for_row_l0_id.iteritems():
            rec_per_row_l0_id = []
            seats_in_row = sorted(seats_in_row, lambda a, b: cmp(numeric_seat_no(a[1]), numeric_seat_no(b[1])))
            for i in range(0, len(seats_in_row) - seat_count + 1):
                rec_per_row_l0_id.append(MySet(seats_in_row[i:i + seat_count], row_l0_id=row_l0_id))
            if rec_per_row_l0_id:
                new_adjacencies[row_l0_id] = rec_per_row_l0_id
    return retval

def diff_adjacencies(relevant_adjacencies, rebuilt_adjacencies):
    retval = {}
    for seat_adjacency_set_id, rec_per_seat_adjacency_set_for_rebuilt_adjacencies in rebuilt_adjacencies.iteritems():
        rec_per_seat_adjacency_set_for_relevant_adjacencies = relevant_adjacencies[seat_adjacency_set_id]
        adjacencies = {}
        for row_l0_id, adjacency_for_rebuilt_adjacency in rec_per_seat_adjacency_set_for_rebuilt_adjacencies['adjacencies'].iteritems():
            adjacency_for_rebuilt_adjacency = set(adjacency_for_rebuilt_adjacency)
            adjacency_for_relevant_adjacency = set(rec_per_seat_adjacency_set_for_relevant_adjacencies['adjacencies'][row_l0_id])
            adjacencies[row_l0_id] = {
                'added': adjacency_for_rebuilt_adjacency.difference(adjacency_for_relevant_adjacency),
                'removed': adjacency_for_relevant_adjacency.difference(adjacency_for_rebuilt_adjacency),
                }
        retval[seat_adjacency_set_id] = {
            'id': seat_adjacency_set_id,
            'seat_count': rec_per_seat_adjacency_set_for_rebuilt_adjacencies['seat_count'],
            'adjacencies': adjacencies,
            }
    return retval

def escape_param(dialect, value):
    if isinstance(value, basestring):
        return "'%s'" % value.replace("'", "''")
    else:
        return str(value) # XXX

def convert_placeholders(compiled_expr):
    stmt_str = str(compiled_expr)
    paramstyle = compiled_expr.dialect.paramstyle
    if paramstyle == 'named':
        named_param_re = r'\b(%s)\b' % '|'.join(compiled_expr.params)

    retval = []
    for token in re.finditer(r"""([^`'"]+)|(`(?:[^`]|``)*`)|('(?:[^']|\\'|'')*')|("(?:[^"]|\\"|"")*")""", stmt_str):
        unquoted = token.group(1)
        if unquoted is not None:
            if paramstyle == 'pyformat':
                unquoted = re.sub(r'%\(([^)]+)\)s', lambda g: '{%s}' % g.group(1), unquoted)
            elif paramstyle == 'qmark':
                counter = itertools.count(0)
                unquoted = re.sub(r'\?', lambda g: '{%d}' % counter.next(), unquoted)
            elif paramstyle == 'format':
                counter = itertools.count(0)
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
            for k in params
            ]
        named = {}
    else:
        positional = ()
        named = dict(
            (k, escape_param(compiled_expr.dialect, v))
            for k, v in params.items()
            )

    return convert_placeholders(compiled_expr).format(*positional, **named)

def build_sql_for_diff(session, diff):
    from altair.app.ticketing.core.models import SeatAdjacency, Seat_SeatAdjacency
    stmts = []
    for seat_adjacency_set_id, rec_per_seat_adjacency_set in diff.iteritems():
        for row_l0_id, adjacency_diffs in rec_per_seat_adjacency_set['adjacencies'].iteritems():
            for adjacency in adjacency_diffs['removed']:
                expr = sqlexpr.delete(Seat_SeatAdjacency.__table__, bind=session.bind) \
                    .where(Seat_SeatAdjacency.seat_adjacency_id == adjacency.id)
                stmts.append(render_sql(expr))
            for adjacency, existing_adjacency_id in zip(adjacency_diffs['added'], (existing_adjacency.id for existing_adjacency in adjacency_diffs['removed'])):
                for item in adjacency:
                    expr = sqlexpr.insert(Seat_SeatAdjacency.__table__, bind=session.bind) \
                        .values(
                            seat_adjacency_id=existing_adjacency_id,
                            l0_id=item[0]
                            )
                    stmts.append(render_sql(expr))
    return stmts

def fix_seat_adjacency(session, site_id):
    from altair.app.ticketing.core.models import Site
    site = session.query(Site).filter(Site.id == site_id).one()
    message(u"Processing site #{0.id} ({0.name})".format(site))
    wrong_adjacencies, used_venue_id = find_wrong_adjacencies(session, site)
    message(u"Wrong adjacencies:")
    for wrong_adjacency_pair, pair_seat_adjacency_ids in sorted(wrong_adjacencies.iteritems()):
        message(
            u"(row_l0_id={0[0][1]}, seat_no={0[0][0]}, name={0[0][2]}, l0_id={0[0][3]}) -- (row_l0_id={0[1][1]}, seat_no={0[1][0]}, name={0[1][2]}, l0_id={0[1][3]}): {1}".format(
                wrong_adjacency_pair,
                u', '.join(unicode(adjacency_id) for adjacency_id in pair_seat_adjacency_ids)
                ),
            True)
    relevant_rows = get_relevant_rows(
        session, used_venue_id,
        list(itertools.chain(*((x[3] for x in wrong_adjacency_pair) for wrong_adjacency_pair in wrong_adjacencies.iterkeys()))))
    relevant_adjacencies = get_relevant_adjacencies(session, site, used_venue_id, relevant_rows)
    rebuilt_adjacencies = rebuild_adjacencies(relevant_adjacencies)
    diff = diff_adjacencies(relevant_adjacencies, rebuilt_adjacencies)
    stmts = build_sql_for_diff(session, diff)
    print 'BEGIN;'
    for stmt in stmts:
        print stmt, ';'

def main(argv=sys.argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('config_uri', metavar='config', type=str,
                        help='config file')
    parser.add_argument('site_id', metavar='site_id', type=long, nargs='*',
                        help='site_id')

    args = parser.parse_args()

    setup_logging(args.config_uri)
    env = bootstrap(args.config_uri)
    request = env['request']

    session = sqlahelper.get_session()

    for site_id in args.site_id:
        fix_seat_adjacency(session, site_id)

if __name__ == '__main__':
    main()
