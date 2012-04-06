# -*- coding:utf-8 -*-
import unittest
config  = None
def setUpModule():
    global config
    from altaircms.lib import testutils
    config = testutils.config()
    config.include("altaircms.tag")
    testutils.create_db(force=False)
    
def tearDownModule():
    from pyramid.testing import tearDown
    tearDown()

class PageAlterTagTest(unittest.TestCase):
    def tearDown(self):
        import transaction
        transaction.abort()

    def _getSession(self):
        from altaircms.models import DBSession
        return DBSession

    def _makePage(self, **kwargs):
        from altaircms.page.models import Page
        return Page(**kwargs)

    def _makeTag(self, **kwargs):
        from altaircms.tag.models import PageTag
        return PageTag(**kwargs)

    def _withSession(self, o):
        self._getSession().add(o)
        return o

    def _getManger(self):
        from altaircms.tag.api import get_tagmanager
        return get_tagmanager

    def test_tagged_when_create(self):
        page = self._withSession(self._makePage())
        manager = self._getManger()("page")

        tag_label_list = [u"ko", u"ni", u"ti", u"wa"]
        manager.replace(page, tag_label_list)

        self.assertEquals(len(page.tags), 4)
        for tag, k in zip(sorted(page.tags, key=lambda x : x.label),
                          sorted(tag_label_list)):
            self.assertEquals(tag.label, k)

    def test_tagged_from_sameword_list(self):
        page = self._withSession(self._makePage())
        manager = self._getManger()("page")

        ## same word list
        tag_label_list = [u"po", u"po", u"po", u"po", u"po"]
        manager.replace(page, tag_label_list)

        from altaircms.tag.models import PageTag
        self.assertEquals(PageTag.query.count(), 1)
            
    def test_tagged_when_create_with_public_status(self):
        page = self._withSession(self._makePage())
        manager = self._getManger()("page")

        ## add public
        tag_label_list = [u"pub", u"both", u"公開"]
        manager.replace(page, tag_label_list, public_status=True)
        self.assertEquals(len(page.tags), 3)
        
        ## add unpublic
        tag_label_list = [u"unpub", u"both", u"非公開"]
        manager.replace(page, tag_label_list, public_status=False)
        self.assertEquals(len(page.tags), 6)

    def test_tagged_when_delete_with_public_status(self):
        page = self._withSession(self._makePage())
        manager = self._getManger()("page")

        tag_label_list = [u"pub", u"both", u"公開"]
        manager.replace(page, tag_label_list, public_status=True)
        tag_label_list = [u"unpub", u"both", u"非公開"]
        manager.replace(page, tag_label_list, public_status=False)

        ## delete unpublic `both' tag
        manager.delete(page, [u"both"], public_status=True)
        self.assertEquals(len(page.tags), 5)

    def test_tagged_when_update(self):
        """ tag: bool, cool, tool => bool, kool, tool
        """
        # create
        session = self._getSession()
        page = self._withSession(self._makePage())
        manager = self._getManger()("page")
        manager.replace(page, [u"fool", u"bool", u"cool"])
        session.flush()
        # update
        tag_label_list = [u"fool", u"bool", u"kool"]
        manager.replace(page, tag_label_list)
        
        self.assertEquals(len(page.tags), 3)
        for tag, k in zip(sorted(page.tags, key=lambda x : x.label),
                          sorted(tag_label_list)):
            self.assertEquals(tag.label, k)

    def test_untagged_when_update(self):
        # create
        session = self._getSession()
        page = self._withSession(self._makePage())
        manager = self._getManger()("page")
        manager.replace(page, [u"fool", u"bool", u"cool"])
        session.flush()
        # untagged
        deletes = [u"fool", u"bool"]
        manager.delete(page, deletes)
        
        self.assertEquals(len(page.tags), 1)
        self.assertEquals(page.tags[0].label, u"cool")

    def test_same_tagged_2target(self):
        page = self._withSession(self._makePage())
        another = self._withSession(self._makePage())
        manager = self._getManger()("page")

        tag_label_list = [u"ko", u"ni", u"ti", u"wa"]
        manager.replace(page, tag_label_list)
        manager.replace(another, tag_label_list)

        self.assertEquals(manager.Object.query.count(), 2)
        self.assertEquals(manager.Tag.query.count(), 4)
        self.assertEquals(manager.XRef.query.count(), 8)
        
if __name__ == "__main__":
    unittest.main()
    
