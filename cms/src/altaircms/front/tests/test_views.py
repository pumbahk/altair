import unittest
import datetime
import os.path

"""
Page -> Layout
Page.structure{} # widget id
Widget
"""

def setUpModule():
    from altaircms.testutils import create_db
    from altaircms.models import DBSession
    DBSession.remove()
    create_db(message="test view create")

def tearDownModule():
    from altaircms.testutils import dropall_db
    dropall_db(message="test view drop")

class FunctionalPageRenderingTest(unittest.TestCase):
    DIR = os.path.dirname(os.path.abspath(__file__))
    def setUp(self):
        from altaircms import main_app
        app = main_app({}, {"sqlalchemy.url": "sqlite://", 
                            "mako.directories": os.path.join(self.DIR, "templates"), 
                            "plugin.static_directory": "altaircms:plugins/static", 
                            "widget.layout_directories": "."})
        from webtest import TestApp
        self.testapp = TestApp(app)

    def tearDown(self):
        import transaction
        transaction.abort()
        self._getSession().remove()
        
    def test_it(self):
        session = self._getSession()
        self._addData(session)

        result = self.testapp.get("/f/publish/sample_page", status=200)
        import re
        self.assertEqual(re.sub("\s", "", result.text), "text:1image:2")

    def test_it_nodata(self):
        self.testapp.get("/f/publish/sample_page", status=404)

    def _addData(self, session):
        session.add(self._getPage())
        session.add(self._getLayout())
        session.add(self._getTextWidget())
        session.add(self._getImageWidget())
        ## why use transaction commit?
        import transaction
        transaction.commit()

    def _getSession(self):
        from altaircms.models import DBSession
        return DBSession

    def _getPage(self):
        from altaircms.page.models import Page
        D = {'created_at': datetime.datetime(2012, 2, 14, 15, 13, 26, 438062),
             'description': u'boo',
             'event_id': None,
             'id': 2,
             'keyword': u'oo',
             'layout_id': 2,
             'parent_id': None,
             'site_id': None,
             'structure': u'{"content": [{"pk": 1, "name": "freetext"}], "footer": [{"pk": 2, "name": "image"}]}',
             'title': u'fofoo',
             'updated_at': datetime.datetime(2012, 2, 14, 15, 13, 26, 438156),
             'url': u'sample_page',
             'version': None}
        return Page.from_dict(D)

    def _getLayout(self):
        from altaircms.layout.models import Layout
        D = {'blocks': u'[["content"],["footer"]]',
             'client_id': None,
             'created_at': datetime.datetime(2012, 2, 16, 11, 26, 55, 755523),
             'id': 2,
             'site_id': None,
             'template_filename': u'layout.mako',
             'title': u'simple',
             'updated_at': datetime.datetime(2012, 2, 16, 11, 26, 55, 755641)}
        return Layout.from_dict(D)

    def _getImageAsset(self):
        from altaircms.asset.models import ImageAsset
        D = {'filepath': u'/static/img/samples/Abstract_Desktop_290.jpg',
             'id': 1,
             "page_id": 2, 
             'type': u'image_asset'}
        return ImageAsset.from_dict(D)

    def _getTextWidget(self):
        from altaircms.plugins.widget.freetext.models import FreetextWidget
        D = {'id': 1, 'text': u'hohoho',"page_id": 2}
        return FreetextWidget.from_dict(D)

    def _getImageWidget(self):
        from altaircms.plugins.widget.image.models import ImageWidget
        asset = self._getImageAsset()
        D = {"assest": asset,  "asset_id": asset.id, "id": 2}
        return ImageWidget.from_dict(D)

if __name__ == "__main__":
    unittest.main()
