# -*- coding:utf-8 -*-

import unittest
from pyramid import testing
from ..testing import _setup_db as _setup_db_, _teardown_db

def _setup_db(echo=False):
    return _setup_db_(
        modules=[
            'altair.app.ticketing.core.models',
            ],
        echo=echo
        )

# Trueはすでにその席が抑えられていることをあらわす
SEAT_STATUSES = [
    [True,  False, True,  False, True,  False,], # A
    [False, False, True,  False, False, True,],  # B
    [False, False, False, True,  False, False,], # C
    [False, False, False, False, True,  False,], # D
    [False, False, False, False, False, True,],  # E
]

ROWS = ['A', 'B', 'C', 'D', 'E']


def _setup_performance(session):
    """ 席データまでの必要なデータをすべて作成 """

    import itertools
    import altair.app.ticketing.core.models as c_m
    # organization
    org = c_m.Organization(code="TEST", short_name='testing')
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
        seat_adjacency_sets[seat_count] = c_m.SeatAdjacencySet(site=venue.site, seat_count=seat_count)

    seat_index_type = c_m.SeatIndexType(venue=venue, name='testing')
    for seat_index_index, (row, ss) in enumerate(zip(ROWS, SEAT_STATUSES)):
        seats = []
        for i, s in enumerate(ss):
            # seat
            seat = c_m.Seat(venue=venue, stock=stock, name=u"%s-%s" % (row, i+1), l0_id=u"%s-%s" % (row, i+1))
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

class ReservingTests(unittest.TestCase):
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
        import altair.app.ticketing.core.models as c_m
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
        self.assertEqual(result[0].name, 'A-2')

    def _reserve_all_seats(self):
        import altair.app.ticketing.core.models as c_m
        ss = c_m.SeatStatus.query.all()
        for s in ss:
            s.status = int(c_m.SeatStatusEnum.InCart)

    def test_2seats_without_vacant_seats(self):
        """ 2連席確保 """
        from altair.app.ticketing.core.models import SeatStatusEnum
        from altair.app.ticketing.cart.reserving import NotEnoughAdjacencyException
        self._reserve_all_seats()

        request = testing.DummyRequest()
        target = self._makeOne(request)

        self.assertRaises(NotEnoughAdjacencyException, target.get_vacant_seats, self.stock_id, 2)

    def test_2seats(self):
        """ 2連席確保 """
        from altair.app.ticketing.core.models import SeatStatusEnum
        request = testing.DummyRequest()
        target = self._makeOne(request)

        result = target.get_vacant_seats(self.stock_id, 2)

        self.assertEqual(len(result), 2)
        self.assertTrue(all(seat.status == SeatStatusEnum.Vacant.v for seat in result))
        self.assertEqual(result[0].name, 'B-1')
        self.assertEqual(result[1].name, 'B-2')

    def test_3seats(self):
        """ 3連席確保 """
        from altair.app.ticketing.core.models import SeatStatusEnum
        request = testing.DummyRequest()
        target = self._makeOne(request)

        result = target.get_vacant_seats(self.stock_id, 3)
        self.assertEqual(len(result), 3)
        self.assertTrue(all(seat.status == SeatStatusEnum.Vacant.v for seat in result))
        self.assertEqual(result[0].name, 'C-1')

    def test_4seats(self):
        """ 4連席確保 """
        from altair.app.ticketing.core.models import SeatStatusEnum
        request = testing.DummyRequest()
        target = self._makeOne(request)

        result = target.get_vacant_seats(self.stock_id, 4)
        self.assertEqual(len(result), 4)
        self.assertTrue(all(seat.status == SeatStatusEnum.Vacant.v for seat in result))
        self.assertEqual(result[0].name, 'D-1')

    def test_reserve(self):
        import altair.app.ticketing.core.models as c_m
        request = testing.DummyRequest()
        target = self._makeOne(request)
        seats = c_m.Seat.query.filter(c_m.Seat.name.in_([u'B-1', u'C-1', u'E-1'])).all()

        result = target._reserve(seats)
        self.assertEqual(len(result), len(seats))

        for s in result:
            self.assertEqual(s.status, int(c_m.SeatStatusEnum.InCart))

    def test_reserve_seats(self):
        import altair.app.ticketing.core.models as c_m
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
        import altair.app.ticketing.core.models as c_m
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
        import altair.app.ticketing.core.models as c_m
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
        import altair.app.ticketing.core.models as c_m
        from altair.app.ticketing.cart.reserving import NotEnoughAdjacencyException
        request = testing.DummyRequest()
        target = self._makeOne(request)

        for i in range(8):
            target.reserve_seats(self.stock_id, 2)
        self.assertRaises(NotEnoughAdjacencyException, target.reserve_seats, self.stock_id, 2)

    def test_reserve_3seats_until_sold_out(self):
        import altair.app.ticketing.core.models as c_m
        from altair.app.ticketing.cart.reserving import NotEnoughAdjacencyException
        request = testing.DummyRequest()
        target = self._makeOne(request)

        for i in range(3):
            target.reserve_seats(self.stock_id, 3)
        self.assertRaises(NotEnoughAdjacencyException, target.reserve_seats, self.stock_id, 3)
        for i in range(4):
            target.reserve_seats(self.stock_id, 2)
        self.assertRaises(NotEnoughAdjacencyException, target.reserve_seats, self.stock_id, 2)

class StockerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.session = _setup_db()

    def setUp(self):
        pass

    def tearDown(self):
        import transaction
        transaction.abort()
        self.session.remove()

    def _getTarget(self):
        from altair.app.ticketing.cart.stocker import Stocker
        return Stocker

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def _add_stock(self, quantity):
        import altair.app.ticketing.core.models as c_m
        # organization
        org = c_m.Organization(code="TEST", short_name="testing")
        # event
        event = c_m.Event(organization=org)
        # performance
        performance = c_m.Performance(event=event)
        stock = c_m.Stock(performance=performance, quantity=quantity)
        product = c_m.Product(price=100.0)
        product_item = c_m.ProductItem(product=product, stock=stock, price=100.0, performance=performance)
        c_m.StockStatus(stock=stock, quantity=quantity)
        c_m.DBSession.add(stock)
        c_m.DBSession.flush()
        return stock

    def test__take_stock(self):
        request = testing.DummyRequest()
        target = self._makeOne(request)
        stock = self._add_stock(10)
        result = target._take_stock([(stock.id, 8)])
        self.assertEqual(result[0][0].quantity, 2)
        self.assertEqual(result[0][1], 8)

    def test__take_stock_not_enough(self):
        from altair.app.ticketing.cart.stocker import NotEnoughStockException
        request = testing.DummyRequest()
        target = self._makeOne(request)
        stock = self._add_stock(10)
        self.assertRaises(NotEnoughStockException, target._take_stock, [(stock.id, 100)])

    def test__take_stock_invalid_product(self):
        from altair.app.ticketing.cart.stocker import InvalidProductSelectionException
        request = testing.DummyRequest()
        target = self._makeOne(request)
        stock = self._add_stock(10)
        product = stock.product_items[0].product
        other_performance_id = stock.performance_id + 1
        self.assertRaises(InvalidProductSelectionException, target.take_stock, other_performance_id, [(product, 1)])

    def test_take_stock(self):
        stock = self._add_stock(10)
        status = stock.stock_status
        product = stock.product_items[0].product
        performance = stock.product_items[0].performance
        
        request = testing.DummyRequest()
        target = self._makeOne(request)
        result = target.take_stock(performance.id, [(product, 10)])
        self.assertEqual(result[0], (status, 10))

class pop_seatTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.session = _setup_db()


    def setUp(self):
        pass

    def tearDown(self):
        import transaction
        transaction.abort()
        self.session.remove()

    def _callFUT(self, *args, **kwargs):
        from .api import pop_seat
        return pop_seat(*args, **kwargs)

    def _add_seats(self):
        import altair.app.ticketing.core.models as c_m
        # organization
        org = c_m.Organization(code="TEST", short_name="testing")
        # event
        event = c_m.Event(organization=org)
        # performance
        performance = c_m.Performance(event=event)
        # site
        site = c_m.Site()
        # venue
        venue = c_m.Venue(site=site, organization=org, performance=performance)
        stock1 = c_m.Stock(performance=performance)
        stock2 = c_m.Stock(performance=performance)
        product_item1 = c_m.ProductItem(price=100, stock=stock1)
        product_item2 = c_m.ProductItem(price=200, stock=stock2)
        seat1 = c_m.Seat(stock=stock1, venue=venue)
        seat2 = c_m.Seat(stock=stock2, venue=venue)
        seat3 = c_m.Seat(stock=stock1, venue=venue)
        seat4 = c_m.Seat(stock=stock2, venue=venue)

        seats = [ seat1, seat2, seat3, seat4 ]

        self.session.add(stock1)
        self.session.add(stock2)
        self.session.flush()

        return performance, product_item1, seats

class CartFactoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.session = _setup_db()


    def setUp(self):
        pass

    def tearDown(self):
        import transaction
        transaction.abort()
        self.session.remove()

    def _getTarget(self):
        from carting import CartFactory
        return CartFactory

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)


    def _add_seats(self):
        import altair.app.ticketing.core.models as c_m
        # organization
        org = c_m.Organization(code="TEST", short_name="testing")
        # event
        event = c_m.Event(organization=org)
        # performance
        performance = c_m.Performance(event=event)
        # site
        site = c_m.Site()
        # venue
        venue = c_m.Venue(site=site, organization=org, performance=performance)
        stock_type = c_m.StockType(quantity_only=False)
        quantity_only_stock_type = c_m.StockType(quantity_only=True)
        stock1 = c_m.Stock(performance=performance, stock_type=stock_type)
        stock2 = c_m.Stock(performance=performance, stock_type=stock_type)
        stock3 = c_m.Stock(performance=performance, stock_type=quantity_only_stock_type)
        product1 = c_m.Product(price=100)
        product2 = c_m.Product(price=200)
        product3 = c_m.Product(price=300)
        product_item1 = c_m.ProductItem(price=100, product=product1, stock=stock1, performance=performance)
        product_item2 = c_m.ProductItem(price=200, product=product2, stock=stock2, performance=performance)
        product_item3 = c_m.ProductItem(price=300, product=product3, stock=stock3, performance=performance)
        seat1 = c_m.Seat(stock=stock1, venue=venue)
        seat2 = c_m.Seat(stock=stock2, venue=venue)
        seat3 = c_m.Seat(stock=stock1, venue=venue)
        seat4 = c_m.Seat(stock=stock2, venue=venue)
        seat5 = c_m.Seat(stock=stock2, venue=venue)

        seats = [ seat1, seat2, seat3, seat4, seat5 ]

        self.session.add(stock1)
        self.session.add(stock2)
        self.session.add(stock3)
        self.session.flush()

        return performance, product1, product2, product3, seats

    def test_create_cart(self):
        performance, product1, product2, product3, seats = self._add_seats()

        seat1 = seats[0]
        seat2 = seats[1]
        seat3 = seats[2]
        seat4 = seats[3]
        seat5 = seats[4]

        request = testing.DummyRequest()
        performance_id = performance.id
        ordered_products = [
            (product1, 2),
            (product2, 3),
            (product3, 10),
        ]

        target = self._makeOne(request)
        result = target.create_cart(performance_id, seats, ordered_products)
        self.assertEqual(len(result.products), 3)
        self.assertEqual(result.products[0].items[0].seats, [seat1, seat3])
        self.assertEqual(result.products[0].quantity, 2)
        self.assertEqual(result.products[1].items[0].seats, [seat2, seat4, seat5])
        self.assertEqual(result.products[1].quantity, 3)
        self.assertEqual(result.products[2].items[0].seats, [])
        self.assertEqual(result.products[2].quantity, 10)

    def test_create_cart_invalid_product(self):
        import altair.app.ticketing.core.models as c_m
        from altair.app.ticketing.cart.stocker import InvalidProductSelectionException
        performance, product1, product2, product3, seats = self._add_seats()

        request = testing.DummyRequest()
        ordered_products = [
            (product1, 2),
            ]

        other_performance = c_m.Performance(event=performance.event)
        self.session.add(other_performance)
        self.session.flush()

        target = self._makeOne(request)
        self.assertRaises(InvalidProductSelectionException, target.create_cart, other_performance.id, seats, ordered_products)

    def test_pop_seats(self):

        performance, product1, product2, product3, seats = self._add_seats()
        product_item1 = product1.items[0]

        seat1 = seats[0]
        seat2 = seats[1]
        seat3 = seats[2]
        seat4 = seats[3]
        seat5 = seats[4]

        quantity = 2

        request = testing.DummyRequest()
        target = self._makeOne(request)

        result = target.pop_seats(product_item1, quantity, seats)

        self.assertEqual(result, [seat1, seat3])
        self.assertEqual(seats, [seat2, seat4, seat5])

    def test_pop_seats_with_few_quantity(self):

        performance, product1, product2, product3, seats = self._add_seats()

        seat1 = seats[0]
        seat2 = seats[1]
        seat3 = seats[2]
        seat4 = seats[3]
        seat5 = seats[4]

        product_item1 = product1.items[0]
        quantity = 1
        request = testing.DummyRequest()

        target = self._makeOne(request)
        result = target.pop_seats(product_item1, quantity, seats)

        self.assertEqual(result, [seat1])
        self.assertEqual(seats, [seat2, seat3, seat4, seat5])

