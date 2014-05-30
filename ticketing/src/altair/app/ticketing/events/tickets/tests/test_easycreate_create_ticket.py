# -*- coding:utf-8 -*-
import unittest

## hmm.. InvalidRequestError: 'Order' failed to locate a name ("name 'Order' is not defined")
import altair.app.ticketing.orders.models
import altair.app.ticketing.core.models

def normalize(x):
    import re
    return re.sub(r"\s+", " ", x.strip())

class EasyCreateTicketTests(unittest.TestCase):
    sample_svg  = u"""\
    <ns0:svg xmlns:ns0="http://www.w3.org/2000/svg" height="230.31496" id="svg2" version="1.2" width="628.93701"> </ns0:svg>
    """

    def _callFUT(self, *args, **kwargs):
        from altair.app.ticketing.events.tickets.views import create_ticket_from_form
        return create_ticket_from_form(*args, **kwargs)

    def _makeEvent(self, event_id):
        from altair.app.ticketing.core.models import Organization, Event
        event = Event(id=event_id, organization=Organization())
        return event

    def _makeBaseTicket(self, organization, base_template_id, ticket_format_id=-1):
        from altair.app.ticketing.core.models import Ticket, TicketFormat
        return Ticket(
            id=base_template_id,
            priced=True,
            always_reissueable=True,
            ticket_format_id=ticket_format_id,
            ticket_format=TicketFormat(id=ticket_format_id),
            organization = organization
        )

    def _makeForm(self, request, base_ticket, event):
        from altair.app.ticketing.events.tickets.forms import EasyCreateTemplateUploadForm
        return EasyCreateTemplateUploadForm(request.POST).configure(event, base_ticket)

    def _makeRequest(self, base_template_id, name="anything name", drawing="", fill_mapping="{}", cover_print=False):
        from altair.app.ticketing.testing import DummyRequest
        return DummyRequest(POST=dict(
            base_template_id=base_template_id,
            cover_print=cover_print,
            name=name,
            preview_type="default",
            template_kind="base",
            drawing=drawing,
            fill_mapping=fill_mapping
        ))

    def test_defaults_values__are_set__after_callFUT(self):
        template_id = 10

        event = self._makeEvent(event_id=1)
        base_ticket = self._makeBaseTicket(event.organization, template_id)
        request = self._makeRequest(template_id, drawing=self.sample_svg)
        form = self._makeForm(request, base_ticket, event)

        self.assertTrue(form.validate())

        result = self._callFUT(form, base_ticket)

        self.assertTrue(result.always_reissueable)
        self.assertTrue(result.priced)
        self.assertEqual(result.organization, event.organization)

    def test_form_values__are_set__after_callFUT(self):
        template_id = 10

        event = self._makeEvent(event_id=1)
        base_ticket = self._makeBaseTicket(event.organization, template_id, ticket_format_id=100)
        request = self._makeRequest(template_id,
                                    name="*new ticket*", 
                                    fill_mapping=u'{"oneline": "this is test"}', 
                                    drawing=self.sample_svg,
                                    cover_print=True)
        form = self._makeForm(request, base_ticket, event)

        self.assertTrue(form.validate())

        result = self._callFUT(form, base_ticket)

        self.assertTrue(result.name, "*new ticket*")
        self.assertEqual(result.ticket_format_id, 100)
        self.assertEqual(result.cover_print, True)
        self.assertEqual(result.event_id, 1)
        self.assertEqual(result.base_template, base_ticket)

        self.assertEqual(normalize(result.data["drawing"]), normalize(self.sample_svg))
        self.assertEqual(result.data["fill_mapping"], {"oneline": "this is test"})

