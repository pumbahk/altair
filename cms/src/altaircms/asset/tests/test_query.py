# -*- coding:utf-8 -*-
import unittest

class AssetQueryTests(unittest.TestCase):
    def tearDown(self):
        import transaction
        transaction.abort()

    def _getTarget(self):
        from altaircms.asset.resources import AssetResource
        return AssetResource(None)

    def _withDB(self, o):
        from altaircms.models import DBSession
        DBSession.add(o)
        return o

    def _makeAsset(self, model, params):
        return self._withDB(model(**params))

    def test_query_all(self):
        from altaircms.asset.models import Asset
        self._makeAsset(Asset, {"discriminator": "image"})
        self._makeAsset(Asset, {"discriminator": "movie"})
        self._makeAsset(Asset, {"discriminator": "flash"})

        qs = self._getTarget().get_assets_all()
        self.assertEquals(qs.count(), 3)

    def test_query_image(self):
        from altaircms.asset.models import (ImageAsset, FlashAsset, MovieAsset)
        self._makeAsset(ImageAsset, {})
        self._makeAsset(FlashAsset, {})
        self._makeAsset(MovieAsset, {})

        qs = self._getTarget().get_image_assets()
        self.assertEquals(qs.count(), 1)

    def test_query_movie(self):
        from altaircms.asset.models import (ImageAsset, FlashAsset, MovieAsset)
        self._makeAsset(ImageAsset, {})
        self._makeAsset(FlashAsset, {})
        self._makeAsset(MovieAsset, {})

        qs = self._getTarget().get_movie_assets()
        self.assertEquals(qs.count(), 1)

    def test_query_flash(self):
        from altaircms.asset.models import (ImageAsset, FlashAsset, MovieAsset)
        self._makeAsset(ImageAsset, {})
        self._makeAsset(FlashAsset, {})
        self._makeAsset(MovieAsset, {})

        qs = self._getTarget().get_flash_assets()
        self.assertEquals(qs.count(), 1)

class AssetGetOneTests(unittest.TestCase):
    def tearDown(self):
        import transaction
        transaction.abort()

    def _getTarget(self):
        from altaircms.asset.resources import AssetResource
        return AssetResource(None)
    
    def _withDB(self, o, flush=False):
        from altaircms.models import DBSession
        DBSession.add(o)
        if flush:
            DBSession.flush()
        return o

    def _makeAsset(self, model, params, flush=False):
        return self._withDB(model(**params), flush=flush)

    def test_get_anything_asset(self):
        from altaircms.asset.models import ImageAsset
        target = self._makeAsset(ImageAsset, {}, flush=True)

        result = self._getTarget().get_asset(target.id)
        self.assertEquals(result.discriminator, "image")

    def test_query_image(self):
        from altaircms.asset.models import (ImageAsset, FlashAsset, MovieAsset)
        target = self._makeAsset(ImageAsset, {})
        self._makeAsset(FlashAsset, {})
        self._makeAsset(MovieAsset, {}, flush=True)

        result = self._getTarget().get_image_asset(target.id)
        self.assertEquals(result.discriminator, "image")

    def test_query_movie(self):
        from altaircms.asset.models import (ImageAsset, FlashAsset, MovieAsset)
        self._makeAsset(ImageAsset, {})
        self._makeAsset(FlashAsset, {})
        target = self._makeAsset(MovieAsset, {}, flush=True)


        result = self._getTarget().get_movie_asset(target.id)
        self.assertEquals(result.discriminator, "movie")

    def test_query_flash(self):
        from altaircms.asset.models import (ImageAsset, FlashAsset, MovieAsset)
        self._makeAsset(ImageAsset, {})
        target = self._makeAsset(FlashAsset, {})
        self._makeAsset(MovieAsset, {}, flush=True)

        result = self._getTarget().get_flash_asset(target.id)
        self.assertEquals(result.discriminator, "flash")
