# -*- coding:utf-8 -*- 

import unittest
from altaircms.plugins.widget.calendar.models import CalendarWidget

config  = None
def setUpModule():
    global config
    from altaircms import testing as mytesting
    mytesting.create_db(force=False)
    config = mytesting.config()

def tearDownModule():
    from pyramid.testing import tearDown
    tearDown()

class WidgetTestSourceMixn(object):
    def _makePage(self, id=None):
        from altaircms.page.models import Page
        return Page.from_dict({"id": id})

    def _getSession(self):
        from altaircms.models import DBSession
        return DBSession

    def _with_session(self, session, *args):
        for e in args:
            session.add(e)
        session.flush()
        return session

    def _makeRequest(self, **kwargs):
        from pyramid.testing import DummyRequest
        request = DummyRequest()
        for k, v in kwargs.iteritems():
            setattr(request, k, v)
        return request
        
class CalendarWidgetViewTests(WidgetTestSourceMixn, 
                          unittest.TestCase):
    def setUp(self):
        self.config = config

    def tearDown(self):
        import transaction
        transaction.abort()

    def _makeTarget(self, request):
        from altaircms.plugins.widget.calendar.views import CalendarWidgetView
        from altaircms.plugins.widget.calendar.models import CalendarWidgetResource
        request.context = CalendarWidgetResource(request)
        return CalendarWidgetView(request)

    def test_create(self):
        """ test creating CalendarWidget.
        check:
          1. Calendar Widget is created,  successfully.
          2. Calendar Widget and Page object is bounded
        """
        session = self._getSession()
        calendar_type = "obi"
        self._with_session(session, self._makePage(id=1))
        request = self._makeRequest(json_body={
                "page_id": 1, "pk": None, "data": {"calendar_type": calendar_type}
                })
        view = self._makeTarget(request)
        expexted = {"page_id": 1,
                    "pk": 1,
                    "data": {"calendar_type": calendar_type}}
        self.assertEquals(view.create(), expexted)

        created = CalendarWidget.query.one()
        self.assertEquals(CalendarWidget.query.count(), 1)
        self.assertEquals(created.page.id, 1)
        self.assertEquals(created.calendar_type, "obi")

    def _create_widget(self, session, page_id=1, data=None):
        self._with_session(session, self._makePage(id=1))
        request = self._makeRequest(json_body={
                "page_id": 1, "pk": None, "data": data or None
                })
        view = self._makeTarget(request)
        return view.create()["pk"]

    def test_update(self):
        session = self._getSession()
        pk = self._create_widget(session, page_id=1, data={"calendar_type": "obi"})
        request = self._makeRequest(json_body={
                "page_id": 1, "pk": pk, "data": {"calendar_type": "tab", 
                                                 "from_date": "2011-1-1",
                                                 "to_date": "2011-2-1"
}
                })
        view = self._makeTarget(request)
        expexted = {"page_id": 1,
                    "pk": pk,
                    "data": {"calendar_type": "tab", 
                             "from_date": "2011-1-1",
                             "to_date": "2011-2-1"
                             } }
        self.assertEquals(view.update(), expexted)

        updated = CalendarWidget.query.one()
        self.assertEquals(CalendarWidget.query.count(), 1)
        self.assertEquals(updated.calendar_type, "tab")

    def test_delete(self):
        session = self._getSession()
        pk = self._create_widget(session, page_id=1, data={"calendar_type": "obi"})

        request = self._makeRequest(json_body={"pk": pk})
        view = self._makeTarget(request)
        expexted = {"status": "ok"}
        self.assertEquals(view.delete(), expexted)

        self.assertEquals(CalendarWidget.query.count(), 0)

        from altaircms.page.models import Page
        self.assertNotEquals(Page.query.count(), 0)

    def test_getdialog(self):
        """ add asset env,  then dialog.mako is rendered successfully or not
        (this test is not checking about html format)
        """
        session = self._getSession()
        self._with_session(session, self._makePage(id=1))

        request = self._makeRequest(GET={"page_id": 1})
        view = self._makeTarget(request)
        
        result = view.dialog()
        self.assertEquals(sorted(["form"]), 
                         sorted(result.keys()))

if __name__ == "__main__":
    unittest.main()
