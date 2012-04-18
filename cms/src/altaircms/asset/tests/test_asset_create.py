import unittest
import pyramid.testing as testing

def _makeOperator(username):
    from altaircms.auth.models import Operator
    return Operator(auth_source="dummy", screen_name=username)

class AssetCreateTests(unittest.TestCase):
    def _getTarget(self):
        from altaircms.asset.resources import AssetResource
        return AssetResource

    def _makeOne(self, request):
        return self._getTarget()(request)

    def test_create_image_asset_in_resource(self):
        import StringIO
        storage = testing.DummyResource(filename="foo.jpg", 
                                        file=StringIO.StringIO("hahah"))
        data = {"filepath": storage, 
                "alt": "create-asset", 
                "tags": "", 
                "private_tags": ""}

        dummy_form = testing.DummyResource(data=data)
        operator = _makeOperator("this-is-operator")
        request = testing.DummyRequest()
        target = self._makeOne(request)
        target.storepath = "."

        result = target.create_image_asset(
            dummy_form, 
             _write_buf=lambda *args, **kwargs: setattr(dummy_form, "writedp", True), 
             _get_extra_status=lambda *args: dict(width=300, height=200), 
             _put_tags = lambda *args: args, 
            _add_operator = lambda asset, r: setattr(asset, "created_by", operator)
            )

        self.assertEquals(result.discriminator,"image" )
        self.assertTrue(".jpg" in result.filepath)

        self.assertEquals(result.mimetype,'image/jpeg')
        self.assertEquals(result.width, 300)
        self.assertEquals(result.height, 200)
        self.assertEquals(result.alt, "create-asset")

    def test_create_movie_asset_in_resource(self):
        import StringIO
        storage = testing.DummyResource(filename="foo.mp4", 
                                        file=StringIO.StringIO("hahah"))
        data = {"filepath": storage, 
                "alt": "create-asset", 
                "tags": "", 
                "private_tags": ""}

        dummy_form = testing.DummyResource(data=data)
        request = testing.DummyRequest()
        target = self._makeOne(request)
        target.storepath = "."

        result = target.create_movie_asset(
            dummy_form, 
             _write_buf=lambda *args, **kwargs: setattr(dummy_form, "writedp", True), 
             _get_extra_status=lambda *args: dict(width=300, height=200), 
             _put_tags = lambda *args: args
            )

        self.assertEquals(result.discriminator,"movie" )
        self.assertTrue(".mp4" in result.filepath)

        self.assertEquals(result.mimetype,'video/mp4')
        self.assertEquals(result.width, 300)
        self.assertEquals(result.height, 200)
        self.assertEquals(result.alt, "create-asset")

    def test_create_flash_asset_in_resource(self):
        import StringIO
        storage = testing.DummyResource(filename="foo.swf", 
                                        file=StringIO.StringIO("hahah"))
        data = {"filepath": storage, 
                "alt": "create-asset", 
                "tags": "", 
                "private_tags": ""}

        dummy_form = testing.DummyResource(data=data)
        request = testing.DummyRequest()
        target = self._makeOne(request)
        target.storepath = "."

        result = target.create_flash_asset(
            dummy_form, 
             _write_buf=lambda *args, **kwargs: setattr(dummy_form, "writedp", True), 
             _get_extra_status=lambda *args: dict(width=300, height=200), 
             _put_tags = lambda *args: args
            )

        self.assertEquals(result.discriminator,"flash" )
        self.assertTrue(".swf" in result.filepath)

        self.assertEquals(result.mimetype,'application/x-shockwave-flash')
        self.assertEquals(result.width, 300)
        self.assertEquals(result.height, 200)
        self.assertEquals(result.alt, "create-asset")

