# -*- coding:utf-8 -*-

import unittest
import mock
from pyramid import testing
from .testing import _setup_db as _setup_db_, _teardown_db

def _setup_db(echo=False):
    return _setup_db_(
        modules=[
            'ticketing.core.models',
            #'ticketing.orders.models',
            'ticketing.cart.models',
            ],
        echo=echo
        )

def _setup_it(config):
    from pyramid.interfaces import IRequest
    from .interfaces import IStocker, IReserving, ICartFactory
    from .stocker import Stocker
    from .reserving import Reserving
    from .carting import CartFactory
    reg = config.registry
    reg.adapters.register([IRequest], IStocker, "", Stocker)
    reg.adapters.register([IRequest], IReserving, "", Reserving)
    reg.adapters.register([IRequest], ICartFactory, "", CartFactory)
    config.add_route('cart.payment', 'cart/payment')

class ReserveViewTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.session = _setup_db(echo=False)

    def setUp(self):
        self.config = testing.setUp()
        _setup_it(self.config)

    def _getTarget(self):
        from .views import ReserveView
        return ReserveView

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def _add_seats(self):
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
        stock_type = c_m.StockType(quantity_only=False)
        quantity_only_stock_type = c_m.StockType(quantity_only=True)

        stock1 = c_m.Stock(stock_type=stock_type, quantity=10, performance=performance)
        stock1_status = c_m.StockStatus(stock=stock1, quantity=10)
        stock2 = c_m.Stock(stock_type=stock_type, quantity=20, performance=performance)
        stock2_status = c_m.StockStatus(stock=stock2, quantity=20)
        stock3 = c_m.Stock(stock_type=quantity_only_stock_type, quantity=30, performance=performance)
        stock3_status = c_m.StockStatus(stock=stock3, quantity=30)
        stock4 = c_m.Stock(stock_type=quantity_only_stock_type, quantity=30, performance=performance)
        stock4_status = c_m.StockStatus(stock=stock4, quantity=0)

        product1 = c_m.Product(price=100)
        product2 = c_m.Product(price=200)
        product3 = c_m.Product(price=300)
        product4 = c_m.Product(price=400)
        product_item1 = c_m.ProductItem(price=100, product=product1, stock=stock1, performance=performance)
        product_item2 = c_m.ProductItem(price=200, product=product2, stock=stock2, performance=performance)
        product_item3 = c_m.ProductItem(price=300, product=product3, stock=stock3, performance=performance)
        product_item4 = c_m.ProductItem(price=400, product=product4, stock=stock4, performance=performance)

        seat_index_type = c_m.SeatIndexType(venue=venue, name='testing')
        seat1 = c_m.Seat(stock=stock1, venue=venue, l0_id="test-1", name=u"テスト１")
        seat1_status = c_m.SeatStatus(seat=seat1, status=int(c_m.SeatStatusEnum.Vacant))
        seat_index1 = c_m.SeatIndex(seat=seat1, index=1, seat_index_type=seat_index_type)
        seat2 = c_m.Seat(stock=stock2, venue=venue, l0_id="test-2", name=u"テスト２")
        seat2_status = c_m.SeatStatus(seat=seat2, status=int(c_m.SeatStatusEnum.Vacant))
        seat_index2 = c_m.SeatIndex(seat=seat2, index=2, seat_index_type=seat_index_type)
        seat3 = c_m.Seat(stock=stock1, venue=venue, l0_id="test-3", name=u"テスト３")
        seat3_status = c_m.SeatStatus(seat=seat3, status=int(c_m.SeatStatusEnum.Vacant))
        seat_index3 = c_m.SeatIndex(seat=seat3, index=3, seat_index_type=seat_index_type)
        seat4 = c_m.Seat(stock=stock2, venue=venue, l0_id="test-4", name=u"テスト４")
        seat4_status = c_m.SeatStatus(seat=seat4, status=int(c_m.SeatStatusEnum.Vacant))
        seat_index4 = c_m.SeatIndex(seat=seat4, index=4, seat_index_type=seat_index_type)
        seat5 = c_m.Seat(stock=stock2, venue=venue, l0_id="test-5", name=u"テスト５")
        seat5_status = c_m.SeatStatus(seat=seat5, status=int(c_m.SeatStatusEnum.Vacant))
        seat_index5 = c_m.SeatIndex(seat=seat5, index=5, seat_index_type=seat_index_type)

        seat_adjacency_set = c_m.SeatAdjacencySet(venue=venue, seat_count=2)
        seat_adjacency = c_m.SeatAdjacency(adjacency_set=seat_adjacency_set,
            seats=[seat1, seat3])
        seat_adjacency = c_m.SeatAdjacency(adjacency_set=seat_adjacency_set,
            seats=[seat2, seat4])
        seats = [ seat1, seat2, seat3, seat4, seat5 ]

        self.session.add(stock1)
        self.session.add(stock2)
        self.session.add(stock3)
        self.session.flush()

        return performance, product1, product2, product3, product4, seats

    def test_it_quantity_only(self):
        from webob.multidict import MultiDict
        performance, product1, product2, product3, product4, seats = self._add_seats()

        params = MultiDict([
            ('performance_id', str(performance.id)),
            ('product-%d' % product3.id, 1),
        ])

        context = mock.Mock()
        request = testing.DummyRequest(params=params, 
            context=context)
        target = self._makeOne(request)

        results = target.reserve()

        self.assertEqual(results['result'], 'OK')

    def test_it_not_enough_quantity(self):
        from webob.multidict import MultiDict
        performance, product1, product2, product3, product4, seats = self._add_seats()

        params = MultiDict([
            ('performance_id', str(performance.id)),
            ('product-%d' % product4.id, 1),
        ])

        
        context = mock.Mock()
        request = testing.DummyRequest(params=params, 
            context=context)
        target = self._makeOne(request)

        results = target.reserve()

        self.assertEqual(results['result'], 'NG')

    def test_it_reserving(self):
        from webob.multidict import MultiDict
        performance, product1, product2, product3, product4, seats = self._add_seats()

        params = MultiDict([
            ('performance_id', str(performance.id)),
            ('product-%d' % product1.id, 2),
        ])

        context = mock.Mock()
        request = testing.DummyRequest(params=params, 
            context=context)
        target = self._makeOne(request)

        results = target.reserve()

        self.assertEqual(results['result'], 'OK')
        self.assertEqual(len(results['cart']['products']), 1)
        self.assertEqual(results['cart']['products'][0]['seats'], 
            [{'l0_id': 'test-1', 'name': u'テスト１'},
             {'l0_id': 'test-3', 'name': u'テスト３'}])

    def test_it_reserving_selected(self):
        from webob.multidict import MultiDict
        performance, product1, product2, product3, product4, seats = self._add_seats()

        seat1 = seats[0]
        seat2 = seats[1]
        seat3 = seats[2]
        seat4 = seats[3]
        seat5 = seats[4]

        params = MultiDict([
            ('performance_id', str(performance.id)),
            ('product-%d' % product1.id, 2),
            ('selected_seat', seat1.l0_id),
            ('selected_seat', seat3.l0_id),
        ])

        context = mock.Mock()
        request = testing.DummyRequest(params=params, 
            context=context)
        target = self._makeOne(request)

        results = target.reserve()

        self.assertEqual(results['result'], 'OK')
        self.assertEqual(results['cart']['products'][0]['seats'], 
            [{'l0_id': 'test-1', 'name': u'テスト１'},
             {'l0_id': 'test-3', 'name': u'テスト３'}])

    def test_it_invalid_reserving_selected(self):
        from webob.multidict import MultiDict
        performance, product1, product2, product3, product4, seats = self._add_seats()

        seat1 = seats[0]
        seat2 = seats[1]
        seat3 = seats[2]
        seat4 = seats[3]
        seat5 = seats[4]

        params = MultiDict([
            ('performance_id', str(performance.id)),
            ('product-%d' % product1.id, 2),
            ('selected_seat', seat2.l0_id),
            ('selected_seat', seat4.l0_id),
        ])

        context = mock.Mock()
        request = testing.DummyRequest(params=params, 
            context=context)

        target = self._makeOne(request)
        results = target.reserve()

        self.assertEqual(results['result'], 'NG')

        #self.assertRaises(InvalidSeatSelectionException, target.reserve)
