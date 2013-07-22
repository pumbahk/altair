import unittest
from pyramid import testing
from altair.app.ticketing.testing import _setup_db, _teardown_db
from altair.mq.testing import DummyMessage


class lot_wish_cartTests(unittest.TestCase):
    def _callFUT(self, *args, **kwargs):
        from ..workers import lot_wish_cart
        return lot_wish_cart(*args, **kwargs)

    def test_it(self):
        from altair.app.ticketing.core.models import (
            Performance, Product, PaymentDeliveryMethodPair, ProductItem,
            PaymentMethod, DeliveryMethod,
            SalesSegment,
        )
        from ..models import LotEntryWish, LotEntry, Lot, LotEntryProduct
        product1 = Product(price=100,
                           items=[ProductItem(quantity=1)])
        product2 = Product(price=150,
                           items=[ProductItem(quantity=1), ProductItem(quantity=9)])

        wish = LotEntryWish(
            performance=Performance(),
            lot_entry=LotEntry(lot=Lot(system_fee=9999999999999999999,# not used
                                       sales_segment=SalesSegment(),
                                   ), 
                               entry_no='testing-entry',
                               payment_delivery_method_pair=PaymentDeliveryMethodPair(system_fee=11,
                                                                                      transaction_fee=111,
                                                                                      payment_method=PaymentMethod(),
                                                                                      delivery_method=DeliveryMethod(),
                                                                                  ),
                               
                           ),
            products=[LotEntryProduct(quantity=3,
                                      product=product1),
                      LotEntryProduct(quantity=4,
                                      product=product2)])
        wish2 = LotEntryWish(
            performance=wish.performance,
            products=[LotEntryProduct(quantity=10,
                                      product=product1)])

        wish.lot_entry.wishes.append(wish2)

        # precondition
        self.assertEqual(wish.lot_entry.max_amount, 1011) # 100 * 10 + 11

        result = self._callFUT(wish)

        self.assertEqual(result.order_no, 'testing-entry')
        self.assertTrue(result.has_different_amount)
        self.assertEqual(result.different_amount, 1011 - 911)
        self.assertEqual(result.total_amount, 911)
        self.assertEqual(len(result.products), 2)
        self.assertEqual(result.products[0].quantity, 3)
        self.assertEqual(result.products[0].product, product1)
        self.assertEqual(len(result.products[0].items), 1)
        self.assertEqual(result.products[0].items[0].quantity, 3)
        self.assertEqual(result.products[1].quantity, 4)
        self.assertEqual(result.products[1].product, product2)
        self.assertEqual(len(result.products[1].items), 2)
        self.assertEqual(result.products[1].items[0].quantity, 4)
        self.assertEqual(result.products[1].items[1].quantity, 36)


class WorkerResourceTests(unittest.TestCase):
    def setUp(self):
        self.session = _setup_db(modules=[
            'altair.app.ticketing.core.models',
            'altair.app.ticketing.lots.models',
        ])

    def tearDown(self):
        _teardown_db()

    def _add_lot(self):
        from ..models import Lot
        lot = Lot()
        self.session.add(lot)
        self.session.flush()
        return lot

    def _getTarget(self):
        from ..workers import WorkerResource
        return WorkerResource

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_lot(self):
        lot = self._add_lot()
        lot_id = str(lot.id)
        message = DummyMessage(params={'lot_id': lot_id})
        target = self._makeOne(message=message)

        self.assertEqual(target.lot_id, lot_id)
        self.assertEqual(target.lot, lot)

class elect_lots_taskTests(unittest.TestCase):
    def _callFUT(self, *args, **kwargs):
        from ..workers import elect_lots_task
        return elect_lots_task(*args, **kwargs)

    def test_no_lot(self):
        context = testing.DummyResource(
            lot_id='testing',
            lot=None,
        )
        dummy_message = DummyMessage()
        self._callFUT(context, dummy_message)
