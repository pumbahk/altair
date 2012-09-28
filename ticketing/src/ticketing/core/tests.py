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

class TicketPrintHistoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.session = _setup_db(modules=['ticketing.core.models'])

    @classmethod
    def tearDownClass(self):
        _teardown_db()

    def tearDown(self):
        import transaction
        transaction.abort()

    def test_insert_events(self):
        from ..models import DomainConstraintError
        from .models import TicketPrintHistory
        import transaction
        self.assertRaises(DomainConstraintError, lambda: TicketPrintHistory().save())
        transaction.begin()
        self.assertRaises(DomainConstraintError, lambda: TicketPrintHistory(ticket_id=1, seat_id=1).save())
        transaction.begin()
        try:
            TicketPrintHistory(ticket_id=1, order_id=1).save()
            self.assert_(True)
        except DomainConstraintError:
            self.fail()
            transaction.begin()
        try:
            TicketPrintHistory(ticket_id=1, ordered_product_item_id=1).save()
            self.assert_(True)
        except DomainConstraintError:
            self.fail()
            transaction.begin()
        try:
            TicketPrintHistory(ticket_id=1, item_token_id=1).save()
            self.assert_(True)
        except DomainConstraintError:
            self.fail()

    def test_update_events(self):
        from ..models import DomainConstraintError
        from .models import TicketPrintHistory
        import transaction
        tp = TicketPrintHistory(id=1, ticket_id=1, order_id=1)
        tp.save()
        transaction.commit()
        tp = TicketPrintHistory.filter_by(id=1).one()
        tp.order_id = None
        self.assertRaises(DomainConstraintError, lambda: tp.save())
        transaction.begin()
        try:
            tp = TicketPrintHistory.filter_by(id=1).one()
            tp.order_id = None
            tp.ordered_product_item_id = 1
            tp.save()
            self.assert_(True)
        except DomainConstraintError:
            transaction.begin()
            self.fail()
        try:
            tp = TicketPrintHistory.filter_by(id=1).one()
            tp.order_id = None
            tp.item_token_id = 1
            tp.save()
            self.assert_(True)
        except DomainConstraintError:
            self.fail()

if __name__ == "__main__":
    unittest.main()

