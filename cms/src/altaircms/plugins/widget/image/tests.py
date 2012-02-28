import unittest
import json
from altaircms.plugins.widget.image.models import ImageWidget

class FunctionalViewTests(unittest.TestCase):
    create_widget = "/api/widget/image/create"
    update_widget = "/api/widget/image/update"
    delete_widget = "/api/widget/image/delete"
    get_dialog = "/api/widget/image/dialog"
    
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

    def _makeAsset(self, id=None):
        from altaircms.asset.models import ImageAsset
        return ImageAsset.from_dict({"id": id, "filepath": "test.jpg"})
    
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
        """ test creating ImageWidget.
        check:
          1. Image Widget is created,  successfully.
          2. image Widget and Page object is bounded
        """
        session = self._getSession()
        page_id = 1
        self._with_session(session, 
            self._makeAsset(id=1), self._makePage(id=page_id))

        res = self._callFUT().post_json(
            self.create_widget, 
            {"page_id": page_id, "pk": None, "data": {"asset_id": 1}}, 
            status=200)
        expexted = {"page_id": page_id,  "asset_id": 1, 
                    "pk": 1,  "data": {"asset_id": 1}}

        self.assertEquals(json.loads(res.body), expexted)
        self.assertEquals(ImageWidget.query.count(), 1)
        self.assertEquals(ImageWidget.query.first().page.id, page_id)

    def _create_widget(self, session, page_id=1, id=1):
        session = self._getSession()
        page_id = 1
        self._with_session(session, 
            self._makeAsset(id=1), self._makePage(id=page_id))
        self._callFUT().post_json(self.create_widget,
                                  {"page_id": page_id, "pk": None, "data": {"asset_id": 1}}, 
                                  status=200)        
        
    def test_update(self):
        session = self._getSession()
        page_id = 10
        self._create_widget(session, id=1, page_id=page_id)

        another_asset = self._makeAsset(id=2)
        session.add(another_asset)
        
        res = self._callFUT().post_json(self.update_widget, 
                                        {"page_id": page_id, "pk":1, "data": {"asset_id": 2}}, 
                                        status=200)
        expexted = {"asset_id": 2,  "page_id": page_id,  
                    "pk": 1,  "data": {"asset_id": 2}}

        self.assertEquals(json.loads(res.body), expexted)
        self.assertEquals(ImageWidget.query.count(), 1)
        self.assertEquals(ImageWidget.query.first().asset.id, 2)

    def test_delete(self):
        session = self._getSession()
        self._create_widget(session, id=1)

        res = self._callFUT().post_json(self.delete_widget,{"pk":1},  status=200)
        self.assertEquals(json.loads(res.body), {"status": "ok"})
        self.assertEquals(ImageWidget.query.count(), 0)    

    def test_getdialog(self):
        """ add asset env,  then dialog.mako is rendered successfully or not
        (this test is not checking about html format)
        """
        session = self._getSession()
        session.add(self._makeAsset(id=1))
        self._callFUT().get(self.get_dialog, status=200)


if __name__ == "__main__":
    unittest.main()
