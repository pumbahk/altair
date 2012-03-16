# -*- coding:utf-8 -*-
import unittest
import json
from altaircms.plugins.widget.topic.models import TopicWidget

class FunctionalViewTests(unittest.TestCase):
    create_widget = "/api/widget/topic/create"
    update_widget = "/api/widget/topic/update"
    delete_widget = "/api/widget/topic/delete"
    get_dialog = "/api/widget/topic/dialog"
    
    def setUp(self):
        self._getSession().remove()
        from altaircms import main_app
        self.app = main_app({}, {"sqlalchemy.url": "sqlite://", 
                            "plugin.static_directory": "altaircms:plugins/static", 
                            "altaircms.debug.strip_security": "true",
                            "widget.template_path_format": "%s.mako", 
                            "widget.layout_directories": "."})
        from webtest import TestApp
        self.testapp = TestApp(self.app)

    def tearDown(self):
        self._getSession().remove()
        from altaircms.testutils import dropall_db
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
        """ test creating TopicWidget.
        check:
          1. Topic Widget is created,  successfully.
          2. topic Widget and Page object is bounded
        """
        session = self._getSession()
        page_id = 1
        self._with_session(session, self._makePage(id=page_id))
        data = {"kind": u"その他", 
                "display_count": 5, 
                "display_global": True, 
                "display_event": True, 
                "display_page": True}
        res = self._callFUT().post_json(
            self.create_widget, 
            {"page_id": page_id, "pk": None, "data": data }, 
            status=200)
        expexted = {u'data': {u'display_count': 5,
                              u'display_event': True,
                              u'display_global': True,
                              u'display_page': True,
                              u'kind': u'その他'},
                    u'page_id': 1,
                    u'pk': 1}
        self.assertEquals(json.loads(res.body), expexted)
        self.assertEquals(TopicWidget.query.count(), 1)
        self.assertEquals(TopicWidget.query.first().page.id, page_id)


    def _create_widget(self, session, page_id=1, id=1):
        dummy = {"kind": u"その他", 
                 "display_count": 5, 
                 "display_global": True, 
                 "display_event": True, 
                 "display_page": True}
        self._with_session(session, self._makePage(id=page_id))
        self._callFUT().post_json(self.create_widget,
                                  {"page_id": page_id, "pk": None, "data": dummy }, 
                                  status=200)        

    def test_update(self):
        session = self._getSession()
        page_id = 10
        self._create_widget(session, id=1, page_id=page_id)
        updated = {"kind": u"その他", 
                 "display_count": 3, 
                 "display_global": True, 
                 "display_event": True, 
                 "display_page": True}
        res = self._callFUT().post_json(
            self.update_widget, 
            {"page_id": page_id, "pk":1, "data": updated }, 
            status=200)

        expexted = {u'data': {u'display_count': 3,
                              u'display_event': True,
                              u'display_global': True,
                              u'display_page': True,
                              u'kind': u'その他'},
                    u'page_id': 10,
                    u'pk': 1}
        self.assertEquals(json.loads(res.body), expexted)
        self.assertEquals(TopicWidget.query.count(), 1)
        self.assertEquals(TopicWidget.query.first().display_count, int(updated["display_count"]))


    def test_delete(self):
        session = self._getSession()
        self._create_widget(session, id=1)

        res = self._callFUT().post_json(self.delete_widget,{"pk":1},  status=200)
        self.assertEquals(json.loads(res.body), {"status": "ok"})
        self.assertEquals(TopicWidget.query.count(), 0)    

        from altaircms.page.models import Page
        self.assertNotEquals(Page.query.count(), 0)


    def test_getdialog(self):
        self._callFUT().get(self.get_dialog, status=200)

if __name__ == "__main__":
    unittest.main()
