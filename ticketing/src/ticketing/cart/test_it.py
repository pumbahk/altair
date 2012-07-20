# -*- coding:utf-8 -*-

import unittest


# Trueはすでにその席が抑えられていることをあらわす
SEAT_STATUSES = [
    [True,  False, True,  False, True,  False,], # A
    [False, False, True,  False, False, True,],  # B
    [False, False, False, True,  False, False,], # B
    [False, False, False, False, True,  False,], # B
    [False, False, False, False, False, True,],  # B
]

def _setup_db():
    from sqlalchemy import create_engine
    engine = create_engine("sqlite:///")
    # engine.echo = True
    import sqlahelper
    sqlahelper.add_engine(engine)
    from ticketing.core import models
    models.Base.metadata.create_all()
    return sqlahelper.get_session()

def _setup_performance(session):
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

    for ss in SEAT_STATUSES:
        seats = []
        for s in ss:
            # seat
            seat = c_m.Seat(venue=venue)
            # seat_status
            status = int(c_m.SeatStatusEnum.InCart) if s else int(c_m.SeatStatusEnum.Vacant)
            seat_status = c_m.SeatStatus(seat=seat, status=status)
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

    # seat_index

class ReserveSeatsTests(unittest.TestCase):
    """
    おまかせ席選択の連席バリエーションでのテスト
    """

    @classmethod
    def setUpClass(cls):
        cls.session = _setup_db()

    def setUp(self):
        _setup_performance(self.session)

    def tearDown(self):
        import transaction
        transaction.abort()
        self.session.remove()

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

    def test_1seat(self):
        """ 単席確保 """
        pass

    def test_2seats(self):
        """ 2連席確保 """
        pass

    def test_3seats(self):
        """ 3連席確保 """
        pass

    def test_4seats(self):
        """ 4連席確保 """
        pass
