import unittest
    
class PageSearchTest(unittest.TestCase):
    def tearDown(self):
        import transaction
        transaction.abort()

    def _getSession(self):
        from altaircms.models import DBSession
        return DBSession

    def _makeTarget(self, **kwargs):
        from altaircms.page.models import Page
        return Page(**kwargs)

    def _makeTag(self, **kwargs):
        from altaircms.tag.models import PageTag
        return PageTag(**kwargs)

    def _getManger(self):
        from altaircms.tag.manager import TagManager
        return TagManager.page()

    def test_empty(self):
        manager = self._getManger()
        self.assertEquals(manager.search(u"foo").count(), 
                         0)

    def test_matched(self):
        session = self._getSession()
        target = self._makeTarget(title=u"page")
        target.tags.append(self._makeTag(label=u"foo"))
        session.add(target)
        manager = self._getManger()
        self.assertEquals(manager.search(u"foo").count(), 
                         1)
        self.assertEquals(manager.search(u"boo").count(), 
                          0)

class EventSearchTest(unittest.TestCase):
    def tearDown(self):
        import transaction
        transaction.abort()

    def _getSession(self):
        from altaircms.models import DBSession
        return DBSession

    def _makeTarget(self, **kwargs):
        from altaircms.event.models import Event
        return Event(**kwargs)

    def _makeTag(self, **kwargs):
        from altaircms.tag.models import EventTag
        return EventTag(**kwargs)

    def _getManger(self):
        from altaircms.tag.manager import TagManager
        return TagManager.event()

    def test_empty(self):
        manager = self._getManger()
        self.assertEquals(manager.search(u"foo").count(), 
                         0)

    def test_matched(self):
        session = self._getSession()
        target = self._makeTarget(title=u"event")
        target.tags.append(self._makeTag(label=u"foo"))
        session.add(target)
        manager = self._getManger()
        self.assertEquals(manager.search(u"foo").count(), 
                         1)
        self.assertEquals(manager.search(u"boo").count(), 
                          0)


class ImageAssetSearchTest(unittest.TestCase):
    def tearDown(self):
        import transaction
        transaction.abort()

    def _getSession(self):
        from altaircms.models import DBSession
        return DBSession

    def _makeTarget(self, **kwargs):
        from altaircms.asset.models import ImageAsset
        return ImageAsset(**kwargs)


    def _makeTag(self, **kwargs):
        from altaircms.tag.models import ImageAssetTag
        return ImageAssetTag(**kwargs)

    def _getManger(self):
        from altaircms.tag.manager import TagManager
        return TagManager.image_asset()

    def test_empty(self):
        manager = self._getManger()
        self.assertEquals(manager.search(u"foo").count(), 
                         0)

    def test_matched(self):
        session = self._getSession()
        target = self._makeTarget(filepath=u"asset")
        target.tags.append(self._makeTag(label=u"foo"))
        session.add(target)
        manager = self._getManger()
        self.assertEquals(manager.search(u"foo").count(), 
                          1)
        self.assertEquals(manager.search(u"boo").count(), 
                          0)

class MovieAssetSearchTest(unittest.TestCase):
    def tearDown(self):
        import transaction
        transaction.abort()

    def _getSession(self):
        from altaircms.models import DBSession
        return DBSession

    def _makeTarget(self, **kwargs):
        from altaircms.asset.models import MovieAsset
        return MovieAsset(**kwargs)


    def _makeTag(self, **kwargs):
        from altaircms.tag.models import MovieAssetTag
        return MovieAssetTag(**kwargs)

    def _getManger(self):
        from altaircms.tag.manager import TagManager
        return TagManager.movie_asset()

    def test_empty(self):
        manager = self._getManger()
        self.assertEquals(manager.search(u"foo").count(), 
                         0)

    def test_matched(self):
        session = self._getSession()
        target = self._makeTarget(filepath=u"asset")
        target.tags.append(self._makeTag(label=u"foo"))
        session.add(target)
        manager = self._getManger()
        self.assertEquals(manager.search(u"foo").count(), 
                          1)
        self.assertEquals(manager.search(u"boo").count(), 
                          0)

class FlashAssetSearchTest(unittest.TestCase):
    def tearDown(self):
        import transaction
        transaction.abort()

    def _getSession(self):
        from altaircms.models import DBSession
        return DBSession

    def _makeTarget(self, **kwargs):
        from altaircms.asset.models import FlashAsset
        return FlashAsset(**kwargs)


    def _makeTag(self, **kwargs):
        from altaircms.tag.models import FlashAssetTag
        return FlashAssetTag(**kwargs)

    def _getManger(self):
        from altaircms.tag.manager import TagManager
        return TagManager.flash_asset()

    def test_empty(self):
        manager = self._getManger()
        self.assertEquals(manager.search(u"foo").count(), 
                         0)

    def test_matched(self):
        session = self._getSession()
        target = self._makeTarget(filepath=u"asset")
        target.tags.append(self._makeTag(label=u"foo"))
        session.add(target)
        manager = self._getManger()
        self.assertEquals(manager.search(u"foo").count(), 
                          1)
        self.assertEquals(manager.search(u"boo").count(), 
                          0)

class AnyKindAssetSearchTests(unittest.TestCase):
    def tearDown(self):
        import transaction
        transaction.abort()

    def _getSession(self):
        from altaircms.models import DBSession
        return DBSession

    def _makeImageAsset(self, **kwargs):
        from altaircms.asset.models import ImageAsset
        return ImageAsset(**kwargs)
    def _makeFlashAsset(self, **kwargs):
        from altaircms.asset.models import FlashAsset
        return FlashAsset(**kwargs)
    def _makeMovieAsset(self, **kwargs):
        from altaircms.asset.models import MovieAsset
        return MovieAsset(**kwargs)

    def _makeTag(self, **kwargs):
        from altaircms.tag.models import AssetTag
        return AssetTag(**kwargs)

    def _getMangerClass(self):
        from altaircms.tag.manager import TagManager
        return TagManager

    def test_any_kind(self):
        """ search image. flash, movie asset exist in session"""
        session = self._getSession()
        flash = self._makeFlashAsset(filepath=u"asset")
        flash.tags.append(self._makeTag(label=u"foo", discriminator="flash"))
        session.add(flash)

        movie = self._makeMovieAsset(filepath=u"asset")
        movie.tags.append(self._makeTag(label=u"foo", discriminator="movie"))
        session.add(movie)

        manager = self._getMangerClass().image_asset()
        self.assertEquals(manager.search(u"foo").count(), 
                          0)
        manager = self._getMangerClass().movie_asset()
        self.assertEquals(manager.search(u"foo").count(), 
                          1)
        manager = self._getMangerClass().flash_asset()
        self.assertEquals(manager.search(u"foo").count(), 
                          1)

        manager = self._getMangerClass().page()
        self.assertEquals(manager.search(u"foo").count(), 
                          0)
        manager = self._getMangerClass().event()
        self.assertEquals(manager.search(u"foo").count(), 
                          0)
    
if __name__ == "__main__":
    config  = None
    def setUpModule():
        global config
        from altaircms.lib import testutils
        config = testutils.config()
        config.scan("altaircms.page.models")
        config.scan("altaircms.event.models")
        config.scan("altaircms.asset.models")
        config.scan("altaircms.tag.models")
        testutils.create_db(force=False)

        # from altaircms.lib.dbinspect import listing_all
        # from altaircms.models import Base
        # listing_all(Base.metadata)

    unittest.main()
