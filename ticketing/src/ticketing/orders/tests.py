# -*- coding:utf-8 -*-

""" TBA
"""

import unittest
from pyramid import testing
from ..testing import _setup_db, _teardown_db

class OrderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.session = _setup_db(
            modules=[
                'ticketing.core.models',
                'ticketing.orders.models',
            ],
        )

    @classmethod
    def tearDownClass(cls):
        _teardown_db()

    def tearDown(self):
        import transaction
        transaction.abort()
    def _getTarget(self):
        from . import models
        return models.Order

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    @unittest.skip
    def test_create_from_cart(self):

        from ..cart import models as c_models
        from ..core import models as core_models

        cart = c_models.Cart(
            products=[
                c_models.CartedProduct(
                    items=[
                        c_models.CartedProductItem(
                            product_item=core_models.ProductItem(price=100.00),
                            seats=[core_models.Seat(id=3333)],
                        ),
                    ],
                    product=core_models.Product(
                        price=100.00,
                    ),
                    quantity=1,
                ),
            ],
        )

        target = self._getTarget()

        result = target.create_from_cart(cart)

        self.assertIsNotNone(result)
        self.assertEqual(len(result.ordered_products), 1)
        ordered_product = result.ordered_products[0]
        self.assertEqual(ordered_product.price, 100.00)
        self.assertEqual(len(ordered_product.ordered_product_items), 1)
        ordered_product_item = ordered_product.ordered_product_items[0]
        self.assertEqual(ordered_product_item.price, 100.00)
        self.assertEqual(len(ordered_product_item.seats), 1)
        seat = ordered_product_item.seats[0]
        self.assertEqual(seat.id, 3333)


class OrderedProductItemTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.session = _setup_db(
            modules=[
                'ticketing.core.models',
                'ticketing.orders.models',
            ],
        )

    @classmethod
    def tearDownClass(cls):
        _teardown_db()

    def tearDown(self):
        import transaction
        transaction.abort()

    def _getTarget(self):
        from .models import OrderedProductItem
        return OrderedProductItem

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def _create_seats(self, num):
        from ticketing.core.models import Seat, Venue, Site, Organization
        organization = Organization()
        site = Site()
        venue = Venue(site=site, organization=organization)
        return [Seat(name=u"Seat %d" % i, venue=venue,
                     l0_id="seat-%d" % i) for i in range(num)]

    def _create_seat_statuses(self, seats):
        from ticketing.core.models import SeatStatus, SeatStatusEnum
        return [SeatStatus(seat_id=s.id,
                    status=int(SeatStatusEnum.Ordered)) for s in seats]

    def _create_product_item(self):
        from ticketing.core.models import ProductItem, Stock, Performance
        performance = Performance()
        stock = Stock(performance=performance)
        return ProductItem(stock=stock, price=100.0)

    def test_release(self):
        seats = self._create_seats(4)
        map(self.session.add, seats)
        self.session.flush()
        statuses = self._create_seat_statuses(seats)
        map(self.session.add, statuses)
        product_item = self._create_product_item()
        self.session.add(product_item)
        self.session.flush()

        target = self._makeOne(seats=seats, product_item=product_item)

        target.release()
        self._assertStatus(target.seats)

    def _assertStatus(self, seats):
        from ticketing.core.models import SeatStatusEnum, SeatStatus
        statuses = self.session.query(SeatStatus).filter(SeatStatus.seat_id.in_([s.id for s in seats]))
        for s in statuses:
            self.assertEqual(s.status, int(SeatStatusEnum.Vacant))
