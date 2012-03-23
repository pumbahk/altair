# -*- coding:utf-8 -*-

import unittest
import json
from altaircms.plugins.widget.detail.models import DetailWidget

"""
todo:kindが不正な値などの異常系のテストまだ入っていない。
"""
class FunctionalViewTests(unittest.TestCase):
    create_widget = "/api/widget/detail/create"
    update_widget = "/api/widget/detail/update"
    delete_widget = "/api/widget/detail/delete"
    get_dialog = "/api/widget/detail/dialog"
    
    def setUp(self):
        self._getSession().remove()
        from altaircms import main
        self.app = main({}, **{"sqlalchemy.url": "sqlite://", 
                            "altaircms.plugin_static_directory": "altaircms:plugins/static", 
                            "altaircms.debug.strip_security": "true",
                            "widget.template_path_format": "%s.mako", 
                            "altaircms.layout_directory": "."})
        from altaircms.lib.testutils import create_db
        create_db()
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
        """ test creating DetailWidget.
        check:
          1. Detail Widget is created,  successfully.
          2. detail Widget and Page object is bounded
        """
        session = self._getSession()
        page_id = 1
        kind = "description"
        self._with_session(session, self._makePage(id=page_id))

        res = self._callFUT().post_json(
            self.create_widget, 
            {"page_id": page_id, "pk": None, "data": {"kind": kind} }, 
            status=200)
        expexted = {"page_id": page_id, "pk": 1,  "data": {"kind": kind} }

        self.assertEquals(json.loads(res.body), expexted)
        self.assertEquals(DetailWidget.query.count(), 1)
        self.assertEquals(DetailWidget.query.first().page.id, page_id)


    def _create_widget(self, session, page_id=1, id=1):
        session = self._getSession()
        page_id = 1
        dummy = "dummy"
        self._with_session(session, self._makePage(id=page_id))
        self._callFUT().post_json(self.create_widget,
                                  {"page_id": page_id, "pk": None, "data": {"kind": dummy} }, 
                                  status=200)        

    def test_update(self):
        session = self._getSession()
        page_id = 10
        self._create_widget(session, id=1, page_id=page_id)
        updated = "description"
        res = self._callFUT().post_json(self.update_widget, 
                                        {"page_id": page_id, "pk":1, "data": {"kind": updated} }, 
                                        status=200)
        expexted = {"page_id": page_id, "pk": 1,  "data": {"kind": updated} }

        self.assertEquals(json.loads(res.body), expexted)
        self.assertEquals(DetailWidget.query.count(), 1)
        self.assertEquals(DetailWidget.query.first().kind, updated)


    def test_delete(self):
        session = self._getSession()
        self._create_widget(session, id=1)

        res = self._callFUT().post_json(self.delete_widget,{"pk":1},  status=200)
        self.assertEquals(json.loads(res.body), {"status": "ok"})
        self.assertEquals(DetailWidget.query.count(), 0)    

        from altaircms.page.models import Page
        self.assertNotEquals(Page.query.count(), 0)


    def test_getdialog(self):
        self._callFUT().get(self.get_dialog, status=200)

if __name__ == "__main__":
    unittest.main()
