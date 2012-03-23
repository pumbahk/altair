import unittest
import json
from altaircms.plugins.widget.calendar.models import CalendarWidget

class FunctionalViewTests(unittest.TestCase):
    create_widget = "/api/widget/calendar/create"
    update_widget = "/api/widget/calendar/update"
    delete_widget = "/api/widget/calendar/delete"
    get_dialog = "/api/widget/calendar/dialog"
    
    def setUp(self):
        self._getSession().remove()
        from altaircms import main
        self.app = main({}, **{"sqlalchemy.url": "sqlite://", 
                            "altaircms.plugin_static_directory": "altaircms:plugins/static", 
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
        """ test creating CalendarWidget.
        check:
          1. Calendar Widget is created,  successfully.
          2. calendar Widget and Page object is bounded
        """
        session = self._getSession()
        page_id = 1
        calendar_type = "this_month"
        self._with_session(session, self._makePage(id=page_id))

        res = self._callFUT().post_json(
            self.create_widget, 
            {"page_id": page_id, "pk": None, "data": {"calendar_type": calendar_type}}, 
            status=200)
        expexted = {"page_id": page_id, "pk": 1,  "data": {"calendar_type": calendar_type}}

        self.assertEquals(json.loads(res.body), expexted)
        self.assertEquals(CalendarWidget.query.count(), 1)
        self.assertEquals(CalendarWidget.query.first().page.id, page_id)


    def _create_widget(self, session, page_id=1, id=1):
        session = self._getSession()
        page_id = 1
        dummy = "dummy"
        self._with_session(session, self._makePage(id=page_id))
        self._callFUT().post_json(self.create_widget,
                                  {"page_id": page_id, "pk": None, "data": {"calendar_type": dummy}}, 
                                  status=200)        

    def test_update(self):
        session = self._getSession()
        page_id = 10
        self._create_widget(session, id=1, page_id=page_id)
        updated = "updated"
        res = self._callFUT().post_json(self.update_widget, 
                                        {"page_id": page_id, "pk":1, "data": {"calendar_type": updated}}, 
                                        status=200)
        expexted = {"page_id": page_id, "pk": 1,  "data": {"calendar_type": updated}}

        self.assertEquals(json.loads(res.body), expexted)
        self.assertEquals(CalendarWidget.query.count(), 1)
        self.assertEquals(CalendarWidget.query.first().calendar_type, updated)

    def test_update_with_term(self):
        session = self._getSession()
        page_id = 10
        self._create_widget(session, id=1, page_id=page_id)
        updated = "updated"
        res = self._callFUT().post_json(self.update_widget, 
                                        {"page_id": page_id, "pk":1,
                                         "data": {"calendar_type": updated,
                                                  "from_date": "2011-1-1",
                                                  "to_date": "2011-2-1"}}, 
                                        status=200)
        expexted = {"page_id": page_id, "pk": 1,  "data": {"calendar_type": updated,
                                                           "from_date": "2011-1-1",
                                                           "to_date": "2011-2-1"}}

        self.assertEquals(json.loads(res.body), expexted)
        self.assertEquals(CalendarWidget.query.count(), 1)
        self.assertEquals(CalendarWidget.query.first().calendar_type, updated)


    def test_delete(self):
        session = self._getSession()
        self._create_widget(session, id=1)

        res = self._callFUT().post_json(self.delete_widget,{"pk":1},  status=200)
        self.assertEquals(json.loads(res.body), {"status": "ok"})
        self.assertEquals(CalendarWidget.query.count(), 0)    

        from altaircms.page.models import Page
        self.assertNotEquals(Page.query.count(), 0)


    def test_getdialog(self):
        self._callFUT().get(self.get_dialog, status=200)


if __name__ == "__main__":
    unittest.main()
