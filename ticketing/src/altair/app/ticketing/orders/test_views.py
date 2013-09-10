# -*- coding:utf-8 -*-
import unittest
import mock

class OrderDetailViewTests(unittest.TestCase):
    def _getTarget(self):
        from altair.app.ticketing.orders.views import OrderDetailView
        return OrderDetailView

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    @mock.patch.multiple("altair.app.ticketing.core.models.Order", get=mock.DEFAULT, save=mock.DEFAULT)
    def test__edit_memo_on_order(self, get, save):
        from altair.app.ticketing.core.models import Order
        order = Order(id=1)
        get.return_value = order

        def _save():
            self.assertEquals(order.attributes.keys(), ["memo_on_order2"])
            self.assertEquals(order.attributes["memo_on_order2"], "123456789")
        save.side_effect = _save
        class request:
            matchdict = {"order_id": 1}
            json_body = {
                "memo_on_order1": "", 
                "memo_on_order2": "123456789", 
                "memo_on_order3": ""
            }
        class context:
            class organization:
               id = 1 
        target = self._makeOne(context, request)
        target.edit_memo_on_order()
