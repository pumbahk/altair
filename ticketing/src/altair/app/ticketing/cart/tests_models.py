import unittest
from altair.app.ticketing.core.testing import CoreTestMixin
from altair.app.ticketing.testing import _setup_db, _teardown_db

class CartTestMixin(CoreTestMixin):
    def setUp(self):
        self.session = _setup_db([
            'altair.app.ticketing.core.models',
            'altair.app.ticketing.orders.models',
            'altair.app.ticketing.lots.models',
            'altair.app.ticketing.cart.models',
            ])
        CoreTestMixin.setUp(self)

    def tearDown(self):
        _teardown_db()

class CartedProductItemTests(unittest.TestCase, CartTestMixin):
    maxDiff = None

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
             {'l0_id': 'seat-D-0', 'name': u'Seat D-0'},
             {'l0_id': 'seat-D-1', 'name': u'Seat D-1'},
             {'l0_id': 'seat-D-2', 'name': u'Seat D-2'},
             {'l0_id': 'seat-D-3', 'name': u'Seat D-3'},])

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
        retval = []
        for stock in stocks:
            seats = self._create_seats([stock])
            for seat in seats:
                seat.status = SeatStatusEnum.InCart.v
            retval.append(CartedProductItem(
                product_item=ProductItem(price=0, stock=stock),
                quantity=len(seats),
                seats=seats
                ))
        return retval

    def test_seats(self):
        target = self._makeOne(items=self._create_items(5))
        result = target.seats
        self.assertEqual(result, 
            [{'l0_id': 'seat-A-0', 'name': u'Seat A-0'},
             {'l0_id': 'seat-A-1', 'name': u'Seat A-1'},
             {'l0_id': 'seat-A-2', 'name': u'Seat A-2'},
             {'l0_id': 'seat-A-3', 'name': u'Seat A-3'},
             {'l0_id': 'seat-D-0', 'name': u'Seat D-0'},
             {'l0_id': 'seat-D-1', 'name': u'Seat D-1'},
             {'l0_id': 'seat-D-2', 'name': u'Seat D-2'},
             {'l0_id': 'seat-D-3', 'name': u'Seat D-3'}])

    def test_release(self):
        from altair.app.ticketing.core.models import Product
        product = Product(price=100)
        target = self._makeOne(items=self._create_items(2), product=product)
        self.session.add(target)
        self.session.flush()
        target.release()
        self.assertTrue(target.finished_at is not None)
        self.assertTrue(all(element.finished_at is not None for element in target.elements))
