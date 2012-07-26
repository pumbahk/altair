import unittest
config  = None
def setUpModule():
    from altaircms.testing import setup_db
    setup_db(["altaircms.page.models", 
              "altaircms.tag.models", 
              "altaircms.event.models", 
              "altaircms.asset.models"])

    global config
    from altaircms import testing as mytesting
    config = mytesting.config()
    config.include("altaircms.tag")
    mytesting.setup_db(["altaircms.page.models", "altaircms.tag.models", "altaircms.event.models", "altaircms.asset.models"])
    
def tearDownModule():
    from altaircms.testing import teardown_db
    teardown_db()

    from pyramid.testing import tearDown
    tearDown()

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

    def _makeOne(self, classifier):
        from altaircms.tag.api import get_tagmanager
        return get_tagmanager(classifier)

    def test_any_kind(self):
        """ search_by_tag_label image. flash, movie asset exist in session"""
        session = self._getSession()
        flash = self._makeFlashAsset(filepath=u"asset")
        flash.tags.append(self._makeTag(label=u"foo", discriminator="flash"))
        session.add(flash)

        movie = self._makeMovieAsset(filepath=u"asset")
        movie.tags.append(self._makeTag(label=u"foo", discriminator="movie"))
        session.add(movie)

        target = self._makeOne("image_asset")
        self.assertEquals(target.search_by_tag_label(u"foo").count(), 
                          0)
        target = self._makeOne("movie_asset")
        self.assertEquals(target.search_by_tag_label(u"foo").count(), 
                          1)
        target = self._makeOne("flash_asset")
        self.assertEquals(target.search_by_tag_label(u"foo").count(), 
                          1)

        target = self._makeOne("page")
        self.assertEquals(target.search_by_tag_label(u"foo").count(), 
                          0)

if __name__ == "__main__":
    unittest.main()
