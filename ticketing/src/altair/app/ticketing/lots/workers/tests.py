import unittest
import mock
from pyramid import testing
from altair.app.ticketing.testing import _setup_db, _teardown_db, DummyRequest
from altair.app.ticketing.core.testing import CoreTestMixin


class lot_wish_cartTests(unittest.TestCase):
    def setUp(self):
        self.session = _setup_db([
            'altair.app.ticketing.orders.models',
            'altair.app.ticketing.lots.models',
            'altair.app.ticketing.core.models',
            'altair.app.ticketing.cart.models',
            ])
   
    def tearDown(self):
        _teardown_db()

    def _callFUT(self, *args, **kwargs):
        from .election import lot_wish_cart
        return lot_wish_cart(*args, **kwargs)

    def test_it(self):
        from altair.app.ticketing.core.models import (
            Performance, Product, PaymentDeliveryMethodPair, ProductItem,
            PaymentMethod, DeliveryMethod,
            SalesSegment,
            Event,
            EventSetting,
            Organization,
            FeeTypeEnum,
        )
        from altair.app.ticketing.cart.models import CartSetting
        from ..models import LotEntryWish, LotEntry, Lot, LotEntryProduct
        product1 = Product(price=100,
                           items=[ProductItem(quantity=1, price=100)])
        product2 = Product(price=150,
                           items=[ProductItem(quantity=1, price=75), ProductItem(quantity=9, price=75)])

        event = Event(
            organization=Organization(short_name=u'test', name=u'test'),
            setting=EventSetting(
                cart_setting=CartSetting()
                )
            )
        self.session.add(event)
        wish = LotEntryWish(
            performance=Performance(
                event=event
                ),
            lot_entry=LotEntry(
                lot=Lot(
                    event=event,
                    organization=event.organization,
                    system_fee=9999999999999999999,# not used
                    sales_segment=SalesSegment(),
                    ), 
                entry_no='testing-entry',
                payment_delivery_method_pair=PaymentDeliveryMethodPair(
                    system_fee=11,
                    system_fee_type=FeeTypeEnum.Once.v[0],
                    transaction_fee=111,
                    delivery_fee_per_order=0,
                    delivery_fee_per_principal_ticket=0,
                    delivery_fee_per_subticket=0,
                    payment_method=PaymentMethod(fee=0),
                    delivery_method=DeliveryMethod(fee_per_order=0),
                    discount=0
                    ),
               ),
            products=[
                LotEntryProduct(
                    quantity=3,
                    product=product1
                    ),
                LotEntryProduct(
                    quantity=4,
                    product=product2
                    ),
                ]
            )
        wish2 = LotEntryWish(
            performance=wish.performance,
            products=[
                LotEntryProduct(
                    quantity=10,
                    product=product1
                    ),
                ]
            )

        wish.lot_entry.wishes.append(wish2)

        # precondition
        self.assertEqual(wish.lot_entry.max_amount, 1122) # 100 * 10 + 111 + 11

        result = self._callFUT(wish)

        self.assertEqual(result.order_no, 'testing-entry')
        self.assertEqual(result.total_amount, 1022)
        self.assertEqual(len(result.items), 2)
        self.assertEqual(result.items[0].quantity, 3)
        self.assertEqual(result.items[0].product, product1)
        self.assertEqual(len(result.items[0].elements), 1)
        self.assertEqual(result.items[0].elements[0].quantity, 3)
        self.assertEqual(result.items[1].quantity, 4)
        self.assertEqual(result.items[1].product, product2)
        self.assertEqual(len(result.items[1].elements), 2)
        self.assertEqual(result.items[1].elements[0].quantity, 4)
        self.assertEqual(result.items[1].elements[1].quantity, 36)


class ElectionWorkerResourceTests(unittest.TestCase):
    def setUp(self):
        self.session = _setup_db(modules=[
            'altair.app.ticketing.core.models',
            'altair.app.ticketing.lots.models',
            'altair.app.ticketing.orders.models',
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
        from .election import ElectionWorkerResource
        return ElectionWorkerResource

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_lot(self):
        lot = self._add_lot()
        lot_id = str(lot.id)
        request = DummyRequest(params={'lot_id': lot_id})
        target = self._makeOne(request=request)

        self.assertEqual(target.lot_id, lot_id)
        self.assertEqual(target.lot, lot)

class elect_lots_taskTests(unittest.TestCase, CoreTestMixin):
    def setUp(self):
        from altair.sqlahelper import register_sessionmaker_with_engine
        self.config = testing.setUp()
        self.session = _setup_db([
            'altair.app.ticketing.orders.models',
            'altair.app.ticketing.lots.models',
            'altair.app.ticketing.core.models',
            'altair.app.ticketing.cart.models',
            ])
        register_sessionmaker_with_engine(
            self.config.registry,
            'lot_work_history',
            self.session.bind
            )
        CoreTestMixin.setUp(self)
        from altair.app.ticketing.core.models import OrganizationSetting, SalesSegmentGroup, SalesSegment, Product
        from altair.app.ticketing.cart.models import CartSetting
        self.sales_segment_group = SalesSegmentGroup(event=self.event)
        self.organization.settings = [OrganizationSetting(cart_setting=CartSetting())]
        self.sales_segment = SalesSegment(sales_segment_group=self.sales_segment_group)
        from ..models import Lot, LotElectWork, LotEntry, LotEntryWish, LotEntryProduct
        import transaction
        self.payment_delivery_method_pairs = self._create_payment_delivery_method_pairs(self.sales_segment_group)
        self.lot = Lot()
        self.session.add(self.lot)
        self.lot_entry = LotEntry(lot=self.lot, payment_delivery_method_pair=self.payment_delivery_method_pairs[0])
        self.session.add(self.lot_entry)
        self.lot_entry_wish = LotEntryWish(
            wish_order=1,
            lot_entry=self.lot_entry,
            performance=self.performance,
            products=[
                LotEntryProduct(
                    product=Product(sales_segment=self.sales_segment, price=0)
                    )
                ])
        self.session.add(self.lot_entry_wish)
        self.work = LotElectWork(lot_entry_no='XX0000000000', wish_order=1)
        self.session.add(self.work)
        self.session.flush()
        transaction.commit()
        self.lot = self.session.merge(self.lot)
        self.lot_entry = self.session.merge(self.lot_entry)
        self.lot_entry_wish = self.session.merge(self.lot_entry_wish)
        self.work = self.session.merge(self.work)

        from altair.app.ticketing.cart.interfaces import IStocker
        from pyramid.interfaces import IRequest
        self.dummy_stocker = mock.Mock()
        self.config.registry.registerAdapter(self.dummy_stocker, [IRequest], IStocker)
   
    def tearDown(self):
        _teardown_db()
        testing.tearDown()

    def _callFUT(self, *args, **kwargs):
        from .election import elect_lots_task
        return elect_lots_task(*args, **kwargs)

    @mock.patch('altair.app.ticketing.lots.workers.election.Payment')
    def test_no_lot(self, payment):
        from altair.app.ticketing.orders.models import Order
        order = Order(order_no=self.lot_entry.entry_no)
        payment.return_value.call_payment.return_value = order
        context = testing.DummyResource(
            lot_id='testing',
            lot=self.lot,
            work=self.work
        )
        dummy_request = DummyRequest()
        self._callFUT(context, dummy_request)
        self.assertEqual(self.lot_entry.order, order)
