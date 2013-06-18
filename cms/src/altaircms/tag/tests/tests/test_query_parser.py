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
    def tearDown(self):
        import transaction
        transaction.abort()

    def _makeOne(self, query):
        from altaircms.tag.manager import QueryParser
        return QueryParser(query)
    
    def _getTagManager(self):
        from altaircms.tag.manager import TagManager
        from altaircms.page.models import PageSet
        from altaircms.tag import models as m
        return TagManager(Object=PageSet, XRef=m.PageTag2Page, Tag=m.PageTag)

    def _callFUT(self, manager, query, **kwargs):
        qp = self._makeOne(query)
        return qp.and_search_by_manager(manager, **kwargs)

    def _makePage(self, **kwargs):
        from altaircms.page.models import PageSet
        return PageSet(**kwargs)

    def _makeTag(self, **kwargs):
        from altaircms.tag.models import PageTag
        return PageTag(**kwargs)

    def _getSession(self):
        from altaircms.models import DBSession
        return DBSession

    def test_it(self):
        organization_id = 1

        manager = self._getTagManager()
        session = self._getSession()

        page0 = self._makePage(name=u"xyz abc", organization_id=organization_id)
        abc_tag = self._makeTag(label=u"abc", organization_id=organization_id)
        page0.tags.append(self._makeTag(label=u"xyz", organization_id=organization_id))
        page0.tags.append(abc_tag)

        page1 = self._makePage(name=u"def abc", organization_id=organization_id)
        page1.tags.append(self._makeTag(label=u"def", organization_id=organization_id))
        page1.tags.append(abc_tag)
        session.add(page0)
        session.add(page1)

        self.assertEquals(len(self._callFUT(manager, u"abc def xyz", organization_id=organization_id).all()), 0)
        self.assertEquals(len(self._callFUT(manager, u"abc", organization_id=organization_id).all()), 2)
        self.assertEquals(len(self._callFUT(manager, u"abc xyz", organization_id=organization_id).all()), 1)
        self.assertEquals(len(self._callFUT(manager, u"abc def", organization_id=organization_id).all()), 1)

    def test_with_another_organization(self):
        organization_id = 1

        manager = self._getTagManager()
        session = self._getSession()

        page0 = self._makePage(name=u"xyz abc", organization_id=organization_id)
        abc_tag = self._makeTag(label=u"abc", organization_id=organization_id)
        page0.tags.append(self._makeTag(label=u"xyz", organization_id=organization_id))
        page0.tags.append(abc_tag)

        page1 = self._makePage(name=u"def abc", organization_id=organization_id)
        page1.tags.append(self._makeTag(label=u"def", organization_id=organization_id))
        page1.tags.append(abc_tag)
        session.add(page0)
        session.add(page1)
        self.assertEquals(len(self._callFUT(manager, u"abc def xyz", organization_id=22222222222).all()), 0)
        self.assertEquals(len(self._callFUT(manager, u"abc", organization_id=22222222222).all()), 0)
        self.assertEquals(len(self._callFUT(manager, u"abc xyz", organization_id=22222222222).all()), 0)
        self.assertEquals(len(self._callFUT(manager, u"abc def", organization_id=22222222222).all()), 0)

if __name__ == "__main__":
    from altaircms.tag.tests import setUpModule as S
    S()
    unittest.main()
