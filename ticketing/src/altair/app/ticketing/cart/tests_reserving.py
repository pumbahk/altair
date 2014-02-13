# -*- coding:utf-8 -*-

import unittest
import mock
from random import shuffle
from pyramid import testing
from altair.app.ticketing.testing import _setup_db as _setup_db_, _teardown_db
from altair.app.ticketing.core.testing import CoreTestMixin

def _setup_db(echo=False):
    return _setup_db_(
        modules=[
            'altair.app.ticketing.core.models',
            'altair.app.ticketing.cart.models',
            ],
        echo=echo
        )

class ReservingTest(unittest.TestCase, CoreTestMixin):
    def _getTarget(self):
        from .reserving import Reserving
        return Reserving

    def _makeOne(self):
        return self._getTarget()(self.request)

    def setUp(self):
        self.request = testing.DummyRequest()
        self.session = _setup_db()
        CoreTestMixin.setUp(self)
        from altair.app.ticketing.core.models import StockType
        self.stock_types = self._create_stock_types(3)
        self.stocks = self._create_stocks(self.stock_types)

    def test_get_vacant_seats_with_same_seat_index_pick_one(self):
        from altair.app.ticketing.core.models import (
            Seat,
            SeatStatus,
            SeatStatusEnum,
            SeatIndex,
            SeatIndexType,
            SeatAdjacency,
            SeatAdjacencySet,
            )
        target = self._makeOne()
        rows = []
        venue = self.performance.venue
        self.session.add(venue)
        seat_index_type = SeatIndexType(name='default', venue=venue)
        seat_adjacency_sets = []
        for n in range(2, 5):
            seat_adjacency_set = SeatAdjacencySet(
                seat_count=n,
                site=venue.site
                )
            self.session.add(seat_adjacency_set)
            seat_adjacency_sets.append(seat_adjacency_set)
        for row_no in range(0, 10):
            row = []
            for i, stock in enumerate(self.stocks):
                for col_no in range(i * 7, i * 7 + 7):
                    l0_id = '%02d-%02d' % (row_no, col_no)
                    seat = Seat(
                        name=l0_id,
                        l0_id=l0_id,
                        venue=venue,
                        stock=stock,
                        status_=SeatStatus(status=SeatStatusEnum.Vacant.v)
                        )
                    self.session.add(seat)
                    self.session.add(
                        SeatIndex(
                            seat=seat,
                            seat_index_type=seat_index_type,
                            index=1)
                        )
                    row.append(seat)
            for seat_adjacency_set in seat_adjacency_sets:
                n = seat_adjacency_set.seat_count
                for i in range(0, len(row) - n):
                    adjacency = SeatAdjacency(seats=row[i:i + n])
                    self.session.add(adjacency)
                    seat_adjacency_set.adjacencies.append(adjacency)
            rows.append(row)
        self.session.flush()
        for stock in self.stocks:
            for row in rows:
                for seat in row:
                    if seat.stock.id != stock.id:
                        continue
                    result = target.get_vacant_seats(stock.id, 1, seat_index_type.id)
                    self.assertEqual(len(result), 1, 'at %s' % seat.l0_id)
                    self.assertEqual(result[0].id, seat.id, '%s (%s) != %s (%s)' % (result[0].id, result[0].l0_id, seat.id, seat.l0_id))
                    result[0].status = SeatStatusEnum.InCart.v
                    self.session.flush()

    def test_get_vacant_seats_with_reversed_seat_index_pick_one(self):
        from altair.app.ticketing.core.models import (
            Seat,
            SeatStatus,
            SeatStatusEnum,
            SeatIndex,
            SeatIndexType,
            SeatAdjacency,
            SeatAdjacencySet,
            )
        target = self._makeOne()
        rows = []
        venue = self.performance.venue
        self.session.add(venue)
        seat_index_type = SeatIndexType(name='default', venue=venue)
        seat_adjacency_sets = []
        for n in range(2, 6):
            seat_adjacency_set = SeatAdjacencySet(
                seat_count=n,
                site=venue.site
                )
            self.session.add(seat_adjacency_set)
            seat_adjacency_sets.append(seat_adjacency_set)
        index = 100000 # a large enough number
        for row_no in range(0, 10):
            row = []
            for i, stock in enumerate(self.stocks):
                for col_no in range(i * 7, i * 7 + 7):
                    l0_id = '%02d-%02d' % (row_no, col_no)
                    seat = Seat(
                        name=l0_id,
                        l0_id=l0_id,
                        venue=venue,
                        stock=stock,
                        status_=SeatStatus(status=SeatStatusEnum.Vacant.v)
                        )
                    self.session.add(seat)
                    self.session.add(
                        SeatIndex(
                            seat=seat,
                            seat_index_type=seat_index_type,
                            index=index)
                        )
                    row.append(seat)
                    index -= 1
            for seat_adjacency_set in seat_adjacency_sets:
                n = seat_adjacency_set.seat_count
                for i in range(0, len(row) - n):
                    adjacency = SeatAdjacency(seats=row[i:i + n])
                    self.session.add(adjacency)
                    seat_adjacency_set.adjacencies.append(adjacency)
            rows.append(row)
        self.session.flush()
        for stock in self.stocks:
            for row in reversed(rows):
                for seat in reversed(row):
                    if seat.stock.id != stock.id:
                        continue
                    result = target.get_vacant_seats(stock.id, 1, seat_index_type.id)
                    self.assertEqual(len(result), 1, 'at %s' % seat.l0_id)
                    self.assertEqual(result[0].id, seat.id, '%s (%s) != %s (%s)' % (result[0].id, result[0].l0_id, seat.id, seat.l0_id))
                    result[0].status = SeatStatusEnum.InCart.v
                    self.session.flush()

    def test_get_vacant_seats_with_same_seat_index_pick_adjacent(self):
        from altair.app.ticketing.core.models import (
            Seat,
            SeatStatus,
            SeatStatusEnum,
            SeatIndex,
            SeatIndexType,
            SeatAdjacency,
            SeatAdjacencySet,
            )
        target = self._makeOne()
        rows = []
        venue = self.performance.venue
        self.session.add(venue)
        seat_index_type = SeatIndexType(name='default', venue=venue)
        seat_adjacency_sets = []
        for n in range(2, 6):
            seat_adjacency_set = SeatAdjacencySet(
                seat_count=n,
                site=venue.site
                )
            self.session.add(seat_adjacency_set)
            seat_adjacency_sets.append(seat_adjacency_set)
        for row_no in range(0, 10):
            row = []
            for i, stock in enumerate(self.stocks):
                for col_no in range(i * 7, i * 7 + 7):
                    l0_id = '%02d-%02d' % (row_no, col_no)
                    seat = Seat(
                        name=l0_id,
                        l0_id=l0_id,
                        venue=venue,
                        stock=stock,
                        status_=SeatStatus(status=SeatStatusEnum.Vacant.v)
                        )
                    self.session.add(seat)
                    self.session.add(
                        SeatIndex(
                            seat=seat,
                            seat_index_type=seat_index_type,
                            index=1)
                        )
                    row.append(seat)
            for seat_adjacency_set in seat_adjacency_sets:
                n = seat_adjacency_set.seat_count
                for i in range(0, len(row) - n):
                    adjacency = SeatAdjacency(seats=row[i:i + n])
                    self.session.add(adjacency)
                    seat_adjacency_set.adjacencies.append(adjacency)
            rows.append(row)
        self.session.flush()
        for seat_adjacency_set in seat_adjacency_sets:
            n = seat_adjacency_set.seat_count
            for stock in self.stocks:
                for row in rows:
                    for i in range(0, len(row)):
                        if any((i + j >= len(row) \
                                  or row[i + j].stock.id != stock.id \
                                  or row[i + j].status != SeatStatusEnum.Vacant.v)
                                for j in range(0, n)):
                            continue
                        seats = row[i:i + n]
                        result = target.get_vacant_seats(stock.id, n, seat_index_type.id)
                        result = sorted(result, lambda a, b: cmp(a.l0_id, b.l0_id))
                        seats = sorted(seats, lambda a, b: cmp(a.l0_id, b.l0_id))
                        self.assertEqual(len(result), n, 'at %s' % seat.l0_id)
                        for got, expected in zip(result, seats):
                            self.assertEqual(got.id, expected.id, '%s (%s) != %s (%s)' % (got.id, ', '.join(seat.l0_id for seat in result), expected.id, ', '.join(seat.l0_id for seat in seats)))
                        for seat in result:
                            seat.status = SeatStatusEnum.InCart.v
                        self.session.flush()
            for row in rows:
                for seat in row:
                    seat.status = SeatStatusEnum.Vacant.v
            self.session.flush()

    def test_get_vacant_seats_with_reversed_seat_index_pick_adjacent(self):
        from altair.app.ticketing.core.models import (
            Seat,
            SeatStatus,
            SeatStatusEnum,
            SeatIndex,
            SeatIndexType,
            SeatAdjacency,
            SeatAdjacencySet,
            )
        target = self._makeOne()
        rows = []
        venue = self.performance.venue
        self.session.add(venue)
        seat_index_type = SeatIndexType(name='default', venue=venue)
        seat_adjacency_sets = []
        for n in range(2, 6):
            seat_adjacency_set = SeatAdjacencySet(
                seat_count=n,
                site=venue.site
                )
            self.session.add(seat_adjacency_set)
            seat_adjacency_sets.append(seat_adjacency_set)
        index = 100000 # a large enough number
        for row_no in range(0, 10):
            row = []
            for i, stock in enumerate(self.stocks):
                for col_no in range(i * 7, i * 7 + 7):
                    l0_id = '%02d-%02d' % (row_no, col_no)
                    seat = Seat(
                        name=l0_id,
                        l0_id=l0_id,
                        venue=venue,
                        stock=stock,
                        status_=SeatStatus(status=SeatStatusEnum.Vacant.v)
                        )
                    self.session.add(seat)
                    self.session.add(
                        SeatIndex(
                            seat=seat,
                            seat_index_type=seat_index_type,
                            index=index)
                        )
                    row.append(seat)
                    index -= 1
            for seat_adjacency_set in seat_adjacency_sets:
                n = seat_adjacency_set.seat_count
                for i in range(0, len(row) - n + 1):
                    adjacency = SeatAdjacency(seats=row[i:i + n])
                    self.session.add(adjacency)
                    seat_adjacency_set.adjacencies.append(adjacency)
            rows.append(row)
        self.session.flush()
        for seat_adjacency_set in seat_adjacency_sets:
            n = seat_adjacency_set.seat_count
            for stock in self.stocks:
                for row in reversed(rows):
                    for i in range(len(row) - 1, -1, -1):
                        if any((i + j >= len(row) \
                                  or row[i + j].stock.id != stock.id \
                                  or row[i + j].status != SeatStatusEnum.Vacant.v)
                                for j in range(0, n)):
                            continue
                        seats = row[i:i + n]
                        result = target.get_vacant_seats(stock.id, n, seat_index_type.id)
                        result = sorted(result, lambda a, b: cmp(a.l0_id, b.l0_id))
                        seats = sorted(seats, lambda a, b: cmp(a.l0_id, b.l0_id))
                        self.assertEqual(len(result), n, 'at %s' % seat.l0_id)
                        for got, expected in zip(result, seats):
                            self.assertEqual(got.id, expected.id, '%s (%s) != %s (%s)' % (got.id, ', '.join(seat.l0_id for seat in result), expected.id, ', '.join(seat.l0_id for seat in seats)))
                        for seat in result:
                            seat.status = SeatStatusEnum.InCart.v
                        self.session.flush()
            for row in rows:
                for seat in row:
                    seat.status = SeatStatusEnum.Vacant.v
            self.session.flush()

    def test_get_vacant_seats_with_random_seat_index_pick_adjacent(self):
        from altair.app.ticketing.core.models import (
            Seat,
            SeatStatus,
            SeatStatusEnum,
            SeatIndex,
            SeatIndexType,
            SeatAdjacency,
            SeatAdjacencySet,
            )
        from .reserving import NotEnoughAdjacencyException
        target = self._makeOne()
        rows = []
        venue = self.performance.venue
        self.session.add(venue)
        seat_index_type = SeatIndexType(name='default', venue=venue)
        seat_adjacency_sets = []
        for n in range(2, 6):
            seat_adjacency_set = SeatAdjacencySet(
                seat_count=n,
                site=venue.site
                )
            self.session.add(seat_adjacency_set)
            seat_adjacency_sets.append(seat_adjacency_set)
        indexes = list(range(0, 10 * 7 * len(self.stocks)))
        shuffle(indexes)
        indexes_iter = iter(indexes)
        seats_by_index = {}
        for row_no in range(0, 10):
            row = []
            for i, stock in enumerate(self.stocks):
                for col_no in range(i * 7, i * 7 + 7):
                    l0_id = '%02d-%02d' % (row_no, col_no)
                    index = indexes_iter.next()
                    seat = Seat(
                        name=l0_id,
                        l0_id=l0_id,
                        venue=venue,
                        stock=stock,
                        status_=SeatStatus(status=SeatStatusEnum.Vacant.v)
                        )
                    self.session.add(seat)
                    self.session.add(
                        SeatIndex(
                            seat=seat,
                            seat_index_type=seat_index_type,
                            index=index)
                        )
                    seats_by_index[index] = (row_no, col_no, seat)
                    row.append(seat)
            for seat_adjacency_set in seat_adjacency_sets:
                n = seat_adjacency_set.seat_count
                for i in range(0, len(row) - n + 1):
                    adjacency = SeatAdjacency(seats=row[i:i + n])
                    self.session.add(adjacency)
                    seat_adjacency_set.adjacencies.append(adjacency)
            rows.append(row)
        self.session.flush()

        def seat_description(seats):
            return ', '.join('%s (status=%d, stock_id=%d) [%s]' % (
                seat.l0_id,
                seat.status,
                seat.stock_id,
                ', '.join(
                    str(seat_index.index)
                    for seat_index in seat.indexes
                    )
                )
                for seat in seats
                )

        for seat_adjacency_set in seat_adjacency_sets:
            n = seat_adjacency_set.seat_count
            for stock in self.stocks:
                seat_iter = (seats_by_index[i] for i in range(0, len(seats_by_index)) if seats_by_index[i][2].stock.id == stock.id)
                for index, (row_no, i, seat) in enumerate(seat_iter):
                    row = rows[row_no]
                    possible_adjacencies = set(
                        adjacency
                        for adjacency in seat.adjacencies
                        if adjacency.adjacency_set.seat_count == n and \
                           all(
                            seat.status == SeatStatusEnum.Vacant.v and \
                            seat.stock_id == stock.id
                            for seat in adjacency.seats
                            )
                        )
                    if not possible_adjacencies:
                        continue
                    adjacencies_description = ' / '.join(
                        'adjacency #%d: %s' % (
                            adjacency.id,
                            seat_description(adjacency.seats)
                            )
                        for adjacency in possible_adjacencies
                        )
                    try:
                        result = target.get_vacant_seats(stock.id, n, seat_index_type.id)
                        result = sorted(result, lambda a, b: cmp(a.l0_id, b.l0_id))
                        self.assertTrue(True)
                    except NotEnoughAdjacencyException:
                        self.fail(adjacencies_description)

                    self.assertEqual(len(result), n, 'at %s' % seat.l0_id)
                    seats_set = []
                    for adjacency in possible_adjacencies:
                        seats = sorted(adjacency.seats, lambda a, b: cmp(a.l0_id, b.l0_id))
                        if set(seat.l0_id for seat in seats) == set(seat.l0_id for seat in result):
                            seats_set.append(seats)
                    self.assertTrue(
                        len(seats_set) > 0,
                        '%s -- %s' % (
                            seat_description(result),
                            adjacencies_description
                            )
                        )
                    for seat in result:
                        seat.status = SeatStatusEnum.InCart.v
                    self.session.flush()
            for row in rows:
                for seat in row:
                    seat.status = SeatStatusEnum.Vacant.v
            self.session.flush()

