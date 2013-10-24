# -*- coding:utf-8 -*-
import unittest

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
        self.assertEquals(result, {
            "k": "v is overwriten", 
            "order": {"id": "*Order.id*"}
        })

## test: overwrite_data
