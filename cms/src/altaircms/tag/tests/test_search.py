import unittest

class PageSearchTest(unittest.TestCase):
    def tearDown(self):
        import transaction
        transaction.abort()

    def _makeOne(self):
        from altaircms.tag.manager import TagManager
        from altaircms.page.models import Page
        from altaircms.tag import models as m
        return TagManager(Object=Page, XRef=m.PageTag2Page, Tag=m.PageTag)

    def _getSession(self):
        from altaircms.models import DBSession
        return DBSession

    def _makeSearchedObj(self, **kwargs):
        from altaircms.page.models import Page
        return Page(**kwargs)

    def _makeTag(self, **kwargs):
        from altaircms.tag.models import PageTag
        return PageTag(**kwargs)

    def test_empty(self):
        self.assertEquals(self._makeOne().search("foo").count(), 0)

    def test_search_by_label(self):
        session = self._getSession()

        obj = self._makeSearchedObj(title=u"page")
        obj.tags.append(self._makeTag(label=u"foo"))
        session.add(obj)

        target = self._makeOne()
        self.assertEquals(target.search(u"foo").count(), 1)
        self.assertEquals(target.search(u"boo").count(), 0)

    def test_search_by_public_status(self):
        session = self._getSession()

        obj = self._makeSearchedObj(title=u"page")
        obj.tags.append(self._makeTag(label=u"public", publicp=True))
        obj.tags.append(self._makeTag(label=u"private", publicp=False))
        session.add(obj)

        target = self._makeOne()
        self.assertEquals(target.search(u"public").count(), 1)
        self.assertEquals(target.public_search(u"public").count(), 1)
        self.assertEquals(target.private_search(u"public").count(), 0)

        self.assertEquals(target.search(u"private").count(), 1)
        self.assertEquals(target.public_search(u"private").count(), 0)
        self.assertEquals(target.private_search(u"private").count(), 1)


class EventSearchTest(unittest.TestCase):
    def tearDown(self):
        import transaction
        transaction.abort()

    def _getSession(self):
        from altaircms.models import DBSession
        return DBSession

    def _makeSearchedObj(self, **kwargs):
        from altaircms.event.models import Event
        return Event(**kwargs)

    def _makeTag(self, **kwargs):
        from altaircms.tag.models import EventTag
        return EventTag(**kwargs)

    def _makeOne(self):
        from altaircms.tag.manager import TagManager
        from altaircms.event.models import Event
        from altaircms.tag import models as m
        return TagManager(Object=Event, XRef=m.EventTag2Event, Tag=m.EventTag)

    def test_empty(self):
        self.assertEquals(self._makeOne().search("foo").count(), 0)

    def test_search_by_label(self):
        session = self._getSession()

        obj = self._makeSearchedObj(title=u"page")
        obj.tags.append(self._makeTag(label=u"foo"))
        session.add(obj)

        target = self._makeOne()
        self.assertEquals(target.search(u"foo").count(), 1)
        self.assertEquals(target.search(u"boo").count(), 0)

    def test_search_by_public_status(self):
        session = self._getSession()

        obj = self._makeSearchedObj(title=u"page")
        obj.tags.append(self._makeTag(label=u"public", publicp=True))
        obj.tags.append(self._makeTag(label=u"private", publicp=False))
        session.add(obj)

        target = self._makeOne()
        self.assertEquals(target.search(u"public").count(), 1)
        self.assertEquals(target.public_search(u"public").count(), 1)
        self.assertEquals(target.private_search(u"public").count(), 0)

        self.assertEquals(target.search(u"private").count(), 1)
        self.assertEquals(target.public_search(u"private").count(), 0)
        self.assertEquals(target.private_search(u"private").count(), 1)

class ImageAssetSearchTest(unittest.TestCase):
    def tearDown(self):
        import transaction
        transaction.abort()

    def _getSession(self):
        from altaircms.models import DBSession
        return DBSession

    def _makeSearchedObj(self, **kwargs):
        from altaircms.asset.models import ImageAsset
        return ImageAsset(**kwargs)


    def _makeTag(self, **kwargs):
        from altaircms.tag.models import ImageAssetTag
        return ImageAssetTag(**kwargs)

    def _makeOne(self):
        from altaircms.tag.manager import TagManager
        from altaircms.asset.models import ImageAsset
        from altaircms.tag import models as m
        return TagManager(Object=ImageAsset, XRef=m.AssetTag2Asset, Tag=m.AssetTag)

    def test_empty(self):
        self.assertEquals(self._makeOne().search("foo").count(), 0)

    def test_search_by_label(self):
        session = self._getSession()

        obj = self._makeSearchedObj(filepath=u"page")
        obj.tags.append(self._makeTag(label=u"foo"))
        session.add(obj)

        target = self._makeOne()
        self.assertEquals(target.search(u"foo").count(), 1)
        self.assertEquals(target.search(u"boo").count(), 0)

    def test_search_by_public_status(self):
        session = self._getSession()

        obj = self._makeSearchedObj(filepath=u"page")
        obj.tags.append(self._makeTag(label=u"public", publicp=True))
        obj.tags.append(self._makeTag(label=u"private", publicp=False))
        session.add(obj)

        target = self._makeOne()
        self.assertEquals(target.search(u"public").count(), 1)
        self.assertEquals(target.public_search(u"public").count(), 1)
        self.assertEquals(target.private_search(u"public").count(), 0)

        self.assertEquals(target.search(u"private").count(), 1)
        self.assertEquals(target.public_search(u"private").count(), 0)
        self.assertEquals(target.private_search(u"private").count(), 1)

