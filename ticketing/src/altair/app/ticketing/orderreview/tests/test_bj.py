# -*- coding:utf-8 -*-

""" TBA
"""

import unittest
from pyramid import testing
from altair.app.ticketing.testing import DummyRequest, _setup_db, _teardown_db

class OrderReviewResourceTests(unittest.TestCase):
    def setUp(self):
        self.session = _setup_db([
            'altair.app.ticketing.core.models',
            'altair.app.ticketing.users.models',
            'altair.app.ticketing.orders.models',
            'altair.app.ticketing.lots.models',
            'altair.app.ticketing.cart.models',
            ])
        self.config = testing.setUp()
        self.config.include('altair.app.ticketing.cart.request')
        from altair.app.ticketing.orders.models import Order
        from altair.app.ticketing.core.models import Organization, ShippingAddress, Host, SalesSegment, SalesSegmentSetting, PaymentDeliveryMethodPair, PaymentMethod, DeliveryMethod
        self.organization = Organization(short_name='AA')
        self.host = Host(host_name='example.com', organization=self.organization)
        self.session.add(self.organization)
        self.session.add(self.host)
        self.session.flush()
        order = Order(
            ordered_from=self.organization,
            sales_segment=SalesSegment(setting=SalesSegmentSetting(disp_orderreview=True)),
            order_no='000000000001',
            total_amount=0,
            system_fee=0,
            transaction_fee=0,
            delivery_fee=0,
            payment_delivery_pair=PaymentDeliveryMethodPair(
                system_fee=0,
                transaction_fee=0,
                discount=0,
                payment_method=PaymentMethod(
                    fee=0
                    ),
                delivery_method=DeliveryMethod(
                    )
                ),
            shipping_address=ShippingAddress(tel_1='0000')
            )
        self.order = order
        self.session.add(order)
        from altair.sqlahelper import register_sessionmaker_with_engine
        register_sessionmaker_with_engine(
            self.config.registry,
            'slave',
            self.session.bind,
            self.session.session_factory
            )

    def tearDown(self):
        _teardown_db()
        testing.tearDown()

    def _getTarget(self):
        from ..resources import OrderReviewResource
        return OrderReviewResource

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_order_no(self):
        from altair.app.ticketing.core.models import Host, Organization
        from altair.app.ticketing.users.models import Membership
        request = DummyRequest(POST=dict(order_no='000000000001', tel='0000'), host='example.com')
        membership = Membership(organization=self.organization, name="89ers")
        self.session.add(membership)
        self.session.flush()

        target = self._makeOne(request)
        self.assertEqual(target.order.order_no, '000000000001')
        self.assertEqual(target.primary_membership.id, membership.id)
