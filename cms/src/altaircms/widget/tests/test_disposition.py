# -*- coding:utf-8 -*-
from altaircms.widget.models import WidgetDisposition
from altaircms.plugins.widget.image.models import ImageWidget
from altaircms.plugins.widget.freetext.models import FreetextWidget
from altaircms.lib.testutils import functionalTestSetUp
from altaircms.lib.testutils import functionalTestTearDown

import unittest
import datetime
import os.path
import json

class UseAssetMixin(object):
    def _getImageAsset(self):
        from altaircms.asset.models import ImageAsset
        D = {'filepath': u'/static/img/samples/Abstract_Desktop_290.jpg',
             'id': 1,
             "page_id": 2}
        return ImageAsset.from_dict(D)


class UseWidgetMixin(object):
    def _getTextWidget(self):
        D = {'id': 1, 'text': u'freetext',"page_id": 2}
        return FreetextWidget.from_dict(D)

    def _getImageWidget(self):
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

    
class WidgetDispositionTest(UseAssetMixin, 
                                  UseWidgetMixin, 
                                  UsePageEtcMixin, 
                                  unittest.TestCase):
    def setUp(self):
        DIR = os.path.dirname(os.path.abspath(__file__))
        app = functionalTestSetUp({"mako.directories": os.path.join(DIR, "templates"), })
        from webtest import TestApp
        self.testapp = TestApp(app)

    def tearDown(self):
        functionalTestTearDown()

    def test_create_from_page(self):
        session = self._getSession()
        self._addData(session)
        page = self._get_page()
        wd = WidgetDisposition.from_page(page, session)

        self.assertEquals(len(wd.widgets), 2)

    def test_bind_page(self):
        session = self._getSession()
        wd = self._make_disposition(session)
        from altaircms.page.models import Page
        page = Page()
        wd.bind_page(page, session)

        self.assertEquals(json.loads(page.structure).keys(),
                          json.loads(wd.structure).keys())
        ## todo. もっとまじめにチェック


    def _make_disposition(self, session):
        self._addData(session)
        page = self._get_page()
        return WidgetDisposition.from_page(page, session)
        
    def _get_page(self):
        from altaircms.page.models import Page
        return Page.query.first()
        
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

