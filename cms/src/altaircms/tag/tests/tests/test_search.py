import unittest

class PageSearchTest(unittest.TestCase):
    def tearDown(self):
        import transaction
        transaction.abort()

    def _makeOne(self):
        from altaircms.tag.manager import TagManager
        from altaircms.page.models import PageSet
        from altaircms.tag import models as m
        return TagManager(Object=PageSet, XRef=m.PageTag2Page, Tag=m.PageTag)

    def _getSession(self):
        from altaircms.models import DBSession
        return DBSession

    def _makeSearchedObj(self, **kwargs):
        from altaircms.page.models import PageSet
        return PageSet(organization_id=1, **kwargs)

    def _makeTag(self, **kwargs):
        from altaircms.tag.models import PageTag
        return PageTag(organization_id=1,**kwargs)

    def test_empty(self):
        self.assertEquals(self._makeOne().search_by_tag_label(u"foo").count(), 0)


    def test_search_by_tag_label_by_label(self):
        session = self._getSession()

        obj = self._makeSearchedObj(name=u"page")
        obj.tags.append(self._makeTag(label=u"foo"))
        session.add(obj)

        target = self._makeOne()
        self.assertEquals(target.search_by_tag_label(u"foo").count(), 1)
        self.assertEquals(target.search_by_tag_label(u"boo").count(), 0)

    def test_search_by_tag_label_by_public_status(self):
        session = self._getSession()

        obj = self._makeSearchedObj(name=u"page")
        obj.tags.append(self._makeTag(label=u"public", publicp=True))
        obj.tags.append(self._makeTag(label=u"private", publicp=False))
        session.add(obj)

        target = self._makeOne()
        self.assertEquals(target.search_by_tag_label(u"public").count(), 1)
        self.assertEquals(target.public_search_by_tag_label(u"public").count(), 1)
        self.assertEquals(target.private_search_by_tag_label(u"public").count(), 0)

        self.assertEquals(target.search_by_tag_label(u"private").count(), 1)
        self.assertEquals(target.public_search_by_tag_label(u"private").count(), 0)
        self.assertEquals(target.private_search_by_tag_label(u"private").count(), 1)

class ImageAssetSearchTest(unittest.TestCase):
    def tearDown(self):
        import transaction
        transaction.abort()

    def _getSession(self):
        from altaircms.models import DBSession
        return DBSession

    def _makeSearchedObj(self, **kwargs):
        from altaircms.asset.models import ImageAsset
        return ImageAsset(organization_id=1,**kwargs)


    def _makeTag(self, **kwargs):
        from altaircms.tag.models import ImageAssetTag
        return ImageAssetTag(organization_id=1,**kwargs)

    def _makeOne(self):
        from altaircms.tag.manager import TagManager
        from altaircms.asset.models import ImageAsset
        from altaircms.tag import models as m
        return TagManager(Object=ImageAsset, XRef=m.AssetTag2Asset, Tag=m.AssetTag)

    def test_empty(self):
        self.assertEquals(self._makeOne().search_by_tag_label(u"foo").count(), 0)


    def test_search_by_tag_label_by_label(self):
        session = self._getSession()

        obj = self._makeSearchedObj(filepath=u"page")
        obj.tags.append(self._makeTag(label=u"foo"))
        session.add(obj)

        target = self._makeOne()
        self.assertEquals(target.search_by_tag_label(u"foo").count(), 1)
        self.assertEquals(target.search_by_tag_label(u"boo").count(), 0)

    def test_search_by_tag_label_by_public_status(self):
        session = self._getSession()

        obj = self._makeSearchedObj(filepath=u"page")
        obj.tags.append(self._makeTag(label=u"public", publicp=True))
        obj.tags.append(self._makeTag(label=u"private", publicp=False))
        session.add(obj)

        target = self._makeOne()
        self.assertEquals(target.search_by_tag_label(u"public").count(), 1)
        self.assertEquals(target.public_search_by_tag_label(u"public").count(), 1)
        self.assertEquals(target.private_search_by_tag_label(u"public").count(), 0)

        self.assertEquals(target.search_by_tag_label(u"private").count(), 1)
        self.assertEquals(target.public_search_by_tag_label(u"private").count(), 0)
        self.assertEquals(target.private_search_by_tag_label(u"private").count(), 1)


