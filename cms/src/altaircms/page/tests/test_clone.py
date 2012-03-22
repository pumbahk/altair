# -*- coding:utf-8 -*-
import unittest
import datetime
import os.path
import json

def setUpModule():
    from altaircms.models import DBSession
    DBSession.remove()

def tearDownModule():
    from altaircms.lib.testutils import dropall_db
    dropall_db(message="test view drop")

class UseAssetMixin(object):
    def _getImageAsset(self):
        from altaircms.asset.models import ImageAsset
        D = {'filepath': u'/static/img/samples/Abstract_Desktop_290.jpg',
             'id': 1,
             "page_id": 2}
        return ImageAsset.from_dict(D)


class UseWidgetMixin(object):
    def _getTextWidget(self):
        from altaircms.plugins.widget.freetext.models import FreetextWidget
        D = {'id': 1, 'text': u'freetext',"page_id": 2}
        return FreetextWidget.from_dict(D)

    def _getImageWidget(self):
        from altaircms.plugins.widget.image.models import ImageWidget
        asset = self._getImageAsset()
        D = {"id": 2, "asset": asset,  "asset_id": asset.id}
        return ImageWidget.from_dict(D)


class UsePageEtcMixin(object):
    def _getPage(self, structure):
        from altaircms.page.models import Page
        D = {'created_at': datetime.datetime(2012, 2, 14, 15, 13, 26, 438062),
             'description': u'boo',
             'event_id': None,
             'id': 2,
             'keywords': u'oo',
             'layout_id': 2,
             'parent_id': None,
             'site_id': None,
             'structure': structure, 
             'title': u'fofoo',
             'updated_at': datetime.datetime(2012, 2, 14, 15, 13, 26, 438156),
             'url': u'sample_page',
             'version': None}
        return Page.from_dict(D)

    def _getLayout(self):
        from altaircms.layout.models import Layout
        D = {'blocks': u'[["content"],["footer"], ["js_prerender"], ["js_postrender"]]',
             'client_id': None,
             'created_at': datetime.datetime(2012, 2, 16, 11, 26, 55, 755523),
             'id': 2,
             'site_id': None,
             'template_filename': u'layout.mako',
             'title': u'simple',
             'updated_at': datetime.datetime(2012, 2, 16, 11, 26, 55, 755641)}
        return Layout.from_dict(D)

    
class FunctionalPageRenderingTest(UseAssetMixin, 
                                  UseWidgetMixin, 
                                  UsePageEtcMixin, 
                                  unittest.TestCase):
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
        from altaircms.page.models import Page
        from altaircms.widget.models import Widget

        session = self._getSession()
        self._addData(session)

        self.assertEquals(Page.query.count(), 1)
        self.assertEquals(Widget.query.count(), 2)
        page = Page.query.first()
        
        cloned =  page.clone(session)
        self.assertEquals(Page.query.count(), 2)
        self.assertTrue(u"コピー" in cloned.title)
        self.assertEquals(Widget.query.count(), 4)
        self.assertEquals(cloned.structure, 
                          json.dumps({"content": [{"pk": 3, "name": "freetext"}],
                                      "footer": [{"pk": 4, "name": "image"}]}))

    def _addData(self, session):
        structure = u'''
{"content": [{"pk": 1, "name": "freetext"}],
 "footer": [{"pk": 2, "name": "image"}]}
'''
        session.add(self._getPage(structure))
        session.add(self._getLayout())
        session.add(self._getTextWidget())
        session.add(self._getImageWidget())
        import transaction
        transaction.commit()

    def _getSession(self):
        from altaircms.models import DBSession
        return DBSession

if __name__ == "__main__":
    unittest.main()
