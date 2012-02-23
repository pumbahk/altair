import unittest
import json

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

    def _makeAsset(self, id=None):
        from altaircms.asset.models import ImageAsset
        return ImageAsset.from_dict({"id": id})
    
    def _getSession(self):
        from altaircms.models import DBSession
        return DBSession

    def _callFUT(self):
        import transaction
        transaction.commit()
        return self.testapp

    def test_create(self):
        session = self._getSession()
        asset = self._makeAsset(id=1)
        session.add(asset)
        res = self._callFUT().post_json(
            self.create_widget, 
            {"pk": None, "data": {"asset_id": 1}}, 
            status=200)
        expexted = {"asset_id": 1,  "pk": 1,  "data": {"asset_id": 1}}
        self.assertEquals(json.loads(res.body), expexted)

    def _create_widget(self, session, id=1):
        asset = self._makeAsset(id=1)
        session.add(asset)
        self._callFUT().post_json(self.create_widget,
                                  {"pk": None, "data": {"asset_id": 1}})
        
    def test_update(self):
        session = self._getSession()
        self._create_widget(session, id=1)

        another_asset = self._makeAsset(id=2)
        session.add(another_asset)
        
        res = self._callFUT().post_json(self.update_widget, 
                                        {"pk":1, "data": {"asset_id": 2}}, 
                                        status=200)
        expexted = {"asset_id": 2,  "pk": 1,  "data": {"asset_id": 2}}
        self.assertEquals(json.loads(res.body), expexted)

    def test_delete(self):
        session = self._getSession()
        self._create_widget(session, id=1)

        res = self._callFUT().post_json(self.delete_widget,{"pk":1},  status=200)
        self.assertEquals(json.loads(res.body), {"status": "ok"})

    
    def test_getdialog(self):
        self._callFUT().get(self.get_dialog, status=200)

if __name__ == "__main__":
    unittest.main()
