# -*- coding:utf-8 -*-

import unittest
from pyramid import testing

# Trueはすでにその席が抑えられていることをあらわす
SEAT_STATUSES = [
    [True,  False, True,  False, True,  False,], # A
    [False, False, True,  False, False, True,],  # B
    [False, False, False, True,  False, False,], # C
    [False, False, False, False, True,  False,], # D
    [False, False, False, False, False, True,],  # E
]

ROWS = ['A', 'B', 'C', 'D', 'E']

def _setup_db():
    from sqlalchemy import create_engine
    engine = create_engine("sqlite:///")
    #engine.echo = True
    import sqlahelper
    sqlahelper.add_engine(engine)
    from ticketing.core import models
    models.Base.metadata.create_all()
    return sqlahelper.get_session()

def _setup_performance(session):
    """ 席データまでの必要なデータをすべて作成 """

    import itertools
    import ticketing.core.models as c_m
    # organization
    org = c_m.Organization()
    # event
    event = c_m.Event(organization=org)
    # performance
    performance = c_m.Performance(event=event)
    # site
    site = c_m.Site()
    # venue
    venue = c_m.Venue(site=site, organization=org, performance=performance)
    # stock_hodler
    stock_holder = c_m.StockHolder(event=event)
    # stock_type
    stock_type = c_m.StockType()

    # stock
    stock = c_m.Stock(performance=performance, stock_holder=stock_holder, 
        stock_type=stock_type,
        quantity=len([s for s in itertools.chain(*SEAT_STATUSES)]))
    # stock_status
    stock_status = c_m.StockStatus(stock=stock, quantity=len([s for s in itertools.chain(*SEAT_STATUSES) if not s]))

    # 連席情報
    # 2連席
    # seat_adjacency_set
    seat_adjacency_sets = {}
    for seat_count in range(2, 5):
        seat_adjacency_sets[seat_count] = c_m.SeatAdjacencySet(venue=venue, seat_count=seat_count)

    seat_index_type = c_m.SeatIndexType(venue=venue, name='testing')
    for seat_index_index, (row, ss) in enumerate(zip(ROWS, SEAT_STATUSES)):
        seats = []
        for i, s in enumerate(ss):
            # seat
            seat = c_m.Seat(venue=venue, stock=stock, name=u"%s-%s" % (row, i+1))
            # seat_status
            status = int(c_m.SeatStatusEnum.InCart) if s else int(c_m.SeatStatusEnum.Vacant)
            seat_status = c_m.SeatStatus(seat=seat, status=status)
            seat_index = c_m.SeatIndex(seat=seat, index=seat_index_index, seat_index_type=seat_index_type)
            seats.append(seat)
        # seat_adjacency
        for seat_count in range(2, 5):
            adjacenced_seats = zip(*[seats[i:] for i in range(seat_count)])
            seat_adjacency_set = seat_adjacency_sets[seat_count]
            for adjacenced in adjacenced_seats:
                seat_adjacency = c_m.SeatAdjacency(adjacency_set=seat_adjacency_set,
                    seats=list(adjacenced))


    session.add(org)
    session.flush()

    return stock.id