class MovieAssetSearchTest(unittest.TestCase):
    def tearDown(self):
        import transaction
        transaction.abort()

    def _getSession(self):
        from altaircms.models import DBSession
        return DBSession

    def _makeSearchedObj(self, **kwargs):
        from altaircms.asset.models import MovieAsset
        return MovieAsset(**kwargs)


    def _makeTag(self, **kwargs):
        from altaircms.tag.models import MovieAssetTag
        return MovieAssetTag(**kwargs)

    def _makeOne(self):
        from altaircms.tag.manager import TagManager
        from altaircms.asset.models import MovieAsset
        from altaircms.tag import models as m
        return TagManager(Object=MovieAsset, XRef=m.AssetTag2Asset, Tag=m.AssetTag)

    def test_empty(self):
        self.assertEquals(self._makeOne().search("foo").count(), 0)

    def test_search_by_label(self):
        session = self._getSession()

        obj = self._makeSearchedObj(filepath=u"page")
        obj.tags.append(self._makeTag(label=u"foo"))
        session.add(obj)

        target = self._makeOne()
        self.assertEquals(target.search(u"foo").count(), 1)
        self.assertEquals(target.search(u"boo").count(), 0)

    def test_search_by_public_status(self):
        session = self._getSession()

        obj = self._makeSearchedObj(filepath=u"page")
        obj.tags.append(self._makeTag(label=u"public", publicp=True))
        obj.tags.append(self._makeTag(label=u"private", publicp=False))
        session.add(obj)

        target = self._makeOne()
        self.assertEquals(target.search(u"public").count(), 1)
        self.assertEquals(target.public_search(u"public").count(), 1)
        self.assertEquals(target.private_search(u"public").count(), 0)

        self.assertEquals(target.search(u"private").count(), 1)
        self.assertEquals(target.public_search(u"private").count(), 0)
        self.assertEquals(target.private_search(u"private").count(), 1)

class FlashAssetSearchTest(unittest.TestCase):
    def tearDown(self):
        import transaction
        transaction.abort()

    def _getSession(self):
        from altaircms.models import DBSession
        return DBSession

    def _makeSearchedObj(self, **kwargs):
        from altaircms.asset.models import FlashAsset
        return FlashAsset(**kwargs)


    def _makeTag(self, **kwargs):
        from altaircms.tag.models import FlashAssetTag
        return FlashAssetTag(**kwargs)

    def _makeOne(self):
        from altaircms.tag.manager import TagManager
        from altaircms.asset.models import FlashAsset
        from altaircms.tag import models as m
        return TagManager(Object=FlashAsset, XRef=m.AssetTag2Asset, Tag=m.AssetTag)

    def test_empty(self):
        self.assertEquals(self._makeOne().search("foo").count(), 0)

    def test_search_by_label(self):
        session = self._getSession()

        obj = self._makeSearchedObj(filepath=u"page")
        obj.tags.append(self._makeTag(label=u"foo"))
        session.add(obj)

        target = self._makeOne()
        self.assertEquals(target.search(u"foo").count(), 1)
        self.assertEquals(target.search(u"boo").count(), 0)

    def test_search_by_public_status(self):
        session = self._getSession()

        obj = self._makeSearchedObj(filepath=u"page")
        obj.tags.append(self._makeTag(label=u"public", publicp=True))
        obj.tags.append(self._makeTag(label=u"private", publicp=False))
        session.add(obj)

        target = self._makeOne()
        self.assertEquals(target.search(u"public").count(), 1)
        self.assertEquals(target.public_search(u"public").count(), 1)
        self.assertEquals(target.private_search(u"public").count(), 0)

        self.assertEquals(target.search(u"private").count(), 1)
        self.assertEquals(target.public_search(u"private").count(), 0)
        self.assertEquals(target.private_search(u"private").count(), 1)

    
if __name__ == "__main__":
    import altaircms.page.models
    import altaircms.event.models
    import altaircms.asset.models
    import altaircms.tag.models
    from altaircms.lib.testutils import db_initialize_for_unittest
    db_initialize_for_unittest()
