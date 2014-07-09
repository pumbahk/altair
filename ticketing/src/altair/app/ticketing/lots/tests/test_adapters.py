import unittest
from altair.app.ticketing.testing import _setup_db, _teardown_db
from pyramid import testing 

class LotSessionCartTest(unittest.TestCase):
    def _getTarget(self):
        from ..adapters import LotSessionCart
        return LotSessionCart

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def setUp(self):
        from ..models import Lot
        from altair.app.ticketing.core.models import (
            Product,
            ProductItem,
            TicketBundle,
            Ticket,
            TicketFormat,
            PaymentDeliveryMethodPair,
            SalesSegment,
            PaymentMethod,
            DeliveryMethod,
            FeeTypeEnum,
            )
        self.request = testing.DummyRequest()
        self.session = _setup_db([
            'altair.app.ticketing.lots.models',
            'altair.app.ticketing.orders.models',
            'altair.app.ticketing.core.models',
            ])
        self.lot = Lot(
            sales_segment=SalesSegment()
            )
        self.session.add(self.lot)
        self.delivery_method = DeliveryMethod(
            fee_type=FeeTypeEnum.PerUnit.v[0],
            fee=20
            )
        self.session.add(self.delivery_method)
        self.session.add(
            Product(
                id=1,
                price=1,
                items=[
                    ProductItem(
                        price=1,
                        ticket_bundle=TicketBundle(
                            tickets=[
                                Ticket(
                                    priced=True,
                                    ticket_format=TicketFormat(
                                        name='X',
                                        delivery_methods=[
                                            self.delivery_method
                                            ]
                                        )
                                    )
                                ]
                            )
                        )
                    ]
                )
            )
        self.session.add(
            Product(
                id=2,
                price=2,
                items=[
                    ProductItem(
                        price=2,
                        ticket_bundle=TicketBundle(
                            tickets=[
                                Ticket(
                                    priced=True,
                                    ticket_format=TicketFormat(
                                        name='Y',
                                        delivery_methods=[]
                                        )
                                    ),
                                Ticket(
                                    priced=False,
                                    ticket_format=TicketFormat(
                                        name='Z',
                                        delivery_methods=[
                                            self.delivery_method
                                            ]
                                        )
                                    )
                                ]
                            )
                        )
                    ]
                )
            )
        self.payment_delivery_method_pair = PaymentDeliveryMethodPair(
            id=1,
            system_fee=3,
            delivery_fee=4,
            transaction_fee=5,
            discount=6,
            payment_method=PaymentMethod(
                fee_type=FeeTypeEnum.Once.v[0],
                fee=50
                ),
            delivery_method=self.delivery_method
            )
        self.session.add(self.payment_delivery_method_pair)
        self.session.flush()

    def tearDown(self):
        _teardown_db()

    def test_total_amount(self):
        entry_dict = {
            'entry_no': '000000000000',
            'payment_delivery_method_pair_id': 1,
            'shipping_address': {},
            'gender': '1',
            'birthday': {
                'year': 1970,
                'month': 1,
                'day': 1,
                },
            'memo': '',
            'wishes': [
                {
                    'wished_products': [
                        {
                            'product_id': 1,
                            'quantity': 1,
                            },
                        {
                            'product_id': 2,
                            'quantity': 2,
                            }
                        ],
                    },
                {
                    'wished_products': [
                        {
                            'product_id': 1,
                            'quantity': 2,
                            },
                        {
                            'product_id': 2,
                            'quantity': 3,
                            }
                        ],
                    }
                ]
            }
        target = self._makeOne(entry_dict, self.request, self.lot)
        self.assertEqual(target.total_amount, 1 * 2 + 2 * 3 + 3 + 4 * 2 + 5)

        
