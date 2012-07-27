# -*- coding:utf-8 -*-

# move it.
import unittest
from ..testing import _setup_db, _teardown_db

def get_organization(*args, **kwargs):
    from .models import Organization
    return Organization(*args, **kwargs)

class EventCMSDataTests(unittest.TestCase):
    def _getTarget(self):
        from .models import Event
        return Event

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_data_include_organazation_id(self):
        organization = get_organization(id=10000)
        target = self._makeOne(organization=organization)
        result = target._get_self_cms_data()
        self.assertEqual(result["organization_id"], 10000)

class ProductTests(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.session = _setup_db(modules=['ticketing.core.models'])

    @classmethod
    def tearDownClass(self):
        _teardown_db()

    def tearDown(self):
        import transaction
        transaction.abort()

    def _getTarget(self):
        from .models import Product
        return Product

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def _create_performance(self):
        from .models import Performance
        return Performance()

    def _create_stock(self, performance):
        from .models import Stock, StockType
        stock_type = StockType()
        return Stock(stock_type=stock_type, performance=performance)
        
    def _create_items(self, performance, stock, quantities):
        from .models import ProductItem
        return [ProductItem(price=0, performance=performance, stock=stock, quantity=q) for q in quantities]

    def test_get_quantity_power(self):
        performance = self._create_performance()
        stock1 = self._create_stock(performance)
        stock2 = self._create_stock(performance)
        target = self._makeOne(
            price=0,
            items=self._create_items(performance, stock1, [1, 2]) + self._create_items(performance, stock2, [3, 4]))

        self.session.add(performance)
        self.session.flush()
        result = target.get_quantity_power(stock1.stock_type, performance.id)

        self.assertEqual(result, 3)
        

class SeatTests(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.session = _setup_db(modules=['ticketing.core.models'])

    @classmethod
    def tearDownClass(self):
        _teardown_db()

    def tearDown(self):
        import transaction
        transaction.abort()

    def _getTarget(self):
        from .models import Seat
        return Seat

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def _create_performance(self):
        from .models import Performance
        return Performance()

    def _create_stock(self, performance, stock_holder):
        from .models import Stock, StockType
        stock_type = StockType()
        return Stock(stock_type=stock_type, 
                     performance=performance,
                     stock_holder=stock_holder)

    def _create_stock_holder(self):
        from .models import StockHolder
        return StockHolder()

    def test_is_hold_instance(self):
        stock_holder = self._create_stock_holder()        
        performance = self._create_performance()
        stock = self._create_stock(performance, stock_holder)

        target = self._makeOne(stock=stock)

        result = target.is_hold(stock_holder)

        self.assertTrue(result)

    def test_is_hold_instance_not_hold(self):
        stock_holder = self._create_stock_holder()        
        other_stock_holder = self._create_stock_holder()        
        performance = self._create_performance()
        stock = self._create_stock(performance, stock_holder)

        target = self._makeOne(stock=stock)

        result = target.is_hold(other_stock_holder)

        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()

