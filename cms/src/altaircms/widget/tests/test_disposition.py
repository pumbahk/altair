# -*- coding:utf-8 -*-
from altaircms.widget.models import WidgetDisposition
from altaircms.plugins.widget.image.models import ImageWidget
from altaircms.plugins.widget.freetext.models import FreetextWidget
from altaircms.widget.fetcher import WidgetFetcher
## todo delete it
WidgetFetcher.add_fetch_method(ImageWidget.type, ImageWidget)
WidgetFetcher.add_fetch_method(FreetextWidget.type, FreetextWidget)
from altaircms.testing import setup_db
from altaircms.testing import teardown_db

def setUpModule():
    setup_db(models=[
            "altaircms.models", 
            "altaircms.asset.models", 
            "altaircms.page.models", 
            "altaircms.widget.models", 
            "altaircms.event.models"
            ])

def tearDownModule():
    teardown_db()

import unittest
import datetime
import json

class UseAssetMixin(object):
    @classmethod
    def _getImageAsset(self):
        from altaircms.asset.models import ImageAsset
        D = {'filepath': u'/static/img/samples/Abstract_Desktop_290.jpg',
             'id': 1,
             "page_id": 2}
        return ImageAsset.from_dict(D)


class UseWidgetMixin(object):
    @classmethod
    def _getTextWidget(self):
        D = {'id': 1, 'text': u'freetext',"page_id": 2}
        return FreetextWidget.from_dict(D)
    @classmethod
    def _getImageWidget(self):
        asset = self._getImageAsset()
        D = {"id": 2, "asset": asset,  "asset_id": asset.id}
        return ImageWidget.from_dict(D)


class UsePageEtcMixin(object):
    @classmethod
    def _getPage(self, structure):
        from altaircms.page.models import Page
        D = {'created_at': datetime.datetime(2012, 2, 14, 15, 13, 26, 438062),
             'description': u'boo',
             'event_id': None,
             'id': 2,
             'keywords': u'oo',
             'layout_id': 2,
             'parent_id': None,
             'organization_id': None,
             'structure': structure, 
             'title': u'fofoo',
             'updated_at': datetime.datetime(2012, 2, 14, 15, 13, 26, 438156),
             'url': u'sample_page',
             'version': None}
        return Page.from_dict(D)
    @classmethod
    def _getLayout(self):
        from altaircms.layout.models import Layout
        D = {'blocks': u'[["content"],["footer"], ["js_prerender"], ["js_postrender"]]',
             'client_id': None,
             'created_at': datetime.datetime(2012, 2, 16, 11, 26, 55, 755523),
             'id': 2,
             'organization_id': None,
             'template_filename': u'layout.html',
             'title': u'simple',
             'updated_at': datetime.datetime(2012, 2, 16, 11, 26, 55, 755641)}
        return Layout.from_dict(D)

    
class WidgetDispositionTest(UseAssetMixin, 
                            UseWidgetMixin, 
                            UsePageEtcMixin, 
                            unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from altaircms.models import DBSession as session
        structure = u'''
{"content": [{"pk": 1, "name": "freetext"}],
 "footer": [{"pk": 2, "name": "image"}]}
'''
        session.add(cls._getPage(structure))
        session.add(cls._getLayout())
        session.add(cls._getTextWidget())
        session.add(cls._getImageWidget())
        session.flush()

    @classmethod
    def tearDownClass(cls):
        import transaction
        transaction.abort()

    def test_create_from_page(self):
        from altaircms.models import DBSession as session
        page = self._get_page()
        wd = WidgetDisposition.deep_copy_from_page(page, session)
        self.assertEquals(len(wd.widgets), 2)

    def test_bind_page(self):
        from altaircms.models import DBSession as session
        wd = self._make_disposition(session)
        from altaircms.page.models import Page
        page = Page()
        wd.bind_page(page, session)

        self.assertEquals(json.loads(page.structure).keys(),
                          json.loads(wd.structure).keys())
        ## todo. もっとまじめにチェック


    def _make_disposition(self, session):
        page = self._get_page()
        return WidgetDisposition.deep_copy_from_page(page, session)
        
    def _get_page(self):
        from altaircms.page.models import Page
        return Page.query.first()       

if __name__ == "__main__":
    unittest.main()