class order_productsTests(unittest.TestCase):
    """ 購入処理テスト(ユニット) """
    def setUp(self):
        self.session = _setup_db()

    def tearDown(self):
        _teardown_db() 

    def _callFUT(self, *args, **kwargs):
        from .api import order_products
        return order_products(*args, **kwargs)

    def test_it(self):
        from pyramid.interfaces import IRequest
        from .interfaces import IStocker, IReserving, ICartFactory
        request = testing.DummyRequest()
        request.registry.adapters.register([IRequest], IStocker, "", DummyStocker)
        request.registry.adapters.register([IRequest], IReserving, "", DummyReserving)
        request.registry.adapters.register([IRequest], ICartFactory, "", DummyCartFactory)

        performance_id = "1"
        product_requires = [
            (testing.DummyModel(), 10),
            (testing.DummyModel(), 20),
        ]

        result = self._callFUT(request, performance_id, product_requires)
        self.assertIsNotNone(result)

    def test_one_order(self):
        from ..core.models import (
            Seat,
            SeatAdjacency,
            SeatAdjacencySet,
            SeatStatus,
            SeatStatusEnum,
            SeatIndex,
            SeatIndexType,
            Stock,
            StockStatus,
            StockType,
            Product,
            ProductItem,
            Event,
            Performance,
            Organization,
            Venue,
            Site
            )
        from pyramid.interfaces import IRequest
        from .interfaces import IStocker, IReserving, ICartFactory
        from .stocker import Stocker, NotEnoughStockException
        from .reserving import Reserving
        from .carting import CartFactory
        request = testing.DummyRequest()
        request.registry.adapters.register([IRequest], IStocker, "", Stocker)
        request.registry.adapters.register([IRequest], IReserving, "", Reserving)
        request.registry.adapters.register([IRequest], ICartFactory, "", CartFactory)

        # 在庫
        stock_id = 1
        venue_id = 2
        site_id = 3
        organization_id = 4
        performance_id = 5
        event_id = 6

        organization = Organization(id=organization_id, short_name='', code='XX')
        event = Event(id=event_id, organization=organization)
        performance = Performance(id=performance_id, event=event)
        site = Site(id=site_id)
        venue = Venue(id=venue_id, organization=organization, site=site, performance=performance)
        stock = Stock(id=stock_id, quantity=5, performance=performance, stock_type=StockType())
        stock_status = StockStatus(stock=stock, quantity=5)
        seats = [Seat(id=i, l0_id='s%s' % i, stock=stock, venue=venue, status_=SeatStatus(status=int(SeatStatusEnum.Vacant))) for i in range(1, 6)]
        seat_index_type = SeatIndexType(name=u'', venue=venue)
        seat_indexes = [SeatIndex(seat=seat, seat_index_type=seat_index_type, index=1) for seat in seats]
        product_item = ProductItem(stock=stock, price=100, quantity=1, performance=performance)
        product = Product(id=1, price=100, items=[product_item])
        self.session.add(stock)
        self.session.add(product)
        self.session.add(product_item)
        self.session.add(stock_status)
        self.session.add(seat_index_type)
        [self.session.add(s) for s in seat_indexes]
        [self.session.add(s) for s in seats]

        # 座席隣接状態
        for seat_count in range (2, 4):
            adjacency_set = SeatAdjacencySet(seat_count=seat_count, site=site)
            for i in range(0, len(seats) - 1):
                adjacency = SeatAdjacency(adjacency_set=adjacency_set)
                adjacency.seats = seats[i:i+2]
                self.session.add(adjacency)
            self.session.add(adjacency_set)
        self.session.flush()

        # 注文 S席 2枚
        ordered_products = [(product, 2)]
        cart1 = self._callFUT(request, performance_id, ordered_products)

        self.assertIsNotNone(cart1)
        self.assertEqual(len(cart1.products), 1)
        self.assertEqual(len(cart1.products[0].items), 1)
        self.assertEqual(cart1.products[0].product, product)
        self.assertEqual(cart1.products[0].items[0].quantity, 2)

        def assertQuantity(quantity):
            from sqlalchemy import sql
            self.assertEqual(self.session.bind.execute(sql.select([StockStatus.quantity]).where(StockStatus.stock_id==stock.id)).first().quantity, quantity)

        assertQuantity(3)

        cart2 = self._callFUT(request, performance_id, ordered_products)

        self.assertIsNotNone(cart2)
        self.assertEqual(len(cart2.products), 1)
        self.assertEqual(len(cart2.products[0].items), 1)
        self.assertEqual(cart2.products[0].product, product)
        self.assertEqual(cart2.products[0].items[0].quantity, 2)

        assertQuantity(1)

        self.assertRaises(NotEnoughStockException, lambda:self._callFUT(request, performance_id, ordered_products))


