# -*- coding:utf-8 -*- 

import unittest
from altaircms.plugins.widget.menu.models import MenuWidget

config  = None
def setUpModule():
    global config
    from altaircms.lib import testutils
    testutils.create_db(force=False)
    config = testutils.config()

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
        from altaircms.testing import DummyRequest
        request = DummyRequest()
        for k, v in kwargs.iteritems():
            setattr(request, k, v)
        return request
        
class MenuWidgetViewTests(WidgetTestSourceMixn, 
                          unittest.TestCase):
    def setUp(self):
        self.config = config

    def tearDown(self):
        import transaction
        transaction.abort()

    def _makeTarget(self, request):
        from altaircms.plugins.widget.menu.views import MenuWidgetView
        from altaircms.plugins.widget.menu.models import MenuWidgetResource
        request.context = MenuWidgetResource(request)
        return MenuWidgetView(request)

    def test_create(self):
        """ test creating MenuWidget.
        check:
          1. Menu Widget is created,  successfully.
          2. Menu Widget and Page object is bounded
        """
        session = self._getSession()

        self._with_session(session, self._makePage(id=1))
        request = self._makeRequest(json_body={
                u"page_id": 1, u"pk": None, u"data": {u"items": u"[]"}
                })
        view = self._makeTarget(request)
        expexted = {u"page_id": 1,
                    u"pk": 1,
                    u"data": {u"items": "[]"}}
        self.assertEquals(view.create(), expexted)

        created = MenuWidget.query.one()
        self.assertEquals(MenuWidget.query.count(), 1)
        self.assertEquals(created.page.id, 1)
        self.assertEquals(created.items, u"[]")

    def _create_widget(self, session, page_id=1, data=None):
        self._with_session(session, self._makePage(id=1))
        request = self._makeRequest(json_body={
                u"page_id": 1, u"pk": None, u"data": data or {}
                })
        view = self._makeTarget(request)
        return view.create()[u"pk"]

    def test_update(self):
        session = self._getSession()
        pk = self._create_widget(session, page_id=1, data={u"items": u"[]"})
        request = self._makeRequest(json_body={
                u"page_id": 1, u"pk": pk, u"data": {u"items": u'[{label:"google", link:"http://www.google.co.jp"}]'}
                })
        view = self._makeTarget(request)
        expexted = {u"page_id": 1,
                    u"pk": pk,
                    u"data": {u"items": u'[{label:"google", link:"http://www.google.co.jp"}]'} }
        self.assertEquals(view.update(), expexted)

        updated = MenuWidget.query.one()
        self.assertEquals(MenuWidget.query.count(), 1)
        self.assertEquals(updated.page.id, 1)
        self.assertEquals(updated.items, u'[{label:"google", link:"http://www.google.co.jp"}]')

    def test_delete(self):
        session = self._getSession()
        pk = self._create_widget(session, page_id=1, data={u"items": u"[]"})

        request = self._makeRequest(json_body={u"pk": pk})
        view = self._makeTarget(request)
        expexted = {"status": "ok"}
        self.assertEquals(view.delete(), expexted)

        self.assertEquals(MenuWidget.query.count(), 0)

        from altaircms.page.models import Page
        self.assertNotEquals(Page.query.count(), 0)

    def test_getdialog(self):
        """ add asset env,  then dialog.mako is rendered successfully or not
        (this test is not checking about html format)
        """
        session = self._getSession()
        self._with_session(session, self._makePage(id=1))

        request = self._makeRequest(GET={"page": 1})
        view = self._makeTarget(request)
        self.assertEquals(sorted(view.dialog().keys()), 
                         sorted(["items", "widget"]))

if __name__ == "__main__":
    unittest.main()
