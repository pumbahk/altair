# -*- encoding:utf-8 -*-
from .searcher import EventSearcher
from altaircms.event.models import Event
from altaircms.testing import setup_db
from altairsite.smartphone.search.forms import DetailSearchForm
from altairsite.mobile.core.const import SalesEnum

import unittest
from pyramid import testing
from datetime import date
from webob.multidict import MultiDict



class DummyRequest(testing.DummyRequest):
    def __init__(self, *args, **kwargs):
        super(DummyRequest, self).__init__(*args, **kwargs)
        for attr in ("POST", "GET", "params"):
            if hasattr(self, attr):
                setattr(self, attr, MultiDict(getattr(self, attr)))

    def allowable(self, model, qs=None):
        return qs or model.query

class TestSearcher(unittest.TestCase):

    def setUp(self):
        setup_db(["altaircms.page.models",
                  "altaircms.tag.models",
                  "altaircms.layout.models",
                  "altaircms.widget.models",
                  "altaircms.event.models",
                  "altaircms.asset.models",
                  "altaircms.models"])

        request = DummyRequest()
        self.searcher = EventSearcher(request)

    def test_search_freeword(self):
        pass

    def test_create_ids(self):
        events = []
        for cnt in range(10):
            event = Event()
            event.id = cnt
            events.append(event)

        ids = self.searcher._create_ids(events)
        self.assertEqual(len(ids), len(events))

    def test_search_sale(self):

        form = DetailSearchForm()

        form.sale.data = int(SalesEnum.ON_SALE)
        ret = self.searcher.get_events_from_sale(form, None)
        self.assertTrue(True)

        form.sale.data = int(SalesEnum.WEEK_SALE)
        ret = self.searcher.get_events_from_sale(form, None)
        self.assertTrue(True)

        form.sale.data = int(SalesEnum.NEAR_SALE_END)
        ret = self.searcher.get_events_from_sale(form, None)
        self.assertTrue(True)















    def test_get_events_from_area(self):

        form = DetailSearchForm()
        form.area.data = 1

        qs = self.searcher.get_events_from_area(form)
        self.assertTrue(True)

        self.searcher.get_events_from_area(form, qs)
        self.assertTrue(True)


    def test_get_event_in_session(self):
        form = DetailSearchForm()
        ret = self.searcher._get_event_in_session(form, None)
        self.assertTrue(True)

    def test_get_events_week_sale(self):
        ret = self.searcher.get_events_week_sale(date.today(), None)
        self.assertTrue(True)

    def test_get_events_near_sale_end(self):
        ret = self.searcher._get_events_near_sale_end(date.today(), 7)
        self.assertTrue(True)

    def test_get_events_from_start_on(self):

        form = DetailSearchForm()
        qs = "query"
        form.year.data = "0"
        ret = self.searcher.get_events_from_start_on(form, qs)
        self.assertEqual(ret, qs)

        form.year.data    = 2013
        form.month.data   = 12
        form.day.data     = 30

        form.since_year.data    = 2013
        form.since_month.data   = 1
        form.since_day.data     = 1

        qs = self.searcher.get_events_from_start_on(form)
        self.assertTrue(True)

    # 販売区分検索
    def test_get_events_from_salessegment(self):
        form = DetailSearchForm()
        qs = self.searcher.get_events_from_salessegment(form)
        self.assertTrue(True)

        form.sales_segment.data = 1
        self.searcher.get_events_from_salessegment(form)
        self.assertTrue(True)

        form.sales_segment.data = 2
        self.searcher.get_events_from_salessegment(form)
        self.assertTrue(True)

if __name__ == "__main__":
    unittest.main()
