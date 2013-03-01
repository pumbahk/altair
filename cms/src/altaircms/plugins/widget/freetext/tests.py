# -*- coding:utf-8 -*- 

import unittest
from altaircms.plugins.widget.freetext.models import FreetextWidget

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
        
class FreetextWidgetViewTests(WidgetTestSourceMixn, 
                          unittest.TestCase):
    def setUp(self):
        self.config = config

    def tearDown(self):
        import transaction
        transaction.abort()

    def _makeTarget(self, request):
        from altaircms.plugins.widget.freetext.views import FreetextWidgetView
        from altaircms.plugins.widget.freetext.models import FreetextWidgetResource
        request.context = FreetextWidgetResource(request)
        return FreetextWidgetView(request)

    def test_create(self):
        """ test creating FreetextWidget.
        check:
          1. Freetext Widget is created,  successfully.
          2. Freetext Widget and Page object is bounded
        """
        session = self._getSession()

        self._with_session(session, self._makePage(id=1))
        request = self._makeRequest(json_body={
                "page_id": 1, "pk": None, "data": {"freetext": u"<h1>title</h1>"}
                })
        view = self._makeTarget(request)
        expexted = {"page_id": 1,
                    "pk": 1,
                    "data": {"freetext": u"<h1>title</h1>"}}
        self.assertEquals(view.create(), expexted)

        created = FreetextWidget.query.one()
        self.assertEquals(FreetextWidget.query.count(), 1)
        self.assertEquals(created.page.id, 1)
        self.assertEquals(created.text, u"<h1>title</h1>")

    def _create_widget(self, session, page_id=1, freetext=None):
        self._with_session(session, self._makePage(id=1))
        request = self._makeRequest(json_body={
                "page_id": 1, "pk": None, "data": {"freetext": freetext}
                })
        view = self._makeTarget(request)
        return view.create()["pk"]

    def test_update(self):
        session = self._getSession()
        pk = self._create_widget(session, page_id=1, freetext=u"dummy")
        freetext = u"updated"
        request = self._makeRequest(json_body={
                "page_id": 1, "pk": pk, "data": {"freetext": freetext}
                })
        view = self._makeTarget(request)
        expexted = {"page_id": 1,
                    "pk": pk,
                    "data": {"freetext": freetext}}
        self.assertEquals(view.update(), expexted)

        updated = FreetextWidget.query.one()
        self.assertEquals(FreetextWidget.query.count(), 1)
        self.assertEquals(updated.page.id, 1)

    def test_delete(self):
        session = self._getSession()
        pk = self._create_widget(session, page_id=1, freetext=u"dummy")

        request = self._makeRequest(json_body={"pk": pk})
        view = self._makeTarget(request)
        expexted = {"status": "ok"}
        self.assertEquals(view.delete(), expexted)

        self.assertEquals(FreetextWidget.query.count(), 0)

        from altaircms.page.models import Page
        self.assertNotEquals(Page.query.count(), 0)

    def test_getdialog(self):
        """ add asset env,  then dialog.html is rendered successfully or not
        (this test is not checking about html format)
        """
        session = self._getSession()
        self._with_session(session, self._makePage(id=1))

        request = self._makeRequest(GET={"page_id": 1})
        view = self._makeTarget(request)
        self.assertTrue("widget" in view.dialog())

if __name__ == "__main__":
    unittest.main()