class MovieAssetSearchTest(unittest.TestCase):
    def tearDown(self):
        import transaction
        transaction.abort()

    def _getSession(self):
        from altaircms.models import DBSession
        return DBSession

    def _makeSearchedObj(self, **kwargs):
        from altaircms.asset.models import MovieAsset
        return MovieAsset(organization_id=1,**kwargs)


    def _makeTag(self, **kwargs):
        from altaircms.tag.models import MovieAssetTag
        return MovieAssetTag(organization_id=1,**kwargs)

    def _makeOne(self):
        from altaircms.tag.manager import TagManager
        from altaircms.asset.models import MovieAsset
        from altaircms.tag import models as m
        return TagManager(Object=MovieAsset, XRef=m.AssetTag2Asset, Tag=m.AssetTag)

    def test_empty(self):
        self.assertEquals(self._makeOne().search_by_tag_label(u"foo").count(), 0)

    def test_search_by_tag_label_by_label(self):
        session = self._getSession()

        obj = self._makeSearchedObj(filepath=u"page")
        obj.tags.append(self._makeTag(label=u"foo"))
        session.add(obj)

        target = self._makeOne()
        self.assertEquals(target.search_by_tag_label(u"foo").count(), 1)
        self.assertEquals(target.search_by_tag_label(u"boo").count(), 0)

    def test_search_by_tag_label_by_public_status(self):
        session = self._getSession()

        obj = self._makeSearchedObj(filepath=u"page")
        obj.tags.append(self._makeTag(label=u"public", publicp=True))
        obj.tags.append(self._makeTag(label=u"private", publicp=False))
        session.add(obj)

        target = self._makeOne()
        self.assertEquals(target.search_by_tag_label(u"public").count(), 1)
        self.assertEquals(target.public_search_by_tag_label(u"public").count(), 1)
        self.assertEquals(target.private_search_by_tag_label(u"public").count(), 0)

        self.assertEquals(target.search_by_tag_label(u"private").count(), 1)
        self.assertEquals(target.public_search_by_tag_label(u"private").count(), 0)
        self.assertEquals(target.private_search_by_tag_label(u"private").count(), 1)

class FlashAssetSearchTest(unittest.TestCase):
    def tearDown(self):
        import transaction
        transaction.abort()

    def _getSession(self):
        from altaircms.models import DBSession
        return DBSession

    def _makeSearchedObj(self, **kwargs):
        from altaircms.asset.models import FlashAsset
        return FlashAsset(organization_id=1,**kwargs)


    def _makeTag(self, **kwargs):
        from altaircms.tag.models import FlashAssetTag
        return FlashAssetTag(organization_id=1,**kwargs)

    def _makeOne(self):
        from altaircms.tag.manager import TagManager
        from altaircms.asset.models import FlashAsset
        from altaircms.tag import models as m
        return TagManager(Object=FlashAsset, XRef=m.AssetTag2Asset, Tag=m.AssetTag)

    def test_empty(self):
        self.assertEquals(self._makeOne().search_by_tag_label(u"foo").count(), 0)

    def test_search_by_tag_label_by_label(self):
        session = self._getSession()

        obj = self._makeSearchedObj(filepath=u"page")
        obj.tags.append(self._makeTag(label=u"foo"))
        session.add(obj)

        target = self._makeOne()
        self.assertEquals(target.search_by_tag_label(u"foo").count(), 1)
        self.assertEquals(target.search_by_tag_label(u"boo").count(), 0)

    def test_search_by_tag_label_by_public_status(self):
        session = self._getSession()

        obj = self._makeSearchedObj(filepath=u"page")
        obj.tags.append(self._makeTag(label=u"public", publicp=True))
        obj.tags.append(self._makeTag(label=u"private", publicp=False))
        session.add(obj)

        target = self._makeOne()
        self.assertEquals(target.search_by_tag_label(u"public").count(), 1)
        self.assertEquals(target.public_search_by_tag_label(u"public").count(), 1)
        self.assertEquals(target.private_search_by_tag_label(u"public").count(), 0)

        self.assertEquals(target.search_by_tag_label(u"private").count(), 1)
        self.assertEquals(target.public_search_by_tag_label(u"private").count(), 0)
        self.assertEquals(target.private_search_by_tag_label(u"private").count(), 1)

if __name__ == "__main__":
    from altaircms.tag.tests import setUpModule as S
    S()
    unittest.main()
