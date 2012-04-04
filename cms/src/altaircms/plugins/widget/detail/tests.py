# -*- coding:utf-8 -*- 

import unittest
from altaircms.plugins.widget.detail.models import DetailWidget

config  = None
def setUpModule():
    global config
    from altaircms.lib import testutils
    testutils.create_db(force=False)
    config = testutils.config()

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
        
class DetailWidgetViewTests(WidgetTestSourceMixn, 
                          unittest.TestCase):
    def setUp(self):
        self.config = config

    def tearDown(self):
        import transaction
        transaction.abort()

    def _makeTarget(self, request):
        from altaircms.plugins.widget.detail.views import DetailWidgetView
        from altaircms.plugins.widget.detail.models import DetailWidgetResource
        request.context = DetailWidgetResource(request)
        return DetailWidgetView(request)

    def test_create(self):
        """ test creating DetailWidget.
        check:
          1. Detail Widget is created,  successfully.
          2. Detail Widget and Page object is bounded
        """
        session = self._getSession()

        self._with_session(session, self._makePage(id=1))
        request = self._makeRequest(json_body={
                "page_id": 1, "pk": None, "data": {"kind": "description"}
                })
        view = self._makeTarget(request)
        expexted = {"page_id": 1,
                    "pk": 1,
                    "data": {"kind": "description"}}
        self.assertEquals(view.create(), expexted)

        created = DetailWidget.query.one()
        self.assertEquals(DetailWidget.query.count(), 1)
        self.assertEquals(created.page.id, 1)
        self.assertEquals(created.kind, "description")

    def _create_widget(self, session, page_id=1, data=None):
        self._with_session(session, self._makePage(id=1))
        request = self._makeRequest(json_body={
                "page_id": 1, "pk": None, "data": data or {}
                })
        view = self._makeTarget(request)
        return view.create()["pk"]

    # def test_update(self):
    #     session = self._getSession()
    #     pk = self._create_widget(session, page_id=1, data={})
    #     request = self._makeRequest(json_body={
    #             "page_id": 1, "pk": pk, "data": {}
    #             })
    #     view = self._makeTarget(request)
    #     expexted = {"page_id": 1,
    #                 "pk": pk,
    #                 "data": {} }
    #     self.assertEquals(view.update(), expexted)

    #     updated = DetailWidget.query.one()
    #     self.assertEquals(DetailWidget.query.count(), 1)
    #     self.assertEquals(updated.page.id, 1)

    def test_delete(self):
        session = self._getSession()
        pk = self._create_widget(session, page_id=1, data={"kind": "description"})

        request = self._makeRequest(json_body={"pk": pk})
        view = self._makeTarget(request)
        expexted = {"status": "ok"}
        self.assertEquals(view.delete(), expexted)

        self.assertEquals(DetailWidget.query.count(), 0)

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
        self.assertEquals(sorted(view.dialog().keys()), 
                          sorted(["form_class", "form"]), )


if __name__ == "__main__":
    unittest.main()
