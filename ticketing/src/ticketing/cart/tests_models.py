import unittest
from ticketing.testing import _setup_db, _teardown_db

class CartTestMixin(object):
    def setUp(self):
        self.session = _setup_db(['ticketing.core.models', 'ticketing.cart.models'])
        from . import models
        from ticketing.core.models import Organization, Event, Performance, Site, Venue
        self.organization = Organization(short_name=u'')
        self.event = Event(organization=self.organization)
        self.performance = Performance(event=self.event, venue=Venue(organization=self.organization, site=Site()))

    def tearDown(self):
        _teardown_db()

    def _create_stock_types(self, num):
        from ticketing.core.models import StockType
        return [StockType(name=name) for name in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'[0:num]]

    def _create_stocks(self, stock_types):
        from ticketing.core.models import Stock, StockStatus, Performance, Venue, Site
        quantity = 4
        return [Stock(performance=self.performance, stock_type=stock_type, quantity=quantity, stock_status=StockStatus(quantity=quantity)) for stock_type in stock_types]

    def _create_seats(self, stocks):
        from ticketing.core.models import Seat, SeatStatus, SeatStatusEnum
        return [Seat(name=u"Seat %s-%d" % (stock.stock_type.name, i),
                     l0_id="seat-%s-%d" % (stock.stock_type.name, i),
                     stock=stock,
                     venue=stock.performance and stock.performance.venue,
                     status_=SeatStatus(status=SeatStatusEnum.InCart.v)) \
                for stock in stocks for i in range(stock.quantity)]

class CartedProductItemTests(unittest.TestCase, CartTestMixin):
    def setUp(self):
        CartTestMixin.setUp(self)

    def tearDown(self):
        CartTestMixin.tearDown(self)

    def _getTarget(self):
        from .models import CartedProductItem
        return CartedProductItem

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)
            
    def test_seatdicts(self):
        target = self._makeOne(seats=self._create_seats(self._create_stocks(self._create_stock_types(5))))

        result = target.seatdicts

        self.assertEqual(list(result), 
            [{'l0_id': 'seat-A-0', 'name': u'Seat A-0'},
             {'l0_id': 'seat-A-1', 'name': u'Seat A-1'},
             {'l0_id': 'seat-A-2', 'name': u'Seat A-2'},
             {'l0_id': 'seat-A-3', 'name': u'Seat A-3'},
             {'l0_id': 'seat-B-0', 'name': u'Seat B-0'},
             {'l0_id': 'seat-B-1', 'name': u'Seat B-1'},
             {'l0_id': 'seat-B-2', 'name': u'Seat B-2'},
             {'l0_id': 'seat-B-3', 'name': u'Seat B-3'},
             {'l0_id': 'seat-C-0', 'name': u'Seat C-0'},
             {'l0_id': 'seat-C-1', 'name': u'Seat C-1'},
             {'l0_id': 'seat-C-2', 'name': u'Seat C-2'},
             {'l0_id': 'seat-C-3', 'name': u'Seat C-3'},
             {'l0_id': 'seat-D-0', 'name': u'Seat D-0'},
             {'l0_id': 'seat-D-1', 'name': u'Seat D-1'},
             {'l0_id': 'seat-D-2', 'name': u'Seat D-2'},
             {'l0_id': 'seat-D-3', 'name': u'Seat D-3'},
             {'l0_id': 'seat-E-0', 'name': u'Seat E-0'},
             {'l0_id': 'seat-E-1', 'name': u'Seat E-1'},
             {'l0_id': 'seat-E-2', 'name': u'Seat E-2'},
             {'l0_id': 'seat-E-3', 'name': u'Seat E-3'}])

class CartedProductTests(unittest.TestCase, CartTestMixin):
    def setUp(self):
        CartTestMixin.setUp(self)

    def tearDown(self):
        CartTestMixin.tearDown(self)

    def _getTarget(self):
        from .models import CartedProduct
        return CartedProduct

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def _create_items(self, num):
        from .models import CartedProductItem
        from ticketing.core.models import ProductItem
        stocks = self._create_stocks(self._create_stock_types(num))
        return [CartedProductItem(product_item=ProductItem(price=0, stock=stock), seats=self._create_seats([stock])) for stock in stocks]

    def test_seats(self):
        target = self._makeOne(items=self._create_items(5))
        result = target.seats
        self.assertEqual(result, 
            [{'l0_id': 'seat-A-0', 'name': u'Seat A-0'},
             {'l0_id': 'seat-A-1', 'name': u'Seat A-1'},
             {'l0_id': 'seat-A-2', 'name': u'Seat A-2'},
             {'l0_id': 'seat-A-3', 'name': u'Seat A-3'},
             {'l0_id': 'seat-B-0', 'name': u'Seat B-0'},
             {'l0_id': 'seat-B-1', 'name': u'Seat B-1'},
             {'l0_id': 'seat-B-2', 'name': u'Seat B-2'},
             {'l0_id': 'seat-B-3', 'name': u'Seat B-3'},
             {'l0_id': 'seat-C-0', 'name': u'Seat C-0'},
             {'l0_id': 'seat-C-1', 'name': u'Seat C-1'},
             {'l0_id': 'seat-C-2', 'name': u'Seat C-2'},
             {'l0_id': 'seat-C-3', 'name': u'Seat C-3'},
             {'l0_id': 'seat-D-0', 'name': u'Seat D-0'},
             {'l0_id': 'seat-D-1', 'name': u'Seat D-1'},
             {'l0_id': 'seat-D-2', 'name': u'Seat D-2'},
             {'l0_id': 'seat-D-3', 'name': u'Seat D-3'},
             {'l0_id': 'seat-E-0', 'name': u'Seat E-0'},
             {'l0_id': 'seat-E-1', 'name': u'Seat E-1'},
             {'l0_id': 'seat-E-2', 'name': u'Seat E-2'},
             {'l0_id': 'seat-E-3', 'name': u'Seat E-3'}])

    def test_release(self):
        from ticketing.core.models import Product
        product = Product(price=100)
        target = self._makeOne(items=self._create_items(2), product=product)
        self.session.add(target)
        self.session.flush()
        target.release()
        self.assertTrue(target.finished_at is not None and all(item.finished_at is not None for item in target.items))
