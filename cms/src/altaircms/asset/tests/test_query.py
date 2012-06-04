# -*- coding:utf-8 -*-
import unittest


def _withDB(o, flush=False):
    from altaircms.models import DBSession
    DBSession.add(o)
    if flush:
        DBSession.flush()
    return o

def _makeOperator(params, flush=False):
    from altaircms.auth.models import Operator
    return _withDB(Operator(**params), flush=flush)

def _makeAsset(model, params, flush=False):
    return _withDB(model(**params), flush=flush)

class AssetSearchQueryTest(unittest.TestCase):
    def tearDown(self):
        import transaction
        transaction.abort()

    def _getTarget(self):
        from altaircms.asset.resources import AssetResource
        return AssetResource

    def _makeOne(self):
        return self._getTarget()(None)

    def test_search_image_asset_empty_params(self):
        from altaircms.asset.models import ImageAsset

        user = _makeOperator({"auth_source": "this-is-auth-source"}, flush=True)

        other_asset = _makeAsset(ImageAsset, {})
        updated_asset = _makeAsset(ImageAsset, {"updated_by": user})
        created_asset = _makeAsset(ImageAsset, {"created_by": user})
        both_asset = _makeAsset(ImageAsset, {"updated_by": user, "created_by": user})

        target = self._makeOne()
        result = target.search_image_asset_by_query({}, 
                                           lambda p : ImageAsset.query)
        self.assertEquals(list(result.all()), [other_asset, updated_asset, created_asset, both_asset])

    def test_search_image_asset_created_by(self):
        from altaircms.asset.models import ImageAsset

        user = _makeOperator({"auth_source": "this-is-auth-source"}, flush=True)

        other_asset = _makeAsset(ImageAsset, {})
        updated_asset = _makeAsset(ImageAsset, {"updated_by": user})
        created_asset = _makeAsset(ImageAsset, {"created_by": user})
        both_asset = _makeAsset(ImageAsset, {"updated_by": user, "created_by": user})

        target = self._makeOne()
        result = target.search_image_asset_by_query({"created_by": user}, 
                                           lambda p : ImageAsset.query)
        self.assertEquals(list(result.all()), [created_asset, both_asset])

    def test_search_image_asset_updated_by(self):
        from altaircms.asset.models import ImageAsset

        user = _makeOperator({"auth_source": "this-is-auth-source"}, flush=True)

        other_asset = _makeAsset(ImageAsset, {})
        updated_asset = _makeAsset(ImageAsset, {"updated_by": user})
        created_asset = _makeAsset(ImageAsset, {"created_by": user})
        both_asset = _makeAsset(ImageAsset, {"updated_by": user, "created_by": user})

        target = self._makeOne()
        result = target.search_image_asset_by_query({"updated_by": user}, 
                                           lambda p : ImageAsset.query)
        self.assertEquals(list(result.all()), [updated_asset, both_asset])

    def test_search_image_asset_created_and_updated_by(self):
        from altaircms.asset.models import ImageAsset

        user = _makeOperator({"auth_source": "this-is-auth-source"}, flush=True)
        other_asset = _makeAsset(ImageAsset, {})
        updated_asset = _makeAsset(ImageAsset, {"updated_by": user})
        created_asset = _makeAsset(ImageAsset, {"created_by": user})
        both_asset = _makeAsset(ImageAsset, {"updated_by": user, "created_by": user})

        target = self._makeOne()
        result = target.search_image_asset_by_query({"updated_by": user, 
                                                     "created_by": user}, 
                                           lambda p : ImageAsset.query)
        self.assertEquals(list(result.all()), [both_asset])


class AssetQueryTests(unittest.TestCase):
    def tearDown(self):
        import transaction
        transaction.abort()

    def _getTarget(self):
        from altaircms.asset.resources import AssetResource
        return AssetResource

    def _makeOne(self):
        return self._getTarget()(None)

    def test_query_all(self):
        from altaircms.asset.models import Asset
        _makeAsset(Asset, {"discriminator": "image"})
        _makeAsset(Asset, {"discriminator": "movie"})
        _makeAsset(Asset, {"discriminator": "flash"})

        qs = self._makeOne().get_assets_all()
        self.assertEquals(qs.count(), 3)

    def test_query_image(self):
        from altaircms.asset.models import (ImageAsset, FlashAsset, MovieAsset)
        _makeAsset(ImageAsset, {})
        _makeAsset(FlashAsset, {})
        _makeAsset(MovieAsset, {})

        qs = self._makeOne().get_image_assets()
        self.assertEquals(qs.count(), 1)

    def test_query_movie(self):
        from altaircms.asset.models import (ImageAsset, FlashAsset, MovieAsset)
        _makeAsset(ImageAsset, {})
        _makeAsset(FlashAsset, {})
        _makeAsset(MovieAsset, {})

        qs = self._makeOne().get_movie_assets()
        self.assertEquals(qs.count(), 1)

    def test_query_flash(self):
        from altaircms.asset.models import (ImageAsset, FlashAsset, MovieAsset)
        _makeAsset(ImageAsset, {})
        _makeAsset(FlashAsset, {})
        _makeAsset(MovieAsset, {})

        qs = self._makeOne().get_flash_assets()
        self.assertEquals(qs.count(), 1)

class AssetGetOneTests(unittest.TestCase):
    def tearDown(self):
        import transaction
        transaction.abort()

    def _getTarget(self):
        from altaircms.asset.resources import AssetResource
        return AssetResource

    def _makeOne(self):
        return self._getTarget()(None)

    def test_get_anything_asset(self):
        from altaircms.asset.models import ImageAsset
        target = _makeAsset(ImageAsset, {}, flush=True)

        result = self._makeOne().get_asset(target.id)
        self.assertEquals(result.discriminator, "image")

    def test_query_image(self):
        from altaircms.asset.models import (ImageAsset, FlashAsset, MovieAsset)
        target = _makeAsset(ImageAsset, {})
        _makeAsset(FlashAsset, {})
        _makeAsset(MovieAsset, {}, flush=True)

        result = self._makeOne().get_image_asset(target.id)
        self.assertEquals(result.discriminator, "image")

    def test_query_movie(self):
        from altaircms.asset.models import (ImageAsset, FlashAsset, MovieAsset)
        _makeAsset(ImageAsset, {})
        _makeAsset(FlashAsset, {})
        target = _makeAsset(MovieAsset, {}, flush=True)


        result = self._makeOne().get_movie_asset(target.id)
        self.assertEquals(result.discriminator, "movie")

    def test_query_flash(self):
        from altaircms.asset.models import (ImageAsset, FlashAsset, MovieAsset)
        _makeAsset(ImageAsset, {})
        target = _makeAsset(FlashAsset, {})
        _makeAsset(MovieAsset, {}, flush=True)

        result = self._makeOne().get_flash_asset(target.id)
        self.assertEquals(result.discriminator, "flash")
