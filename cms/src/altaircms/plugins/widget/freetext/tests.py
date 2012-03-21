import unittest
import json
from altaircms.plugins.widget.freetext.models import FreetextWidget

class FunctionalViewTests(unittest.TestCase):
    create_widget = "/api/widget/freetext/create"
    update_widget = "/api/widget/freetext/update"
    delete_widget = "/api/widget/freetext/delete"
    get_dialog = "/api/widget/freetext/dialog"
    
    def setUp(self):
        self._getSession().remove()
        from altaircms import main_app
        self.app = main_app({}, {"sqlalchemy.url": "sqlite://", 
                            "plugin.static_directory": "altaircms:plugins/static", 
                            "widget.template_path_format": "%s.mako", 
                            "widget.layout_directories": "."})
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
        """ test creating FreetextWidget.
        check:
          1. Freetext Widget is created,  successfully.
          2. freetext Widget and Page object is bounded
        """
        session = self._getSession()
        page_id = 1
        textdata = "foo foo foo"
        self._with_session(session, self._makePage(id=page_id))

        res = self._callFUT().post_json(
            self.create_widget, 
            {"page_id": page_id, "pk": None, "data": {"freetext": textdata}}, 
            status=200)
        expexted = {"page_id": page_id, "pk": 1,  "data": {"freetext": textdata}}

        self.assertEquals(json.loads(res.body), expexted)
        self.assertEquals(FreetextWidget.query.count(), 1)
        self.assertEquals(FreetextWidget.query.first().page.id, page_id)

    def _create_widget(self, session, page_id=1, id=1):
        session = self._getSession()
        page_id = 1
        dummy_text = "dummy"
        self._with_session(session, self._makePage(id=page_id))
        self._callFUT().post_json(self.create_widget,
                                  {"page_id": page_id, "pk": None, "data": {"freetext": dummy_text}}, 
                                  status=200)        
        
    def test_update(self):
        session = self._getSession()
        page_id = 10
        self._create_widget(session, id=1, page_id=page_id)
        update_text = "updated"
        res = self._callFUT().post_json(self.update_widget, 
                                        {"page_id": page_id, "pk":1, "data": {"freetext": update_text}}, 
                                        status=200)
        expexted = {"page_id": page_id, "pk": 1,  "data": {"freetext": update_text}}

        self.assertEquals(json.loads(res.body), expexted)
        self.assertEquals(FreetextWidget.query.count(), 1)
        self.assertEquals(FreetextWidget.query.first().text, update_text)


    def test_delete(self):
        session = self._getSession()
        self._create_widget(session, id=1)

        res = self._callFUT().post_json(self.delete_widget,{"pk":1},  status=200)
        self.assertEquals(json.loads(res.body), {"status": "ok"})
        self.assertEquals(FreetextWidget.query.count(), 0)    

        from altaircms.page.models import Page
        self.assertNotEquals(Page.query.count(), 0)


    def test_getdialog(self):
        self._callFUT().get(self.get_dialog, status=200)

if __name__ == "__main__":
    unittest.main()
