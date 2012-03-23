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
        D = {"id": 2, "asset": asset,  "asset_id": asset.id, "page_id":2}
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


class WithWidgetPageTest(UseAssetMixin, 
                    UseWidgetMixin, 
                    UsePageEtcMixin, 
                    unittest.TestCase):
    DIR = os.path.dirname(os.path.abspath(__file__))
    def setUp(self):
        from altaircms import main
        app = main({}, **{"sqlalchemy.url": "sqlite://", 
                          "mako.directories": os.path.join(self.DIR, "templates"), 
                          "altaircms.plugin_static_directory": "altaircms:plugins/static", 
                          "altaircms.debug.strip_security": "true", 
                          "session.secret": "B7gzHVRUqErB1TFgSeLCHH3Ux6ShtI", 
                          "altaircms.layout_directory": "."})
        from altaircms.lib.testutils import create_db
        create_db()
        from webtest import TestApp
        self.testapp = TestApp(app)

    def tearDown(self):
        import transaction
        transaction.abort()
        self._getSession().remove()
        
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
        self.assertEquals(Widget.query.count(), 2)
        page = Page.query.first()
        
        cloned =  page.clone(session)
        self.assertEquals(Page.query.count(), 2)
        self.assertTrue(u"コピー" in cloned.title)
        self.assertEquals(Widget.query.count(), 4)
        self.assertEquals(cloned.structure, 
                          json.dumps({"content": [{"pk": 3, "name": "freetext"}],
                                      "footer":  [{"pk": 4, "name": "image"}]}))


class DispositionViewFunctionalTest(WithWidgetPageTest):
    def _another_page(self, session):
        from altaircms.page.models import Page
        page = Page()
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

    def _page_and_widget_count(self, session, page_id):
        from altaircms.page.models import Page
        from altaircms.widget.models import Widget
        # print [(w.id, w.page_id, w.disposition_id) for w in Widget.query.all()]
        where = (Page.id==Widget.page_id) & (Page.id==page_id)
        return session.query(Widget, Page).filter(where).count()
        
    def test_it(self):
        """widget layout 保存. widget layout の読み込み"""
        session = self._getSession()
        self._addData(session)
        self.assertEquals(self._page_and_widget_count(session, 0), 0)

        ## save
        from altaircms.widget.models import WidgetDisposition
        self.assertEquals(WidgetDisposition.query.count(), 0)
        self._save(session)
        self.assertEquals(WidgetDisposition.query.count(), 1)

        ## create another page
        page1_id = self._another_page(session).id
        self.assertEquals(self._page_and_widget_count(session, page1_id), 0)

        ## load
        wdisposition = WidgetDisposition.query.first()
        self._load(session, page1_id, wdisposition.id)
        self.assertNotEquals(self._page_and_widget_count(session, page1_id), 0)

if __name__ == "__main__":
    unittest.main()
