# -*- coding:utf-8 -*-
import unittest

class PageQueryParserTests(unittest.TestCase):
    def _makeOne(self, query):
        from altaircms.tag.manager import QueryParser
        return QueryParser(query)
        
    def _callFUT(self, query):
        return self._makeOne(query).parse()

    def test_whitespace(self):
        self.assertEquals(self._callFUT("foo bar"), ["foo", "bar"])
        self.assertEquals(self._callFUT("foo   bar"), ["foo", "bar"])
        self.assertEquals(self._callFUT("  foo   bar"), ["foo", "bar"])
        self.assertEquals(self._callFUT("foo   bar   "), ["foo", "bar"])

    def test_zenkakuspace(self):
        self.assertEquals(self._callFUT(u"あかさたな　はま"), [u"あかさたな", u"はま"])
        self.assertEquals(self._callFUT(u"　あかさたな　はま"), [u"あかさたな", u"はま"])
        self.assertEquals(self._callFUT(u"あかさたな　はま　"), [u"あかさたな", u"はま"])


class PageQueryParserSearchTests(unittest.TestCase):
    def _makeOne(self, query):
        from altaircms.tag.manager import QueryParser
        return QueryParser(query)
    
    def _getTagManager(self):
        from altaircms.tag.manager import TagManager
        from altaircms.page.models import Page
        from altaircms.tag import models as m
        return TagManager(Object=Page, XRef=m.PageTag2Page, Tag=m.PageTag)

    def _callFUT(self, manager, query):
        qp = self._makeOne(query)
        return qp.and_search_by_manager(manager)

    def _makePage(self, **kwargs):
        from altaircms.page.models import Page
        return Page(**kwargs)

    def _makeTag(self, **kwargs):
        from altaircms.tag.models import PageTag
        return PageTag(**kwargs)

    def _getSession(self):
        from altaircms.models import DBSession
        return DBSession

    def test_it(self):
        manager = self._getTagManager()
        session = self._getSession()

        page0 = self._makePage(title=u"xyz abc")
        abc_tag = self._makeTag(label=u"abc")
        page0.tags.append(self._makeTag(label=u"xyz"))
        page0.tags.append(abc_tag)

        page1 = self._makePage(title=u"def abc")
        page1.tags.append(self._makeTag(label=u"def"))
        page1.tags.append(abc_tag)
        session.add(page0)
        session.add(page1)

        self.assertEquals(len(self._callFUT(manager, u"abc def xyz").all()), 0)
        self.assertEquals(len(self._callFUT(manager, u"abc").all()), 2)
        self.assertEquals(len(self._callFUT(manager, u"abc xyz").all()), 1)
        self.assertEquals(len(self._callFUT(manager, u"abc def").all()), 1)

if __name__ == "__main__":
    import altaircms.page.models
    import altaircms.tag.models
    import altaircms.event.models
    import altaircms.asset.models
    from altaircms.testing import db_initialize_for_unittest
    db_initialize_for_unittest()
    unittest.main()
