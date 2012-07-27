# -*- coding:utf-8 -*- 

import unittest
from altaircms.plugins.widget.reuse.models import ReuseWidget

config  = None
def setUpModule():
    global config
    from altaircms import testing as mytesting
    mytesting.setup_db(["altaircms.page.models", "altaircms.tag.models", "altaircms.event.models", "altaircms.asset.models"])
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
        
class ReuseWidgetViewTests(WidgetTestSourceMixn, 
                          unittest.TestCase):
    def setUp(self):
        self.config = config

    def tearDown(self):
        import transaction
        transaction.abort()

    def _makeTarget(self, request):
        from altaircms.plugins.widget.reuse.views import ReuseWidgetView
        from altaircms.plugins.widget.reuse.models import ReuseWidgetResource
        request.context = ReuseWidgetResource(request)
        return ReuseWidgetView(request)

    def test_create(self):
        """ test creating ReuseWidget.
        check:
          1. Reuse Widget is created,  successfully.
          2. Reuse Widget and Page object is bounded
        """
        session = self._getSession()

        self._with_session(session, self._makePage(id=1), self._makePage(id=2))
        request = self._makeRequest(json_body={
                "page_id": 1, "pk": None,
                "data": {"width": 100, "source_page_id": 2, }
                })
        view = self._makeTarget(request)
        expexted = {"page_id": 1,
                    "pk": 1,
                    "data": {"width": 100, "source_page_id": 2 }}
        self.assertEquals(view.create(), expexted)

        created = ReuseWidget.query.one()
        self.assertEquals(ReuseWidget.query.count(), 1)
        self.assertEquals(created.page.id, 1)
        self.assertEquals(created.width, 100)
        self.assertEquals(created.source_page.id, 2)

    def _create_widget(self, session, page_id=1, data=None):
        self._with_session(session, self._makePage(id=1))
        request = self._makeRequest(json_body={
                "page_id": 1, "pk": None, "data": data or {}
                })
        view = self._makeTarget(request)
        return view.create()["pk"]

    def test_update(self):
        session = self._getSession()
        pk = self._create_widget(session, page_id=1, data={})
        new_page = self._makePage(id=3)
        session.flush()
        request = self._makeRequest(json_body={
                "page_id": 1, "pk": pk, 
                "data": {"height": 200, "width": 200, "source_page_id": new_page.id}
                })
        view = self._makeTarget(request)
        expexted = {"page_id": 1,
                    "pk": pk,
                    "data": {"height": 200,
                             "width": 200, 
                             "source_page_id": new_page.id}}
        self.assertEquals(view.update(), expexted)

        updated = ReuseWidget.query.one()
        self.assertEquals(ReuseWidget.query.count(), 1)
        self.assertEquals(updated.page.id, 1)

    def test_delete(self):
        session = self._getSession()
        sub_page = self._makePage(id=2)
        pk = self._create_widget(session, page_id=1, data={"source_page_id": 2})

        request = self._makeRequest(json_body={"pk": pk})
        view = self._makeTarget(request)
        expexted = {"status": "ok"}
        self.assertEquals(view.delete(), expexted)

        self.assertEquals(ReuseWidget.query.count(), 0)

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
        self.assertTrue(sorted(view.dialog().keys()), 
                       sorted(["form"]))

if __name__ == "__main__":
    unittest.main()
