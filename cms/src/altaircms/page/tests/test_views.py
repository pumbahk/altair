# -*- coding:utf-8 -*-
import unittest
from altaircms.models import DBSession
from altaircms.page.models import Page

def setUpModule():
    DBSession.remove()

def tearDownModule():
    from altaircms.lib.testutils import dropall_db
    dropall_db(message="test view drop")

class PageFunctionalTests(unittest.TestCase):
   def setUp(self):
        from altaircms import main
        app = main({}, **{"sqlalchemy.url": "sqlite://", 
                            "session.secret": "B7gzHVRUqErB1TFgSeLCHH3Ux6ShtI", 
                            "mako.directories": "altaircms:templates", 
                            "altaircms.debug.strip_security": 'true', 
                            "altaircms.plugin_static_directory": "altaircms:plugins/static", 
                            "altaircms.layout_directory": "."})
        from altaircms.lib.testutils import create_db
        create_db()

        from webtest import TestApp
        self.testapp = TestApp(app)
        
   def _create_layout(self):
       from altaircms.layout.models import Layout
       layout = Layout(blocks="[]")
       DBSession.add(layout)
       import transaction
       transaction.commit()
   
   def create(self, title="title"):
       params = {u'description': u'descriptioin',
                 u'keywords': u'keywords',
                 u'layout': u"1",
                 u'title': title, 
                 u'url': u'/tmp/url'}
       self.testapp.post("/page/", params, status=302)

   def update(self, obj_id, title="title"):
       params = {u'_method': u'put',
                 u'description': u'music page',
                 u'keywords': u'music,rhythm,etc',
                 u'layout': u'1',
                 u'stage': u'execute',
                 u'tags': u'music',
                 u'title': title,
                 u'url': u'top/music'}

       self.testapp.post("/page/%s/update" % obj_id, params, status=302)

   def delete(self, obj_id):
       params = {u'_method': u'delete'}
       self.testapp.post("/page/%s/delete" % obj_id, params, status=302)

   def duplicate(self, obj_id):
       params = {}
       self.testapp.post("/page/%s/duplicate" % obj_id, params, status=302)

   def test_it(self):
       self._create_layout()

       ## create
       self.create(title="page_title")
       self.assertEquals(Page.query.count(), 1)
       obj = Page.query.first()
       self.assertEquals(obj.title, "page_title")

       ## update
       self.update(obj.id, title="music")
       self.assertEquals(Page.query.count(), 1)
       obj = Page.query.first()
       self.assertEquals(obj.title, "music")

       ## D&Dでwidgetを追加するページが開ける
       self.testapp.get("/page/%s" % obj.id, status=200)
       ## duplicate
       self.duplicate(obj.id)
       self.assertEquals(Page.query.count(), 2)

       ## delete
       self.delete(obj.id)
       self.assertEquals(Page.query.count(), 1)
       
if __name__ == "__main__":
    unittest.main()
