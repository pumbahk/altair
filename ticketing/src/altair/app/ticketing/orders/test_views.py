# -*- coding:utf-8 -*-
import unittest
import mock
from pyramid.testing import DummyResource
from altair.app.ticketing.testing import DummyRequest
from altair.app.ticketing.testing import _setup_db, _teardown_db

class OrderDetailViewTests(unittest.TestCase):
    def setUp(self):
        self.session = _setup_db(
            modules=[
                'altair.app.ticketing.core.models',
                'altair.app.ticketing.lots.models',
                'altair.app.ticketing.orders.models',
                ]
            )

    def tearDown(self):
        _teardown_db()

    def _getTarget(self):
        from altair.app.ticketing.orders.views import OrderDetailView
        return OrderDetailView

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    @mock.patch.multiple("altair.app.ticketing.orders.models.Order", get=mock.DEFAULT, save=mock.DEFAULT)
    def test__edit_memo_on_order(self, get, save):
        from altair.app.ticketing.orders.models import Order
        order = Order(
            id=1,
            order_no='XX0000000000',
            organization_id=1,
            total_amount=0,
            transaction_fee=0,
            delivery_fee=0,
            system_fee=0,
            special_fee=0
            )
        self.session.add(order)
        self.session.flush()
        get.return_value = order

        def _save():
            self.assertEquals(order.attributes.keys(), ["memo_on_order2"])
            self.assertEquals(order.attributes["memo_on_order2"], "123456789")
        save.side_effect = _save
        request = DummyRequest(
            matchdict={u"order_id": u"1"},
            json_body={
                u"memo_on_order1": u"", 
                u"memo_on_order2": u"123456789", 
                u"memo_on_order3": u""
                }
            )
        context = DummyResource(
            organization=DummyResource(id=1)
            )
        target = self._makeOne(context, request)
        target.edit_memo_on_order()
