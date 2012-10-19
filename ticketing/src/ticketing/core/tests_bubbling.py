# -*- encoding:utf-8 -*-
import unittest
from pyramid import testing
from datetime import datetime

def setUpModule():
    from ticketing.testing import _setup_db
    _setup_db(modules=[
            "ticketing.models",
            "ticketing.core.models",
            "ticketing.cart.models",
            ])

def tearDownModule():
    from ticketing.testing import _teardown_db
    _teardown_db()

class IssuedPrintedSetterTests(unittest.TestCase):
    def tearDown(self):
        import transaction
        transaction.abort()

    def _getTarget(self):
        from ticketing.core.utils import IssuedPrintedAtSetter
        return IssuedPrintedAtSetter

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args,**kwargs)

    def test_order_non_printed(self):
        from ticketing.core.models import Order
        import sqlahelper
        order = Order(total_amount=0, system_fee=0, transaction_fee=0, delivery_fee=0,  id=1)
        sqlahelper.get_session().add(order)

        now_date = datetime(2000, 1, 1)

        target = self._makeOne(now_date)
        target.add_order(order)

        target.start_bubbling()

        self.assertEquals(order.printed_at, now_date)
        self.assertEquals(order.issued_at, now_date)
        self.assertEquals(order.issued, True)

    def test_order_printed(self):
        from ticketing.core.models import Order
        import sqlahelper
        order = Order(total_amount=0, system_fee=0, transaction_fee=0, delivery_fee=0,  id=1, printed_at=datetime(1950, 1, 1), issued_at=datetime(1900, 1, 1))
        sqlahelper.get_session().add(order)

        now_date = datetime(2000, 1, 1)

        target = self._makeOne(now_date)
        target.add_order(order)

        target.start_bubbling()

        self.assertEquals(order.printed_at, datetime(1950, 1, 1))
        self.assertEquals(order.issued_at, datetime(1900, 1, 1))
        self.assertEquals(order.issued, True)

    def test_bubling_from_item(self):
        from ticketing.core.models import Order, OrderedProduct, OrderedProductItem
        import sqlahelper
        order = Order(total_amount=0, system_fee=0, transaction_fee=0, delivery_fee=0,  id=1)
        sqlahelper.get_session().add(order)

        ordered_product = OrderedProduct(price=0, id=1, order=order)
        items = [
            OrderedProductItem(price=0, id=1, ordered_product=ordered_product), 
            OrderedProductItem(price=0, id=2, ordered_product=ordered_product), 
            OrderedProductItem(price=0, id=3, ordered_product=ordered_product), 
            ]
        now_date = datetime(2000, 1, 1)

        target = self._makeOne(now_date)
        for item in items:
            target.add_item(item)
            
        target.start_bubbling()

        self.assertEquals(order.printed_at, now_date)
        self.assertEquals(order.issued_at, now_date)
        self.assertEquals(order.issued, True)

        self.assertEquals(OrderedProductItem.query.filter_by(printed_at=datetime(2000, 1, 1), issued_at=datetime(2000, 1, 1)).count(), 3)

    def test_bubling_from_token(self):
        from ticketing.core.models import Order, OrderedProduct, OrderedProductItem, OrderedProductItemToken
        import sqlahelper
        order = Order(total_amount=0, system_fee=0, transaction_fee=0, delivery_fee=0,  id=1)
        sqlahelper.get_session().add(order)

        ordered_product = OrderedProduct(price=0, id=1, order=order)
        items = [
            OrderedProductItem(price=0, id=1, ordered_product=ordered_product), 
            OrderedProductItem(price=0, id=2, ordered_product=ordered_product), 
            OrderedProductItem(price=0, id=3, ordered_product=ordered_product), 
            ]
        tokens = [
            OrderedProductItemToken(serial="xxxx", id=1, item=items[0]), 
            OrderedProductItemToken(serial="xxxx", id=2, item=items[0]), 
            OrderedProductItemToken(serial="xxxx", id=3, item=items[1]), 
            OrderedProductItemToken(serial="xxxx", id=4, item=items[1]), 
            ]
        now_date = datetime(2000, 1, 1)

        target = self._makeOne(now_date)
        for item in items:
            for token in item.tokens:
                target.add_token(token)
            target.add_item(item)

        target.start_bubbling()

        self.assertEquals(order.printed_at, now_date)
        self.assertEquals(order.issued_at, now_date)
        self.assertEquals(order.issued, True)

        self.assertEquals(OrderedProductItem.query.filter_by(printed_at=datetime(2000, 1, 1), issued_at=datetime(2000, 1, 1)).count(), 3)
        self.assertEquals(OrderedProductItemToken.query.filter_by(printed_at=datetime(2000, 1, 1), issued_at=datetime(2000, 1, 1)).count(), 4)
        
if __name__ == "__main__":
    unittest.main()
