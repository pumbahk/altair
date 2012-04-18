# -*- coding:utf-8 -*-
import unittest
import datetime
import os.path
import json

from altaircms.lib.testutils import functionalTestSetUp
from altaircms.lib.testutils import functionalTestTearDown

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
        D = {"id": 2, "asset": asset,  "asset_id": asset.id, "page_id":2}
        return ImageWidget.from_dict(D)

    def _getMenuWidget(self):
        from altaircms.plugins.widget.menu.models import MenuWidget
        D = {"id": 3,  "page_id":2, "items":"[]"}
        return MenuWidget.from_dict(D)


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
             'url': 'sample_page',
             'version': None}
        return Page.from_dict(D)

    def _getLayout(self):
        from altaircms.layout.models import Layout
        D = {'blocks': '[["content"],["footer"], ["js_prerender"], ["js_postrender"]]',
             'client_id': None,
             'created_at': datetime.datetime(2012, 2, 16, 11, 26, 55, 755523),
             'id': 2,
             'site_id': None,
             'template_filename': u'layout.mako',
             'title': 'simple',
             'updated_at': datetime.datetime(2012, 2, 16, 11, 26, 55, 755641)}
        return Layout.from_dict(D)


class WithWidgetPageTest(UseAssetMixin, 
                    UseWidgetMixin, 
                    UsePageEtcMixin, 
                    unittest.TestCase):
    DIR = os.path.dirname(os.path.abspath(__file__))

    def setUp(self):
        app = functionalTestSetUp()
        from webtest import TestApp
        self.testapp = TestApp(app)

    def tearDown(self):
        functionalTestTearDown()
        
    def _addData(self, session):
        structure = '''
{"content": [{"pk": 3,  "name":"menu"}, {"pk": 1, "name": "freetext"}],
 "footer": [{"pk": 2, "name": "image"}]}
'''
        session.add(self._getPage(structure))
        session.add(self._getLayout())
        session.add(self._getTextWidget())
        session.add(self._getImageWidget())
        session.add(self._getMenuWidget())
        import transaction
        transaction.commit()

    def _getSession(self):
        from altaircms.models import DBSession
        return DBSession
"""
todo: このあたり汚くて治したい。
"""
class PageCloneTest(WithWidgetPageTest):
    """ pageの複製のテスト
    """
    def test_it(self):
        from altaircms.page.models import Page
        from altaircms.widget.models import Widget

        session = self._getSession()
        self._addData(session)

        self.assertEquals(Page.query.count(), 1)
        self.assertEquals(Widget.query.count(), 3)
        page = Page.query.first()
        
        cloned =  page.clone(session)
        self.assertEquals(Page.query.count(), 2)
        self.assertTrue(u"コピー" in cloned.title)
        self.assertEquals(Widget.query.count(), 6)
        self.assertEquals(cloned.structure, 
                          json.dumps({"content": [{"pk": 4, "name": "menu"}, 
                                                  {"pk": 5, "name": "freetext"}],
                                      "footer":  [{"pk": 6, "name": "image"}]}))

class DispositionViewFunctionalTest(WithWidgetPageTest):
    def _another_page(self, session):
        from altaircms.page.models import Page
        from altaircms.page.models import Layout
        page = Page(layout=Layout())
        session.add(page)
        session.flush()
        return page

    def _save(self, session):
        from altaircms.page.models import Page
        page = Page.query.first()
        params = dict(page=page.id, title=u"テキトーな名前")
        self.testapp.post("/page/%s/disposition" % page.id, params, status=302)

    def _load(self, session, page_id, wdisposition_id):
        import transaction
        transaction.commit()
        params = {"disposition":wdisposition_id}
        self.testapp.get("/page/%s/disposition" % page_id, params, status=302)     

    def _delete(self, wdisposition_id):
        self.testapp.post("/disposition/%s/alter" % wdisposition_id)

    def _page_and_widget_count(self, session, page_id):
        from altaircms.page.models import Page
        from altaircms.widget.models import Widget
        where = (Page.id==Widget.page_id) & (Page.id==page_id)
        return session.query(Widget, Page).filter(where).count()
        
    def test_it(self):
        """widget layout 保存. widget layout の読み込み"""
        from altaircms.widget.models import WidgetDisposition

        session = self._getSession()
        self._addData(session)
        self.assertEquals(self._page_and_widget_count(session, 0), 0)

        ## save
        self.assertEquals(WidgetDisposition.query.count(), 0)
        self._save(session)
        self.assertEquals(WidgetDisposition.query.count(), 1)

        ## create another page
        another_page_id = self._another_page(session).id
        self.assertEquals(self._page_and_widget_count(session, another_page_id), 0)

        ## load
        wdisposition = WidgetDisposition.query.first()
        wdisposition_id = wdisposition.id
        self.assertEquals(WidgetDisposition.query.count(), 1)
        self._load(session, another_page_id, wdisposition_id)
        self.assertEquals(WidgetDisposition.query.count(), 2)
        self.assertNotEquals(self._page_and_widget_count(session, another_page_id), 0)

        ## delete
        self.assertEquals(WidgetDisposition.query.count(), 2)
        self._delete(wdisposition_id)
        self.assertEquals(WidgetDisposition.query.count(), 1)

    def test_bind_disposition_and_page_structure_has_page_id(self):
        """ save後のstructureはwidgetのPkを持ち、nullではない。
        """
        from altaircms.widget.models import WidgetDisposition

        ## create
        session = self._getSession()
        self._addData(session)
        self._save(session)

        ## bind to another page
        another_page_id = self._another_page(session).id
        wdisposition = WidgetDisposition.query.first()
        wdisposition_id = wdisposition.id
        self._load(session, another_page_id, wdisposition_id)

        from altaircms.page.models import Page
        bound_page = Page.query.filter(Page.id==another_page_id).one()
        structure = json.loads(bound_page.structure)
        for k, block in structure.items():
            for w in block:
                self.assertNotEqual(w["pk"], None)

    def test_if_bind_disposition_many_times(self):
        """ 何度もwidget layoutをloadできる.その時WidgetLayoutのsnapshotが作成される
        """
        from altaircms.widget.models import WidgetDisposition

        ## create
        session = self._getSession()
        self._addData(session)
        self._save(session)

        ## bind to another page
        another_page_id = self._another_page(session).id
        wdisposition = WidgetDisposition.query.first()
        wdisposition_id = wdisposition.id

        ## bound many times
        self._load(session, another_page_id, wdisposition_id)
        self._load(session, another_page_id, wdisposition_id)
        self._load(session, another_page_id, wdisposition_id)
        self.assertEquals(WidgetDisposition.query.count(), 4)
        

        
    def test_save_and_delete_number_of_widget(self):
        """ widgetも一緒に消されるはず.
        1. page生成 -> widget*2
        2. widget layout保存 -> widget*4
        3. widget layout削除 -> widget*2"""

        from altaircms.widget.models import Widget
        from altaircms.widget.models import WidgetDisposition

        ## create
        session = self._getSession()
        self._addData(session)
        self.assertEquals(Widget.query.count(), 3)
        self._save(session)
        self.assertEquals(Widget.query.count(), 6)
        
        ## delete
        wdisposition = WidgetDisposition.query.first()
        self._delete(wdisposition.id)
        self.assertEquals(Widget.query.count(), 3)

if __name__ == "__main__":
    unittest.main()
