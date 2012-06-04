import unittest
from pyramid import testing

def _makeOperator(username):
    from altaircms.auth.models import Operator
    return Operator(auth_source="dummy", screen_name=username)

class AssetImageUpdateTests(unittest.TestCase):
    def _getTarget(self):
        from altaircms.asset.resources import AssetResource
        return AssetResource

    def _makeOne(self, request):
        target = self._getTarget()(request)
        target.storepath = "."
        return target

    def _makeAsset(self, *args, **kwargs):
        from altaircms.asset.models import ImageAsset
        return ImageAsset(*args, **kwargs)

    def test_update_asset(self):
        import StringIO
        storage = testing.DummyResource(
            filename="foo.jpg",
            file=StringIO.StringIO('hahaha'))

        operator = _makeOperator("this-is-operator")
        dummy_form = testing.DummyResource(
            data={
                "filepath": storage, 
                "alt": "updated-asset",
                "tags": "", 
                "private_tags": "",
                })

        asset = self._makeAsset()
        request = testing.DummyRequest()
        target = self._makeOne(request)
        result = target.update_image_asset(asset, 
                                           dummy_form,
                                           _write_buf=lambda *args, **kwargs: None,
                                           _get_extra_status=lambda *args: dict(width=300, height=200), 
                                           _put_tags = lambda *args: args, 
                                           _add_operator=lambda asset, r: setattr(asset, "updated_by", operator))
        self.assertEqual(result, asset)
        self.assertEquals(result.updated_by, operator)

        self.assertTrue(".jpg" in result.filepath)

        self.assertEquals(result.mimetype,'image/jpeg')
        self.assertEquals(result.width, 300)
        self.assertEquals(result.height, 200)
        self.assertEquals(result.alt, "updated-asset")

    def test_filepath_is_empty(self):
        dummy_form = testing.DummyResource(
            data={
                "filepath": '',
                "alt": "empty!",
                "tags": "", 
                "private_tags": "",
                })

        asset = self._makeAsset(filepath="this-is-asset-filepath")

        request = testing.DummyRequest()
        target = self._makeOne(request)
        operator = _makeOperator("this-is-operator")

        result = target.update_image_asset(
            asset, 
            dummy_form, 
            _write_buf=lambda *args, **kwargs: None,
            _get_extra_status=lambda *args: dict(width=300, height=200), 
            _put_tags = lambda *args: args, 
            _add_operator=lambda asset, r: setattr(asset, "updated_by", operator))

        self.assertEqual(result, asset)
        self.assertEquals(result.updated_by, operator)
        self.assertEqual(result.filepath, 'this-is-asset-filepath')
        self.assertEquals(result.alt, "empty!")


class AssetMovieUpdateTests(unittest.TestCase):
    def _getTarget(self):
        from altaircms.asset.resources import AssetResource
        return AssetResource

    def _makeOne(self, request):
        target = self._getTarget()(request)
        target.storepath = "."
        return target

    def _makeAsset(self, *args, **kwargs):
        from altaircms.asset.models import MovieAsset
        return MovieAsset(*args, **kwargs)

    def test_update_asset(self):
        import StringIO
        storage = testing.DummyResource(
            filename="foo.mp4",
            file=StringIO.StringIO('hahaha'))

        dummy_form = testing.DummyResource(
            data={
                "filepath": storage, 
                "alt": "updated-asset",
                "tags": "", 
                "private_tags": "",
                })
        operator = _makeOperator("this-is-operator")

        asset = self._makeAsset()
        request = testing.DummyRequest()
        target = self._makeOne(request)
        result = target.update_movie_asset(asset, 
                                           dummy_form,
                                           _write_buf=lambda *args, **kwargs: None,
                                           _get_extra_status=lambda *args: dict(width=300, height=200), 
                                           _put_tags = lambda *args: args, 
                                           _add_operator=lambda asset, r: setattr(asset, "updated_by", operator))
        self.assertEqual(result, asset)

        self.assertTrue(".mp4" in result.filepath)

        self.assertEquals(result.mimetype,'video/mp4')
        self.assertEquals(result.width, 300)
        self.assertEquals(result.height, 200)
        self.assertEquals(result.alt, "updated-asset")

    def test_filepath_is_empty(self):
        dummy_form = testing.DummyResource(
            data={
                "filepath": '',
                "alt": "empty!",
                "tags": "", 
                "private_tags": "",
                })
        operator = _makeOperator("this-is-operator")

        asset = self._makeAsset(filepath="this-is-asset-filepath")
        request = testing.DummyRequest()
        target = self._makeOne(request)

        result = target.update_movie_asset(
            asset, 
            dummy_form, 
            _write_buf=lambda *args, **kwargs: None,
            _get_extra_status=lambda *args: dict(width=300, height=200), 
            _put_tags = lambda *args: args, 
            _add_operator=lambda asset, r: setattr(asset, "updated_by", operator))

        self.assertEqual(result, asset)
        self.assertEqual(result.filepath, 'this-is-asset-filepath')
        self.assertEquals(result.alt, "empty!")

class AssetFlashUpdateTests(unittest.TestCase):
    def _getTarget(self):
        from altaircms.asset.resources import AssetResource
        return AssetResource

    def _makeOne(self, request):
        target = self._getTarget()(request)
        target.storepath = "."
        return target

    def _makeAsset(self, *args, **kwargs):
        from altaircms.asset.models import FlashAsset
        return FlashAsset(*args, **kwargs)

    def test_update_asset(self):
        import StringIO
        storage = testing.DummyResource(
            filename="foo.swf",
            file=StringIO.StringIO('hahaha'))

        dummy_form = testing.DummyResource(
            data={
                "filepath": storage, 
                "alt": "updated-asset",
                "tags": "", 
                "private_tags": "",
                })

        operator = _makeOperator("this-is-operator")

        asset = self._makeAsset()
        request = testing.DummyRequest()
        target = self._makeOne(request)
        result = target.update_flash_asset(asset, 
                                           dummy_form,
                                           _write_buf=lambda *args, **kwargs: None,
                                           _get_extra_status=lambda *args: dict(width=300, height=200), 
                                           _put_tags = lambda *args: args, 
                                           _add_operator=lambda asset, r: setattr(asset, "updated_by", operator))
        self.assertEqual(result, asset)

        self.assertTrue(".swf" in result.filepath)

        self.assertEquals(result.mimetype,'application/x-shockwave-flash')
        self.assertEquals(result.width, 300)
        self.assertEquals(result.height, 200)
        self.assertEquals(result.alt, "updated-asset")

    def test_filepath_is_empty(self):
        dummy_form = testing.DummyResource(
            data={
                "filepath": '',
                "alt": "empty!",
                "tags": "", 
                "private_tags": "",
                })

        asset = self._makeAsset(filepath="this-is-asset-filepath")
        operator = _makeOperator("this-is-operator")

        request = testing.DummyRequest()
        target = self._makeOne(request)

        result = target.update_flash_asset(
            asset, 
            dummy_form, 
            _write_buf=lambda *args, **kwargs: None,
            _get_extra_status=lambda *args: dict(width=300, height=200), 
            _put_tags = lambda *args: args, 
            _add_operator=lambda asset, r: setattr(asset, "updated_by", operator))

        self.assertEqual(result, asset)
        self.assertEqual(result.filepath, 'this-is-asset-filepath')
        self.assertEquals(result.alt, "empty!")

