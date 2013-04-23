# -*- coding:utf-8 -*-
import unittest
from datetime import datetime
import sys
import os

try:
    from functional_tests.utils import get_here, create_api_key, get_pushed_data_from_backend
    from functional_tests import AppFunctionalTests, logout, login, get_registry
    from functional_tests import delete_models, find_form
except ImportError:
    sys.path.append(os.path.join(os.path.dirname(__name__), "../../"))
    from functional_tests.utils import get_here, create_api_key, get_pushed_data_from_backend
    from functional_tests import AppFunctionalTests, logout, login, get_registry, get_here
    from functional_tests import delete_models, find_form

## here. test_eventpage
CORRECT_API_HEADER_NAME = 'X-Altair-Authorization'

class NotifiedEventInfoFromBackendTests(AppFunctionalTests):
    def tearDown(self):
        from altaircms.event.models import Event
        from altaircms.auth.models import APIKey
        from altaircms.models import Performance, SalesSegment, Ticket
        from altaircms.layout.models import Layout
        delete_models([Performance, SalesSegment, Ticket, APIKey, Event, Layout])

    def test_403_if_hasnot_apikey(self):
        app = self._getTarget()
        response = app.post_json("/api/event/register", params={}, headers=[], status=403)
        self.assertEqual(response.status_int, 403)


    def test_403_if_invalid_apikey(self):
        invalid_api_header = (CORRECT_API_HEADER_NAME, "heke-heke-heke")
        app = self._getTarget()
        response = app.post_json("/api/event/register", params={}, headers=[invalid_api_header], status=403)
        self.assertEqual(response.status_int, 403)
        
    def test_400_if_access_with_correct_apikey_but_invalid_paramater(self):
        import json
        apikey = create_api_key()
        correct_api_header = (CORRECT_API_HEADER_NAME, apikey.apikey)
        app = self._getTarget()

        response = app.post_json("/api/event/register", params={}, headers=[correct_api_header], status=400)
        self.assertEqual(response.status_int, 400)
        result = json.loads(response.ubody)

        self.assertEqual(result["apikey"], apikey.apikey)
        self.assertEqual(result["status"], "error")

    def test_201_access_with_correct_apikey(self):
        import json
        from altaircms.models import Ticket
        from altaircms.event.models import Event
        from altaircms.auth.models import Organization

        apikey = create_api_key()
        correct_api_header = (CORRECT_API_HEADER_NAME, apikey.apikey)
        app = self._getTarget()

        params = json.loads(get_pushed_data_from_backend())
        response = app.post_json("/api/event/register", headers=[correct_api_header], params=params)
        self.assertEqual(response.status_int, 201)


        event = Event.query.one()
        self.assertEqual(event.title, u"マツイ・オン・アイス")
        self.assertEqual(event.backend_id, 40020) #backend id
        self.assertEqual(event.event_open, datetime(2013, 3, 15, 10))
        self.assertEqual(event.event_close, datetime(2013, 3, 26, 19))
        self.assertNotEqual(event.organization_id, 1000)
        self.assertEqual(event.organization_id, Organization.query.filter_by(backend_id=1).one().id)
        self.assertEqual(len(event.performances), 2)

        performance = event.performances[0]
        self.assertEqual(performance.title, u"マツイ・オン・アイス(東京公演)")
        self.assertEqual(performance.backend_id, 40096)
        self.assertEqual(performance.venue, u"まついZEROホール")
        self.assertEqual(performance.open_on, datetime(2013, 3, 15, 8))
        self.assertEqual(performance.start_on, datetime(2013, 3, 15, 10))
        self.assertEqual(performance.end_on, datetime(2013, 3, 15, 13))

        ## todo:change
        self.assertEqual(len(performance.sales), 1)

        sale = performance.sales[0]
        self.assertEqual(sale.group.name, u"一般先行")
        self.assertEqual(sale.backend_id, 40039)
        self.assertEqual(sale.start_on, datetime(2012, 1, 12, 10))
        self.assertEqual(sale.end_on, datetime(2012, 1, 22, 10))

        self.assertEqual(Ticket.query.count(), 8)
        self.assertEqual(len(sale.tickets), 4)

        ticket = performance.sales[0].tickets[0]
        self.assertEqual(ticket.backend_id, 400599)
        self.assertEqual(ticket.name, u"S席大人")
        self.assertEqual(ticket.seattype, u"S席")
        self.assertEqual(ticket.price, 20000)

class EventDetailPageCreateTests(AppFunctionalTests):
    @classmethod
    def setUpClass(cls):
        """layoutの登録にpagetypeが必要なのです """
        from altaircms.models import DBSession
        from altaircms.auth.models import Organization
        from altaircms.page.models import PageType

        app = cls._getTarget()
        with login(app):
            # login時にorganization, pagetypeは作成される
            organization = Organization.query.first()
            DBSession.flush()
            pagetype = PageType.query.filter_by(organization_id=organization.id, name="event_detail").first()
            DBSession.flush()

            ## layoutも作ります
            create_page = app.get("/layout/pagetype/%d/create/input" % pagetype.id)
            layout_title = u"this-is-created-layout-template"
            form = find_form(create_page.forms, action_part="create")
            form.set("title", layout_title)
            form.set("template_filename", "saved-template-name") ## htmlがない
            form.set("filepath", ("layout-create-template.html", ))
            form.submit()

        ## ついでにbackendからデータを通知しておきます
        import json
        apikey = create_api_key()
        correct_api_header = (CORRECT_API_HEADER_NAME, apikey.apikey)
        app = cls._getTarget()
        
        params = json.loads(get_pushed_data_from_backend())
        app.post_json("/api/event/register", headers=[correct_api_header], params=params)

    @classmethod
    def tearDownClass(cls):
        from altaircms.event.models import Event
        from altaircms.auth.models import APIKey
        from altaircms.models import Performance, SalesSegment, Ticket
        from altaircms.page.models import PageSet, Page
        delete_models([Performance, SalesSegment, Ticket, APIKey, PageSet, Page, Event])

    @unittest.skip("skip")
    def test_traverse_event_data(self):
        pass

    def test_it(self):
        from altaircms.event.models import Event
        app = self._getTarget()
        with login(app):
            ## access detail page
            event = Event.query.one()
            event_detail_response = app.get("/event/%s" % event.id)

            ## create pageset
            pageset_create_input_response = event_detail_response.click(href="/event/1/page/create/input")
            form = find_form(pageset_create_input_response.forms, action_part="create")
            form.set("name", u"demo-page")
            form.set("url", u"demo-url")
            form.set("title", u"this-is-page-title")
            form.set("publish_begin", datetime(1900, 1, 1))
            form.set("description", u"ababababbaba-ababababbaba-ababababbaba-ababababbaba-ababababbaba")
            form.set("tags", u"event demo page tag public")
            form.set("private_tags", u"event demo page tag public")
            confirm_response = form.submit()

            form = find_form(confirm_response.forms, action_part="create")
            submit_response = form.submit()
            
            self.assertEqual(submit_response.status_int, 302)

            # page is created!!,  to be continued ...

        
if __name__ == "__main__":
    def setUpModule():
        from functional_tests import get_app
        get_app()
    unittest.main()
