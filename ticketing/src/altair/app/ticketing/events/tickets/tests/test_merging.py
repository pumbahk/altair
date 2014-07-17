# -*- coding:utf-8 -*-
import unittest
import altair.app.ticketing.core.models
import altair.app.ticketing.orders.models

class CollectVarsWithDefaultTests(unittest.TestCase):
    def _getTarget(self):
        from altair.app.ticketing.events.tickets.merging import TicketVarsCollector
        return TicketVarsCollector

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def _makeTemplate(self, drawing, fill_mapping={}):
        from altair.app.ticketing.core.models import Ticket
        data = {
            "drawing": drawing, 
            "fill_mapping": fill_mapping
        }
        return Ticket(data=data)

    def test_it_with_base_template_ticket(self):
        ticket = self._makeTemplate(
            drawing="""hi, test message.""",
            fill_mapping={
                "message": "test message",
                "prefix": "hi",
            })
        ticket.base_template = self._makeTemplate(
            drawing="""{{prefix}}, {{message}}"""
        )

        target = self._makeOne(ticket)
        self.assertTrue(target.is_support())
        result = target.collect()

        self.assertEqual(dict(result), {"prefix": "hi", "message": "test message"})

    def test_it_without_base_template(self):
        ticket = self._makeTemplate(
            drawing="""hi, test message.""",
            fill_mapping={
                "message": "test message",
                "prefix": "hi",
            })
        target = self._makeOne(ticket)
        self.assertFalse(target.is_support())
        result = target.collect()

        self.assertEqual(dict(result), {})


    def test_it__force_self_template__is_True__use_self_template(self):
        ticket = self._makeTemplate(
            drawing="""** base template **""",
        )
        ticket.base_template = self._makeTemplate(
            drawing="""{{prefix}}, {{message}}"""
        )

        target = self._makeOne(ticket, force_self_template=True)

        self.assertFalse(target.is_support())
        self.assertEqual(target.template, "** base template **")


class EmitToAnotherTemplateTests(unittest.TestCase):
    def _makeTemplate(self, drawing, fill_mapping):
        from altair.app.ticketing.core.models import Ticket
        data = {
            "drawing": drawing, 
            "fill_mapping": fill_mapping
        }
        return Ticket(data=data)

    def _callFUT(self, *args, **kwargs):
        from altair.app.ticketing.events.tickets.merging import emit_to_another_template
        return emit_to_another_template(*args, **kwargs)

    def test_it(self):
        current_ticket = self._makeTemplate(
            drawing="""hi, test message.""",
            fill_mapping={
                "message": "test message",
                "prefix": "hi",
            })

        another_template = self._makeTemplate(
            drawing="""<{{prefix}}>{{message}}</{{prefix}}>""",
            fill_mapping=None
        )

        result = self._callFUT(another_template, current_ticket)
        self.assertEqual(result, "<hi>test message</hi>")
