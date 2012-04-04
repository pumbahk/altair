# -*- coding:utf-8 -*- 

import unittest
from altaircms.plugins.widget.flash.models import FlashWidget

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

    def _makeAsset(self, id=None):
        from altaircms.asset.models import FlashAsset
        return FlashAsset.from_dict({"id": id, "filepath": "test.jpg"})

    def _getSession(self):
        from altaircms.models import DBSession
        return DBSession

    def _with_session(self, session, *args):
        for e in args:
            session.add(e)
        session.flush()
        return session

    def _prepare(self, session, page_id=None, widget_id=None, asset_id=None):
        self._with_session(session, 
            self._makeAsset(id=asset_id), self._makePage(id=page_id))

        request = self._makeRequest(json_body={
                "page_id": page_id, "pk": widget_id, "data": {"asset_id": asset_id}
                })
        return request

    def _makeRequest(self, **kwargs):
        from pyramid.testing import DummyRequest
        request = DummyRequest()
        for k, v in kwargs.iteritems():
            setattr(request, k, v)
        return request
        
class FlashWidgetViewTests(WidgetTestSourceMixn, 
                          unittest.TestCase):
    def setUp(self):
        self.config = config

    def tearDown(self):
        import transaction
        transaction.abort()

    def _makeTarget(self, request):
        from altaircms.plugins.widget.flash.views import FlashWidgetView
        from altaircms.plugins.widget.flash.models import FlashWidgetResource
        request.context = FlashWidgetResource(request)
        return FlashWidgetView(request)

    def test_create(self):
        """ test creating FlashWidget.
        check:
          1. Flash Widget is created,  successfully.
          2. flash Widget and Page object is bounded
        """
        session = self._getSession()
        request = self._prepare(session, page_id=1, asset_id=2)
        view = self._makeTarget(request)
        expexted = {"page_id": 1,
                    "asset_id":2,
                    "pk": 1,
                    "data": {"asset_id": 2}}
        self.assertEquals(view.create(), expexted)

        created = FlashWidget.query.one()
        self.assertEquals(FlashWidget.query.count(), 1)
        self.assertEquals(created.page.id, 1)
        self.assertEquals(created.asset.id, 2)

    def _create_widget(self, session, page_id=1, asset_id=2, widget_id=None):
        request = self._prepare(session,
                                widget_id=widget_id, 
                                page_id=page_id,
                                asset_id=asset_id)
        view = self._makeTarget(request)
        return view.create()["pk"]
        
    def test_update(self):
        session = self._getSession()
        pk = self._create_widget(session, page_id=1, asset_id=2)
        asset_id = 10
        self._with_session(session, self._makeAsset(asset_id))

        request = self._makeRequest(json_body={
                "page_id": 1, "pk": pk, "data": {"asset_id": 10}
                })
        view = self._makeTarget(request)
        view.update()
        expexted = {"page_id": 1,
                    "asset_id":10,
                    "pk": pk,
                    "data": {"asset_id": 10}}

        self.assertEquals(view.update(), expexted)

        updated = FlashWidget.query.one()
        self.assertEquals(FlashWidget.query.count(), 1)
        self.assertEquals(updated.page.id, 1)
        self.assertEquals(updated.asset.id, 10)

    def test_delete(self):
        session = self._getSession()
        pk = self._create_widget(session, page_id=1, asset_id=2)
        asset_id = 10
        self._with_session(session, self._makeAsset(asset_id))

        request = self._makeRequest(json_body={"pk": pk})
        view = self._makeTarget(request)
        expexted = {"status": "ok"}
        self.assertEquals(view.delete(), expexted)

        self.assertEquals(FlashWidget.query.count(), 0)

        from altaircms.page.models import Page
        self.assertNotEquals(Page.query.count(), 0)

    def test_getdialog(self):
        """ add asset env,  then dialog.mako is rendered successfully or not
        (this test is not checking about html format)
        """
        session = self._getSession()
        self._with_session(session, 
            self._makeAsset(id=1), self._makePage(id=1))

        request = self._makeRequest(GET={"page_id": 1})
        view = self._makeTarget(request)
        self.assertTrue("assets" in view.dialog())

if __name__ == "__main__":
    unittest.main()
