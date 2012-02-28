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
        from altaircms import main_app
        self.app = main_app({}, {"sqlalchemy.url": "sqlite://", 
                            "plugin.static_directory": "altaircms:plugins/static", 
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
        """ test creating CalendarWidget.
        check:
          1. Calendar Widget is created,  successfully.
          2. calendar Widget and Page object is bounded
        """
        pass

    def _create_widget(self, session, page_id=1, id=1):
        pass

    def test_update(self):
        pass

    def test_delete(self):
        pass

    def test_getdialog(self):
        pass

if __name__ == "__main__":
    unittest.main()