class DummyStocker(object):
    """ dummy for IStocker"""
    def __init__(self, request):
        self.request = request

    def take_stock(self, performance_id, product_requires):
        return [
            (testing.DummyModel(
                stock_id=10000,
                stock=testing.DummyModel(
                    stock_type=testing.DummyModel(quantity_only=False))), 10)
        ]


class get_valid_sales_urlTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.session = _setup_db()

    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, *args, **kwargs):
        from .api import get_valid_sales_url
        return get_valid_sales_url(*args, **kwargs)

    def _create_data(self):
        import altair.app.ticketing.core.models as c_m
        import altair.app.ticketing.users.models as u_m
        event = c_m.Event()
        membership = u_m.Membership(name='ms1')
        membergroup = u_m.MemberGroup(name='mg1', membership=membership)
        sales_segment_group = c_m.SalesSegmentGroup(
            event=event,
            membergroups=[membergroup],
            margin_ratio=0.,
            refund_ratio=0.,
            printing_fee=0.,
            registration_fee=0.
            )
        sales_segment = c_m.SalesSegment(
            sales_segment_group=sales_segment_group)
        self.session.add(event)
        self.session.add(membership)
        self.session.flush()
        return event, membergroup

    def test_it(self):
        self.config.testing_securitypolicy(
            "test_user",
            ['membership:ms1', 'membergroup:mg1']
        )
        self.config.add_route('cart.index.sales',
            '{event_id}/{sales_segment_group_id}')
        event, membergroup = self._create_data()
        request = testing.DummyRequest()
        result = self._callFUT(request, event)

        self.assertEqual(result, 'http://example.com/1/1')

    def test_it_not_found(self):
        self.config.testing_securitypolicy(
            "test_user",
            ['membership:ms1', 'membergroup:mg2']
        )
        self.config.add_route('cart.index.sales',
            '{event_id}/{sales_segment_group_id}')
        event, membergroup = self._create_data()
        request = testing.DummyRequest()
        result = self._callFUT(request, event)

        self.assertIsNone(result)

class DummyReserving(object):
    """ dummy for IReserving"""
    def __init__(self, request):
        self.request = request

    def reserve_seats(self, stock_id, quantity):
        return [testing.DummyModel()] * quantity

class DummyCartFactory(object):
    def __init__(self, request):
        self.request = request
    
    def create_cart(self, performance_id, seats, ordered_products):
        return testing.DummyModel(performance_id=performance_id, seats=seats, ordered_products=ordered_products)

class logout_Tests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, *args, **kwargs):
        from .api import logout
        return logout(*args, **kwargs)

    def test_it(self):
        request = testing.DummyRequest()
        self._callFUT(request)