class ReserveSeatsTests(unittest.TestCase):
    """
    おまかせ席選択の連席バリエーションでのテスト
    """

    @classmethod
    def setUpClass(cls):
        cls.session = _setup_db()

    def setUp(self):
        self.stock_id = _setup_performance(self.session)

    def tearDown(self):
        import transaction
        transaction.abort()
        self.session.remove()

    def _getTarget(self):
        from .reserving import Reserving
        return Reserving

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_prepare(self):
        """ 生成データの確認 """
        import ticketing.core.models as c_m
        self.assertEqual(c_m.Seat.query.count(), 30)
        self.assertEqual(c_m.Seat.query.filter(
                    c_m.SeatStatus.status==int(c_m.SeatStatusEnum.Vacant)
                ).filter(
                    c_m.SeatStatus.seat_id==c_m.Seat.id
                ).count(), 
            22)
        self.assertEqual(c_m.SeatAdjacency.query.count(), 60)
        self.assertEqual(c_m.SeatStatus.query.filter(c_m.SeatStatus.status==int(c_m.SeatStatusEnum.InCart)).count(),
            8)

    def test_1seat(self):
        """ 単席確保 """
        request = testing.DummyRequest()
        target = self._makeOne(request)

        result = target.get_vacant_seats(self.stock_id, 1)

    def _reserve_all_seats(self):
        import ticketing.core.models as c_m
        ss = c_m.SeatStatus.query.all()
        for s in ss:
            s.status = int(c_m.SeatStatusEnum.InCart)

    def test_2seats_without_vacant_seats(self):
        """ 2連席確保 """
        from ticketing.cart.reserving import NotEnoughAdjacencyException
        self._reserve_all_seats()

        request = testing.DummyRequest()
        target = self._makeOne(request)

        self.assertRaises(NotEnoughAdjacencyException, target.get_vacant_seats, self.stock_id, 2)

    def test_2seats(self):
        """ 2連席確保 """
        request = testing.DummyRequest()
        target = self._makeOne(request)

        result = target.get_vacant_seats(self.stock_id, 2)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].name, 'B-1')
        self.assertEqual(result[1].name, 'B-2')

    def test_3seats(self):
        """ 3連席確保 """
        request = testing.DummyRequest()
        target = self._makeOne(request)

        result = target.get_vacant_seats(self.stock_id, 3)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0].name, 'C-1')

    def test_4seats(self):
        """ 4連席確保 """
        request = testing.DummyRequest()
        target = self._makeOne(request)

        result = target.get_vacant_seats(self.stock_id, 4)
        self.assertEqual(len(result), 4)
        self.assertEqual(result[0].name, 'D-1')

    def test_reserve(self):
        import ticketing.core.models as c_m
        request = testing.DummyRequest()
        target = self._makeOne(request)
        seats = c_m.Seat.query.filter(c_m.Seat.name.in_([u'B-1', u'C-1', u'E-1'])).all()

        result = target._reserve(seats)
        self.assertEqual(len(result), len(seats))

        for s in result:
            self.assertEqual(s.status, int(c_m.SeatStatusEnum.InCart))

    def test_reserve_seats(self):
        import ticketing.core.models as c_m
        request = testing.DummyRequest()
        target = self._makeOne(request)
        result = target.reserve_seats(self.stock_id, 2)

        self.assertEqual(len(result), 2)

        statuses = c_m.SeatStatus.query.filter(c_m.SeatStatus.seat_id.in_([s.id for s in result])).all()
        self.assertEqual(len(statuses), 2)

        for s in statuses:
            self.assertEqual(s.status, int(c_m.SeatStatusEnum.InCart))

        statuses = c_m.SeatStatus.query.filter(c_m.SeatStatus.status==int(c_m.SeatStatusEnum.InCart)).all()
        self.assertEqual(len(statuses), 2 + 8)
        
            

    def test_reserve_2seats_twice(self):
        """ 2連席連続確保 """
        import ticketing.core.models as c_m
        request = testing.DummyRequest()
        target = self._makeOne(request)
        result = target.reserve_seats(self.stock_id, 2)
        self.assertEqual(result[0].name, 'B-1')
        self.assertEqual(result[1].name, 'B-2')
        result = target.reserve_seats(self.stock_id, 2)
        self.assertEqual(result[0].name, 'B-4')
        self.assertEqual(result[1].name, 'B-5')

    def test_reserve_seats_3times(self):
        """ 4 -> 3 -> 2 連席連続確保 """
        import ticketing.core.models as c_m
        request = testing.DummyRequest()
        target = self._makeOne(request)
        result = target.reserve_seats(self.stock_id, 4)
        self.assertEqual(result[0].name, 'D-1')
        self.assertEqual(result[1].name, 'D-2')
        self.assertEqual(result[2].name, 'D-3')
        self.assertEqual(result[3].name, 'D-4')
        result = target.reserve_seats(self.stock_id, 3)
        self.assertEqual(result[0].name, 'C-1')
        self.assertEqual(result[1].name, 'C-2')
        self.assertEqual(result[2].name, 'C-3')
        result = target.reserve_seats(self.stock_id, 2)
        self.assertEqual(result[0].name, 'B-1')
        self.assertEqual(result[1].name, 'B-2')


    def test_reserve_2seats_until_sold_out(self):
        import ticketing.core.models as c_m
        from ticketing.cart.reserving import NotEnoughAdjacencyException
        request = testing.DummyRequest()
        target = self._makeOne(request)

        for i in range(8):
            target.reserve_seats(self.stock_id, 2)
        self.assertRaises(NotEnoughAdjacencyException, target.reserve_seats, self.stock_id, 2)

    def test_reserve_3seats_until_sold_out(self):
        import ticketing.core.models as c_m
        from ticketing.cart.reserving import NotEnoughAdjacencyException
        request = testing.DummyRequest()
        target = self._makeOne(request)

        for i in range(3):
            target.reserve_seats(self.stock_id, 3)
        self.assertRaises(NotEnoughAdjacencyException, target.reserve_seats, self.stock_id, 3)
        for i in range(4):
            target.reserve_seats(self.stock_id, 2)
        self.assertRaises(NotEnoughAdjacencyException, target.reserve_seats, self.stock_id, 2)
