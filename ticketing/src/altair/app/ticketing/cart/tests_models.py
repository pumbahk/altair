import unittest
from altair.app.ticketing.core.testing import CoreTestMixin
from altair.app.ticketing.testing import _setup_db, _teardown_db

class CartTestMixin(CoreTestMixin):
    def setUp(self):
        self.session = _setup_db(['altair.app.ticketing.core.models', 'altair.app.ticketing.cart.models'])
        CoreTestMixin.setUp(self)

    def tearDown(self):
        _teardown_db()

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
        from ..core.models import SeatStatusEnum
        from altair.app.ticketing.core.models import ProductItem
        stocks = self._create_stocks(self._create_stock_types(num))
        def mark_in_cart(seats):
            for seat in seats:
                seat.status = SeatStatusEnum.InCart.v
            return seats
        return [CartedProductItem(product_item=ProductItem(price=0, stock=stock), seats=mark_in_cart(self._create_seats([stock]))) for stock in stocks]

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
        from altair.app.ticketing.core.models import Product
        product = Product(price=100)
        target = self._makeOne(items=self._create_items(2), product=product)
        self.session.add(target)
        self.session.flush()
        target.release()
        self.assertTrue(target.finished_at is not None)
        self.assertTrue(all(item.finished_at is not None for item in target.items))
