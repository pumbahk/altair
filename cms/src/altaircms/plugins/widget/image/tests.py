import unittest

def setUpModule():
    from altaircms.testutils import create_db
    create_db(message="image widget test")

def tearDownModule():
    from altaircms.testutils import dropall_db
    dropall_db()

class FunctionalTests(unittest.TestCase):
    def setUp(self):
        from altaircms import main_app
        app = main_app({}, {"sqlalchemy.url": "sqlite://", 
                            "plugin.static_directory": "altaircms:plugins/static", 
                            "widget.template_path_format": "%s.mako", 
                            "widget.layout_directories": "."})
        from webtest import TestApp
        self.testapp = TestApp(app)

    def tearDown(self):
        import transaction
        transaction.abort()

    def _makeAsset(self, id=None):
        from altaircms.asset.models import ImageAsset
        return ImageAsset()
    
    def _getSession(self):
        from altaircms.models import DBSession
        return DBSession

    def test_create(self):
        session = self._getSession()
        asset = self._makeAsset()
        session.add(asset)
        import transaction
        transaction.commit()
        self.testapp.post_json('/api/widget/image/create',
                          {"pk": None, "data": {"asset_id": 1}})


if __name__ == "__main__":
    unittest.main()
