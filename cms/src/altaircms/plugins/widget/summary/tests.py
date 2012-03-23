# -*- coding:utf-8 -*-

import unittest
import json
from altaircms.plugins.widget.summary.models import SummaryWidget
import mock

class FunctionalViewTests(unittest.TestCase):
    create_widget = "/api/widget/summary/create"
    update_widget = "/api/widget/summary/update"
    delete_widget = "/api/widget/summary/delete"
    get_dialog = "/api/widget/summary/dialog"
    
    def setUp(self):
        self._getSession().remove()
        from altaircms import main
        self.app = main({}, **{"sqlalchemy.url": "sqlite://", 
                            "altaircms.plugin_static_directory": "altaircms:plugins/static", 
                            "altaircms.debug.strip_security": "true",
                            "widget.template_path_format": "%s.mako", 
                            "altaircms.layout_directory": "."})
        from webtest import TestApp
        self.testapp = TestApp(self.app)

    def tearDown(self):
        self._getSession().remove()
        from altaircms.lib.testutils import dropall_db
        dropall_db()
        del self.app

    def _makePage(self, id=None):
        from altaircms.page.models import Page
        return Page.from_dict({"id": id})
    
    def _getSession(self):
        from altaircms.models import DBSession
        return DBSession

    def _callFUT(self):
        import transaction
        transaction.commit()
        return self.testapp

    def _with_session(self, session, *args):
        for e in args:
            session.add(e)
        session.flush()
        return session

    def test_create(self):
        """ test creating SummaryWidget.
        check:
          1. Summary Widget is created,  successfully.
          2. summary Widget and Page object is bounded
        """
        session = self._getSession()
        page_id = 1

        self._with_session(session, self._makePage(id=page_id))
        items = json.dumps([
            {"label": u"講演期間", 
             "content": u"2012年06月03日(日) 〜 07月16日(月) (講演カレンダーを見る)",
             "attr":"class='performance_period'"}, 
            {"label": u"説明／注意事項",
             "content": u"※未就学児童のご入場はお断りいたします。",
             "attr":"class='notice'"}])

        res = self._callFUT().post_json(
            self.create_widget, 
            {"page_id": page_id, "pk": None, "data": {"items": items} }, 
            status=200)
        expexted = {"page_id": page_id, "pk": 1,  "data": {"items": items} }

        self.assertEquals(json.loads(res.body), expexted)
        self.assertEquals(SummaryWidget.query.count(), 1)
        self.assertEquals(SummaryWidget.query.first().page.id, page_id)


    def _create_widget(self, session, page_id=1, id=1):
        session = self._getSession()
        page_id = 1
        dummy = "[]"
        self._with_session(session, self._makePage(id=page_id))
        self._callFUT().post_json(self.create_widget,
                                  {"page_id": page_id, "pk": None, "data": {"items": dummy} }, 
                                  status=200)        

    def test_update(self):
        session = self._getSession()
        page_id = 10
        self._create_widget(session, id=1, page_id=page_id)
        updated = "[{'label': 'foo',  'content': 'content', 'attr':''}]"
        res = self._callFUT().post_json(self.update_widget, 
                                        {"page_id": page_id, "pk":1, "data": {"items": updated} }, 
                                        status=200)
        expexted = {"page_id": page_id, "pk": 1,  "data": {"items": updated} }

        self.assertEquals(json.loads(res.body), expexted)
        self.assertEquals(SummaryWidget.query.count(), 1)
        self.assertEquals(SummaryWidget.query.first().items, updated)


    def test_delete(self):
        session = self._getSession()
        self._create_widget(session, id=1)

        res = self._callFUT().post_json(self.delete_widget,{"pk":1},  status=200)
        self.assertEquals(json.loads(res.body), {"status": "ok"})
        self.assertEquals(SummaryWidget.query.count(), 0)    

        from altaircms.page.models import Page
        self.assertNotEquals(Page.query.count(), 0)

    item_json=u"""
       [{label: "講演期間", content: u"2012年06月03日(日) 〜 07月16日(月) (講演カレンダーを見る)"}, 
        {label: "説明／注意事項", content: u"※未就学児童のご入場はお断りいたします。"}]
"""
    @mock.patch("altaircms.plugins.widget.summary.models.SummaryWidgetResource.get_items", return_value=item_json)
    def test_getdialog(self, mocked):
        self._callFUT().get(self.get_dialog, {"page": None}, status=200)

if __name__ == "__main__":
    unittest.main()
