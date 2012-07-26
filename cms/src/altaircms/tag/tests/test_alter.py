# -*- coding:utf-8 -*-
import unittest

class PageTagAlterTest(unittest.TestCase):
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

    def _makeOne(self):
        from altaircms.tag.manager import TagManager
        from altaircms.page.models import Page
        from altaircms.tag import models as m
        return TagManager(Object=Page, XRef=m.PageTag2Page, Tag=m.PageTag)

    ## create
    #

    def test_tagged_when_create(self):
        page = self._withSession(self._makePage())
        manager = self._makeOne()

        tag_label_list = [u"ko", u"ni", u"ti", u"wa"]
        manager.replace_tags(page, tag_label_list)

        self.assertEquals(len(page.tags), 4)
        for tag, k in zip(sorted(page.tags, key=lambda x : x.label),
                          sorted(tag_label_list)):
            self.assertEquals(tag.label, k)

    def test_tagged_from_sameword_list(self):
        page = self._withSession(self._makePage())
        manager = self._makeOne()

        ## same word list
        tag_label_list = [u"po", u"po", u"po", u"po", u"po"]
        manager.replace_tags(page, tag_label_list)

        from altaircms.tag.models import PageTag
        self.assertEquals(PageTag.query.count(), 1)
            
    def test_tagged_when_create_with_public_status(self):
        page = self._withSession(self._makePage())
        manager = self._makeOne()

        ## add public
        tag_label_list = [u"pub", u"both", u"公開"]
        manager.replace_tags(page, tag_label_list, public_status=True)
        self.assertEquals(len(page.tags), 3)
        
        ## add private
        tag_label_list = [u"unpub", u"both", u"非公開"]
        manager.replace_tags(page, tag_label_list, public_status=False)
        self.assertEquals(len(page.tags), 6)

    def test_same_tagged_two_pages(self):
        page = self._withSession(self._makePage())
        another = self._withSession(self._makePage())
        manager = self._makeOne()

        tag_label_list = [u"ko", u"ni", u"ti", u"wa"]
        manager.replace_tags(page, tag_label_list)
        manager.replace_tags(another, tag_label_list)

        self.assertEquals(manager.Object.query.count(), 2)
        self.assertEquals(manager.Tag.query.count(), 4)
        self.assertEquals(manager.XRef.query.count(), 8)

    ## update
    ##
        
    def test_tagged_when_update(self):
        """ tag: bool, cool, tool => bool, kool, tool
        """
        # create
        session = self._getSession()
        page = self._withSession(self._makePage())
        manager = self._makeOne()
        manager.replace_tags(page, [u"fool", u"bool", u"cool"])
        session.flush()
        # update
        tag_label_list = [u"fool", u"bool", u"kool"]
        manager.replace_tags(page, tag_label_list)
        
        self.assertEquals(len(page.tags), 3)
        for tag, k in zip(sorted(page.tags, key=lambda x : x.label),
                          sorted(tag_label_list)):
            self.assertEquals(tag.label, k)

    ## delete
    #

    def test_untagged_when_update(self):
        # create
        session = self._getSession()
        page = self._withSession(self._makePage())
        manager = self._makeOne()
        manager.replace_tags(page, [u"fool", u"bool", u"cool"])
        session.flush()
        # untagged
        deletes = [u"fool", u"bool"]
        manager.delete_tags(page, deletes)
        
        self.assertEquals(len(page.tags), 1)
        self.assertEquals(page.tags[0].label, u"cool")


    def test_tagged_when_delete_with_public_status(self):
        page = self._withSession(self._makePage())
        manager = self._makeOne()

        tag_label_list = [u"pub", u"both", u"公開"]
        manager.replace_tags(page, tag_label_list, public_status=True)
        tag_label_list = [u"unpub", u"both", u"非公開"]
        manager.replace_tags(page, tag_label_list, public_status=False)

        ## delete private `both' tag
        manager.delete_tags(page, [u"both"], public_status=True)
        self.assertEquals(len(page.tags), 5)
       
if __name__ == "__main__":
    import altaircms.page.models
    import altaircms.event.models
    import altaircms.asset.models
    import altaircms.tag.models
    from altaircms.testing import db_initialize_for_unittest
    db_initialize_for_unittest()
