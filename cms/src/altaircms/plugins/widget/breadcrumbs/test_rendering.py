# -*-coding:utf-8 -*-
import unittest
from altaircms.testing import setup_db
from altaircms.testing import teardown_db

def setUpModule():
    setup_db(models=[
            "altaircms.models", 
            "altaircms.topic.models", 
            "altaircms.event.models", 
            "altaircms.widget.models", 
            "altaircms.page.models", 
            ])

def tearDownModule():
    teardown_db()

class BreadCrumbsOrderTest(unittest.TestCase):
    def _make_page(self, title, parent=None):
        from altaircms.page.models import Page, PageSet
        page = Page.from_dict(dict(title=title))
        pageset = PageSet.get_or_create(page)

        if parent:
            pageset.parent = parent.pageset
        return page

    def _callFUT(self, page):
        from altaircms.plugins.widget.breadcrumbs.models import BreadcrumbsWidget
        return BreadcrumbsWidget().get_ancestor_pages(page)
    
    def test_single(self):
        page = self._make_page("a")
        result = self._callFUT(page)
        self.assertEquals(result, [])

    def test_it(self):
        page0 = self._make_page("a")
        page1 = self._make_page("b", parent=page0)
        page2 = self._make_page("c", parent=page1)

        self.assertEquals(page2.title, "c")
        result = self._callFUT(page2)
        self.assertEquals([ps.pages[0].title for ps in result], 
                          ["b", "a"])

    def test_with_genre(self):
        from altaircms.models import Genre
        from altaircms.models import DBSession
        top = Genre(label=u"トップ", name="top")
        music = Genre(label=u"音楽", name="music")
        music.add_parent(top)

        music.category_top_pageset = self._make_page("music").pageset
        top.category_top_pageset = self._make_page("top").pageset
        event_detail_page = self._make_page("event-detail-page")
        event_detail_page.pageset.genre = music

        DBSession.add(music)
        DBSession.add(top)
        DBSession.add(event_detail_page)
        DBSession.flush()
        self.assertEquals(event_detail_page.title, "event-detail-page")
        result = self._callFUT(event_detail_page)
        self.assertEquals([ps.pages[0].title for ps in result], 
                          ["music", "top"])
        

        

if __name__ == "__main__":
    unittest.main()

