# -*- coding:utf-8 -*-
from altaircms.modelmanager.ancestors import HasAncestorMixin
import unittest

class Node(HasAncestorMixin):
    def __init__(self, v, parent=None):
        self.parent = parent
        self.v = v

from altaircms.testing import setup_db
from altaircms.testing import teardown_db

def setUpModule():
    setup_db(models=[
            "altaircms.models", 
            "altaircms.event.models", 
            "altaircms.widget.models", 
            "altaircms.page.models", 
            ])

def tearDownModule():
    teardown_db()

class HasAncestorMixinTest(unittest.TestCase):
    def test_self(self):
        self.assertEquals([n.v for n in Node(10).ancestors], 
                         [])

    def test_parent_and_child(self):
        parent = Node(10)
        child0 = Node(20, parent=parent)
        child = Node(30, parent=child0)
        self.assertEquals([n.v for n in child.ancestors], 
                         [20, 10])

class GetWithGenrePagesetAncestorTests(unittest.TestCase):
    def _callFUT(self, pageset):
        from altaircms.modelmanager.ancestors import GetWithGenrePagesetAncestor
        return GetWithGenrePagesetAncestor(pageset).get_ancestors()

    def test_noparent(self):
        from altaircms.page.models import PageSet

        detail_page = PageSet()
        self.assertEqual(self._callFUT(detail_page), 
                         [])

    def test_ancestors_are_one(self):
        from altaircms.page.models import PageSet
        detail_page = PageSet()
        sub_page = PageSet(parent=detail_page)
        self.assertEqual(self._callFUT(sub_page), 
                         [detail_page])

    def test_ancestors_with_genre(self):
        from altaircms.page.models import PageSet
        from altaircms.models import Genre
        from altaircms.modellib import DBSession

        detail_page = PageSet()
        sub_page = PageSet(parent=detail_page)

        top = Genre(label=u"トップ", name="top")
        music = Genre(label=u"音楽", name="music")
        music.add_parent(top)
        top_page = PageSet()
        top.category_top_pageset = top_page
        music_page = PageSet()
        music.category_top_pageset = music_page

        detail_page.genre = music
        DBSession.add(top)
        DBSession.add(music)
        DBSession.flush()
        self.assertEqual(self._callFUT(sub_page), 
                         [detail_page, music_page, top_page])

if __name__ == "__main__":
    unittest.main()
