# -*- coding:utf-8 -*-

import unittest

"""
URL生成時のmappingのテスト(参考:120427_Title・URLルール.xlsx)
"""

from altaircms.testing import setup_db
from altaircms.testing import teardown_db

def setUpModule():
    setup_db(models=[
            "altaircms.models", 
            "altaircms.topic.models", 
            "altaircms.event.models", 
            "altaircms.widget.models", 
            "altaircms.layout.models", 
            "altaircms.page.models"
            ])

def tearDownModule():
    teardown_db()
    
class GenrePageDefaultInfoTests(unittest.TestCase):
    def _getTarget(self):
        from altaircms.page.nameresolver import GenrePageInfoResolver
        return GenrePageInfoResolver

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    @classmethod
    def tearDownClass(cls):
        import transaction
        transaction.abort()

    @classmethod
    def setUpClass(cls):
        from altaircms.models import Genre, DBSession
        jpop = Genre(name=u"jpop", label=u"jポップ")
        music = Genre(name=u"music", label=u"音楽")
        top = Genre(name=u"top", label=u"トップ")
        jpop.add_parent(music)
        music.add_parent(top)
        jpop.add_parent(top, hop=2)
        DBSession.add(jpop)
        DBSession.flush()
        cls.jpop = jpop

    def test_url(self):
        class defaultinfo:
            url_prefix = None

        target = self._makeOne(defaultinfo)
        self.assertEqual(target.resolve_url(self.jpop), "/music/jpop")

    def test_url2(self):
        class defaultinfo:
            url_prefix = u"prefix-"

        target = self._makeOne(defaultinfo)
        self.assertEqual(target.resolve_url(self.jpop), "prefix-/music/jpop")


    @unittest.skip ("* #5609: maybe fix")
    def test_title(self):
        class defaultinfo:
            title_prefix = u"タイトル:"

        target = self._makeOne(defaultinfo)
        self.assertEqual(target.resolve_title(self.jpop), u"タイトル:音楽/jポップ")
        

    def test_description(self):
        class defaultinfo:
            description = u"this-is-description"

        target = self._makeOne(defaultinfo)
        self.assertEqual(target.resolve_description(self.jpop), u"this-is-description")

    def test_keywords(self):
        class defaultinfo:
            keywords = u"k0, k1, k2"

        target = self._makeOne(defaultinfo)
        self.assertEqual(target.resolve_keywords(self.jpop), u"k0, k1, k2, 音楽, jポップ")


class EventPageDefaultInfoTests(unittest.TestCase):
    def _getTarget(self):
        from altaircms.page.nameresolver import EventPageInfoResolver
        return EventPageInfoResolver

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    @classmethod
    def tearDownClass(cls):
        import transaction
        transaction.abort()

    @classmethod
    def setUpClass(cls):
        from altaircms.models import Genre, DBSession
        jpop = Genre(name=u"jpop", label=u"jポップ")
        music = Genre(name=u"music", label=u"音楽")
        top = Genre(name=u"top", label=u"トップ")
        jpop.add_parent(music)
        music.add_parent(top)
        jpop.add_parent(top, hop=2)
        DBSession.add(jpop)
        DBSession.flush()
        cls.jpop = jpop

    def test_url(self):
        class defaultinfo:
            url_prefix = None
        class event:
            title=u"this-is-event-name", 
            subtitle=u"this-is-event-subtitle", 
            code=u"EV0010"
            organization_id = None
        target = self._makeOne(defaultinfo)
        self.assertEqual(target.resolve_url(self.jpop, event=event), "/music/jpop/EV0010")

    def test_url2(self):
        class defaultinfo:
            url_prefix = u"prefix-"
        class event:
            title=u"this-is-event-name", 
            subtitle=u"this-is-event-subtitle", 
            code=u"EV0010"
            organization_id = None
        target = self._makeOne(defaultinfo)
        self.assertEqual(target.resolve_url(self.jpop, event=event), "prefix-/music/jpop/EV0010")

    def test_url_with_organization(self):
        class defaultinfo:
            url_prefix = u"prefix-"
        class event:
            title=u"this-is-event-name", 
            subtitle=u"this-is-event-subtitle", 
            code=u"RTEV0010"
            organization_id = 1
            class organization:
                code = "RT"
        target = self._makeOne(defaultinfo)
        self.assertEqual(target.resolve_url(self.jpop, event=event), "prefix-/music/jpop/RTEV0010")


    @unittest.skip ("* #5609: maybe fix")
    def test_title_only(self):
        class defaultinfo:
            title_prefix = u"タイトル:"
        class event:
            title=u"this-is-event-name"
            subtitle = None
            code=u"EV0010"
            organization_id = None
        target = self._makeOne(defaultinfo)
        self.assertEqual(target.resolve_title(self.jpop, event=event), u"this-is-event-name")

    @unittest.skip ("* #5609: maybe fix")
    def test_title_has_subtitle(self):
        class defaultinfo:
            title_prefix = u"タイトル:"
        class event:
            title=u"this-is-event-name"
            subtitle=u"this-is-event-subtitle"
            code=u"EV0010"
            organization_id = None
        target = self._makeOne(defaultinfo)
        self.assertEqual(target.resolve_title(self.jpop, event=event), u"this-is-event-subtitle")
        

    def test_description(self):
        class defaultinfo:
            description = u"this-is-description"
        class event:
            title=u"this-is-event-name", 
            description = "description"
            organization_id = None
        target = self._makeOne(defaultinfo)
        self.assertEqual(target.resolve_description(self.jpop, event=event), u"this-is-description description ")

    def test_keywords(self):
        class defaultinfo:
            keywords = u"k0, k1, k2"
        class event:
            title = u"this-is-event-name"
            class pageset:
                public_tags = []
            pagesets = [pageset]
            organization_id = None
        target = self._makeOne(defaultinfo)
        self.assertEqual(target.resolve_keywords(self.jpop, event=event), u"this-is-event-name, k0, k1, k2, 音楽, jポップ")

    def test_keywords_with_pagetags(self):
        class defaultinfo:
            keywords = u"k0, k1, k2"
        class event:
            title = u"this-is-event-name"
            organization_id = 1
            class Pageset:
                class Tag:
                    organization_id = 1
                    label=u"イベントのタグ"
                class Tag2:
                    organization_id = 2
                    label=u"invalid-key"
                public_tags = [Tag, Tag2]
            pagesets = [Pageset]
            
        target = self._makeOne(defaultinfo)
        self.assertEqual(target.resolve_keywords(self.jpop, event=event), u"this-is-event-name, イベントのタグ, k0, k1, k2, 音楽, jポップ")

