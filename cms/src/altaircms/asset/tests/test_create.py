import unittest

class FunctionalViewTests(unittest.TestCase):
    def setUp(self):
        self._getSession().remove()
        from altaircms import main_with_strip_secret
        settings = {"sqlalchemy.url": "sqlite://", 
                    "altaircms.plugin_static_directory": "altaircms:plugins/static", 
                    "altaircms.asset.storepath": " %(here)s/data/assets"
                    }
        self.app = main_app_with_strip_secret({}, settings)
        from webtest import TestApp
        self.testapp = TestApp(self.app)

    def tearDown(self):
        self._getSession().remove()
        from altaircms.lib.testutils import dropall_db
        dropall_db()
        del self.app
    
    def _getSession(self):
        from altaircms.models import DBSession
        return DBSession

    def _callFUT(self):
        import transaction
        transaction.commit()
        return self.testapp

    # def test_create_image_asset(self):
        
    #     res = self._callFUT().get("/asset/form/image")
    #     form =  res.form
    #     import pprint
    #     pprint.pprint([(k, v, v[0].value) for k, v in form.fields.items()])
        # form[u"upload"] = [u"test.jpg"]
        # form[u"_charset_"] = u'UTF-8'
        # form.submit("submit")

    # def _create_url(self, session, id=1):
    #     asset = self._makeAsset(id=1)
    #     session.add(asset)
    #     self._callFUT().post_json(self.create_url,
    #                               {"pk": None, "data": {"asset_id": 1}})
        
    # def test_update(self):
    #     session = self._getSession()
    #     self._create_url(session, id=1)

    #     another_asset = self._makeAsset(id=2)
    #     session.add(another_asset)
        
    #     res = self._callFUT().post_json(self.update_url, 
    #                                     {"pk":1, "data": {"asset_id": 2}}, 
    #                                     status=200)
    #     expexted = {"asset_id": 2,  "pk": 1,  "data": {"asset_id": 2}}
    #     self.assertEquals(json.loads(res.body), expexted)

    # def test_delete(self):
    #     session = self._getSession()
    #     self._create_url(session, id=1)

    #     res = self._callFUT().post_json(self.delete_url,{"pk":1},  status=200)
    #     self.assertEquals(json.loads(res.body), {"status": "ok"})

    
    # def test_getdialog(self):
    #     self._callFUT().get(self.get_dialog, status=200)

if __name__ == "__main__":
    unittest.main()
