# -*- coding:utf-8 -*-
import unittest
from datetime import datetime

def setup_ticket(*args, **kwargs):
    from altair.app.ticketing.core.models import Ticket
    return Ticket(*args, **kwargs)

class getTemplateTests(unittest.TestCase):
    def _getTarget(self):
        from .svg_builder import TicketModelControl
        return TicketModelControl

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_it(self):
        target = self._makeOne()
        ticket = setup_ticket(data={"drawing": "<svg>"})
        result = target.get_template(ticket)
        self.assertEquals(result, "<svg>")

class DataOverWriteTests(unittest.TestCase):
    def _getTarget(self):
        from .svg_builder import TicketModelControl
        return TicketModelControl

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_it(self):
        target = self._makeOne()
        data = {"k": "v"}

        ticket = setup_ticket(data={})
        result = target.get_vals(ticket, data)
        self.assertEquals(result, {"k": "v"})

    def test_with_default(self):
        target = self._makeOne()
        data = {"k": "v"}
        ticket = setup_ticket(data={"vars_defaults": {"qr": "qr-default"}})

        result = target.get_vals(ticket, data)
        self.assertEquals(result, {"k": "v", "qr": "qr-default"})

    def test_with_overwrite__order_is_notfound(self):
        target = self._makeOne()
        target.overwrite_data = {"k": "v is overwriten"}
        data = {"k": "v"}

        ticket = setup_ticket(data={})
        result = target.get_vals(ticket, data)
        self.assertEquals(result, {"k": "v"})

    def test_with_overwrite__order_is_found(self):
        target = self._makeOne()
        target.overwrite_data = {"*Order.id*": {"k": "v is overwriten"}}
        data = {
            "k": "v", 
            "order": {"id": "*Order.id*"}
        }

        ticket = setup_ticket(data={})
        result = target.get_vals(ticket, data)
        ## 上書きされている
        self.assertEquals(result["k"], "v is overwriten")

        ## order.idは除去 => 無理
        self.assertEquals(result["order"], {"id": "*Order.id*"})

    def test_with_overwrite__order_is_found__aux(self):
        target = self._makeOne()
        target.overwrite_data = {"*Order.id*": {
            "aux": {"a": {"b": "c"}}
        }}
        data = {
            "aux": {"x": "y"}, 
            "order": {"id": "*Order.id*"},
        }

        ticket = setup_ticket(data={})
        result = target.get_vals(ticket, data)
        ## 上書きされている
        self.assertEquals(result["aux"], {"a": {"b": "c"}, "x": "y"})

        ## order.idは除去 => 無理
        self.assertEquals(result["order"], {"id": "*Order.id*"})


class OrderAttributesDataTests(unittest.TestCase):
    def setUp(self):
        from altair.app.ticketing.testing import _setup_db
        self.session = _setup_db(["altair.app.ticketing.core.models"])

    def tearDown(self):
        import transaction
        transaction.abort()
        from altair.app.ticketing.testing import _teardown_db
        _teardown_db()

    def _getTarget(self):
        from .svg_builder import OrderAttributesForOverwriteData
        return OrderAttributesForOverwriteData

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_it(self):
        from altair.app.ticketing.core.models import Order
        from altair.app.ticketing.models import DBSession

        order_id = 9999
        order = Order(
            id=order_id,  
            shipping_address_id=-1, #xxx:
            total_amount=600, 
            system_fee=100, 
            transaction_fee=200, 
            delivery_fee=300, 
            special_fee=400, 
            multicheckout_approval_no=":multicheckout_approval_no", 
            order_no="no", 
            paid_at=datetime(2000, 1, 1, 1, 10), 
            delivered_at=None, 
            canceled_at=None, 
            created_at=datetime(2000, 1, 1, 1), 
            issued_at=datetime(2000, 1, 1, 1, 13),
            issuing_start_at=datetime(1970, 1, 1),
            issuing_end_at=datetime(1970, 1, 1),
            payment_start_at=datetime(1970, 1, 1),
            payment_due_at=datetime(1970, 1, 1),
            organization_id=-1, 
            payment_delivery_method_pair_id=-1, 
            performance_id=-1, 
        )
        DBSession.add(order)

        order.attributes[u"venue"] = u"overwriten venue"
        order.attributes[u"aux.税込み表記"] = u"[o_o]"
        target = self._makeOne()
        result = target[order_id]
        self.assertEquals(result, {
            u"venue": "overwriten venue",
            u"aux": {u"税込み表記": u"[o_o]"}
        })

class SVGBuilderUseMultipleTests(unittest.TestCase):
    def _getTarget(self):
        from altair.app.ticketing.tickets.svg_builder import TicketModelControl
        return TicketModelControl

    def _makeOne(self, *args, **kwargs):
        class Contorl(self._getTarget()):
            def overwrite_attributes(self, x):
                return x
        return Contorl(*args, **kwargs)

    def test_it__6512(self):
        class ticket(object):
            vars_defaults = {}

        vals = self._makeOne().get_vals(ticket, {"seat": "a"}) #指定席
        self.assertEqual(vals, {"seat": "a"})

        vals = self._makeOne().get_vals(ticket, {}) #自由席
        self.assertEqual(vals, {})