class NoGenreEventPageDefaultInfoTests(unittest.TestCase):
    def _getTarget(self):
        from altaircms.page.nameresolver import EventPageInfoResolver
        return EventPageInfoResolver

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    @classmethod
    def tearDownClass(cls):
        import transaction
        transaction.abort()

    def test_url(self):
        class defaultinfo:
            url_prefix = None
        class event:
            title=u"this-is-event-name", 
            subtitle=u"this-is-event-subtitle", 
            code=u"EV0010"
            organization_id = None
        target = self._makeOne(defaultinfo)
        self.assertEqual(target.resolve_url(None, event=event), "/EV0010")

    def test_url2(self):
        class defaultinfo:
            url_prefix = u"prefix-"
        class event:
            title=u"this-is-event-name", 
            subtitle=u"this-is-event-subtitle", 
            code=u"EV0010"
            organization_id = None
        target = self._makeOne(defaultinfo)
        self.assertEqual(target.resolve_url(None, event=event), "prefix-/EV0010")


    @unittest.skip ("* #5609: maybe fix")
    def test_title_only(self):
        class defaultinfo:
            title_prefix = u"タイトル:"
        class event:
            title=u"this-is-event-name"
            subtitle = None
            code=u"EV0010"

        target = self._makeOne(defaultinfo)
        self.assertEqual(target.resolve_title(None, event=event), u"this-is-event-name")

    @unittest.skip ("* #5609: maybe fix")
    def test_title_has_subtitle(self):
        class defaultinfo:
            title_prefix = u"タイトル:"
        class event:
            title=u"this-is-event-name"
            subtitle=u"this-is-event-subtitle"
            code=u"EV0010"

        target = self._makeOne(defaultinfo)
        self.assertEqual(target.resolve_title(None, event=event), u"this-is-event-subtitle")
        

    def test_description(self):
        class defaultinfo:
            description = u"this-is-description"
        class event:
            title=u"this-is-event-name", 
            description = "description"

        target = self._makeOne(defaultinfo)
        self.assertEqual(target.resolve_description(None, event=event), u"this-is-description description ")

    def test_keywords(self):
        class defaultinfo:
            keywords = u"k0, k1, k2"
        class event:
            title = u"this-is-event-name"
            class pageset:
                public_tags = []
            pagesets = [pageset]

        target = self._makeOne(defaultinfo)
        self.assertEqual(target.resolve_keywords(None, event=event), u"this-is-event-name, k0, k1, k2")

    def test_keywords_with_pagetags(self):
        class defaultinfo:
            keywords = u"k0, k1, k2"
        class event:
            title = u"this-is-event-name"
            organization_id = 1
            class Pageset:
                class Tag:
                    organization_id = 1
                    label=u"イベントのタグ"
                class Tag2:
                    organization_id = 2
                    label=u"invalid-key"
                public_tags = [Tag, Tag2]
            pagesets = [Pageset]
            
        target = self._makeOne(defaultinfo)
        self.assertEqual(target.resolve_keywords(None, event=event), u"this-is-event-name, イベントのタグ, k0, k1, k2")
        
if __name__ == "__main__":
    unittest.main()


