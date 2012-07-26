# -*- coding:utf-8 -*- 

import unittest
from altaircms.plugins.widget.topic.models import TopicWidget

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
        
class TopicWidgetViewTests(WidgetTestSourceMixn, 
                          unittest.TestCase):
    def setUp(self):
        self.config = config

    def tearDown(self):
        import transaction
        transaction.abort()

    def _makeTarget(self, request):
        from altaircms.plugins.widget.topic.views import TopicWidgetView
        from altaircms.plugins.widget.topic.models import TopicWidgetResource
        request.context = TopicWidgetResource(request)
        return TopicWidgetView(request)

    def test_create(self):
        """ test creating TopicWidget.
        check:
          1. Topic Widget is created,  successfully.
          2. Topic Widget and Page object is bounded
        """
        session = self._getSession()

        self._with_session(session, self._makePage(id=1))
        data = {"kind": u"その他", 
                "topic_type": "topic", 
                "display_count": 5, 
                "display_global": True, 
                "display_event": True, 
                "display_page": True}
        request = self._makeRequest(json_body={
                "page_id": 1, "pk": None, "data": data
                })
        view = self._makeTarget(request)
        expexted = {"page_id": 1,
                    "pk": 1,
                    "data": data}
        self.assertEquals(view.create(), expexted)

        created = TopicWidget.query.one()
        self.assertEquals(TopicWidget.query.count(), 1)
        self.assertEquals(created.page.id, 1)
        self.assertEquals(created.kind, u"その他")
        self.assertEquals(created.topic_type, u"topic")
        self.assertEquals(created.display_count, 5)
        self.assertEquals(created.display_event, True)


    def _create_widget(self, session, page_id=1, data=None):
        self._with_session(session, self._makePage(id=1))
        request = self._makeRequest(json_body={
                "page_id": 1, "pk": None, "data": data or {}
                })
        view = self._makeTarget(request)
        return view.create()["pk"]

    def test_update(self):
        session = self._getSession()
        dummy = {"kind": u"その他", 
                 "display_count": 5, 
                 "display_global": True, 
                 "display_event": True, 
                 "display_page": True}
        pk = self._create_widget(session, page_id=1, data=dummy)
        data = {"kind": u"その他", 
                 "display_count": 3, 
                 "display_global": False, 
                 "display_event": True, 
                 "display_page": True}
        request = self._makeRequest(json_body={
                "page_id": 1, "pk": pk, "data": data
                })
        view = self._makeTarget(request)
        expexted = {"page_id": 1,
                    "pk": pk,
                    "data": data }
        self.assertEquals(view.update(), expexted)

        updated = TopicWidget.query.one()
        self.assertEquals(TopicWidget.query.count(), 1)
        self.assertEquals(updated.page.id, 1)
        self.assertEquals(updated.display_count, 3)
        self.assertEquals(updated.display_global, False)

    def test_delete(self):
        session = self._getSession()
        pk = self._create_widget(session, page_id=1, data={})

        request = self._makeRequest(json_body={"pk": pk})
        view = self._makeTarget(request)
        expexted = {"status": "ok"}
        self.assertEquals(view.delete(), expexted)

        self.assertEquals(TopicWidget.query.count(), 0)

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
        self.assertTrue("form" in view.dialog())

if __name__ == "__main__":
    unittest.main()
