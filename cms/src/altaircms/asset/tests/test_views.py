import unittest
import sqlahelper
from pyramid import testing
from altaircms.testing import dummy_form_factory

SuccessForm = dummy_form_factory(name="SuccessForm", validate=True)
FailForm = dummy_form_factory(name="FailForm", validate=False, 
                              errors={"error0": "error-occured!"})

def attach_method(obj, name, method):
    from types import MethodType
    setattr(obj, name, MethodType(method, obj, obj.__class__))
    return obj

def withDB(obj, flush=False):
    session = sqlahelper.get_session()
    session.add(obj)
    if flush:
        session.flush()
    return obj
    
class AssetViewTestBase(unittest.TestCase):
    def setUp(self):
        settings={}
        self.config = testing.setUp(settings=settings)

    def tearDown(self):
        import transaction
        testing.tearDown()
        transaction.abort()

class AssetCreateViewTests(AssetViewTestBase):
    def _getTarget(self):
        from altaircms.asset import views
        return views.AssetCreateView

    def _makeOne(self, request):
        return self._getTarget()(request)

    def test_create_image_asset_invalid(self):
        self.config.add_route('asset_image_list', '/this-is-asset-image-list')

        request = testing.DummyRequest()

        class DummyContext(object):
            forms = testing.DummyResource(ImageAssetForm=FailForm)
            storepath = "."
            def __init__(self, request):
                self.request = request
                self._asset = "asset-is-not-found"


        request.context = DummyContext(request)

        target = self._makeOne(request)
        result = target.create_image_asset()

        self.assertEquals(result.location, '/this-is-asset-image-list')
        self.assertEquals(request.context._asset, "asset-is-not-found")

    def test_create_image_asset(self):
        self.config.add_route('asset_image_list', '/this-is-asset-image-list')

        _asset = object()
        class DummyContext(object):
            forms = testing.DummyResource(ImageAssetForm=SuccessForm)
            def __init__(self, request):
                self.request = request
                self._asset = "asset-is-not-found"

            def create_image_asset(self, form):
                return _asset
            
            def add(self, asset):
                self._asset = asset
                self.called = "add"

        request = testing.DummyRequest()
        request.context = DummyContext(request)
        target = self._makeOne(request)
        result = target.create_image_asset()
        
        self.assertEqual(result.location, '/this-is-asset-image-list')
        self.assertEqual(request.context._asset, _asset)
        self.assertEqual(request.context.called, "add")

    def test_create_movie_asset_invalid(self):
        self.config.add_route('asset_movie_list', '/this-is-asset-movie-list')

        class DummyContext(object):
            forms = testing.DummyResource(MovieAssetForm=FailForm)
            storepath = "."
            def __init__(self, request):
                self.request = request
                self._asset = "asset-is-not-found"

        request = testing.DummyRequest()
        request.context = DummyContext(request)

        target = self._makeOne(request)
        result = target.create_movie_asset()

        self.assertEquals(result.location, '/this-is-asset-movie-list')
        self.assertEquals(request.context._asset, "asset-is-not-found")

    def test_create_movie_asset(self):
        self.config.add_route('asset_movie_list', '/this-is-asset-movie-list')

        _asset = object()
        class DummyContext(object):
            forms = testing.DummyResource(MovieAssetForm=SuccessForm)
            def __init__(self, request):
                self.request = request
                self._asset = "asset-is-not-found"

            def create_movie_asset(self, form):
                return _asset
            
            def add(self, asset):
                self._asset = asset
                self.called = "add"

        request = testing.DummyRequest()
        request.context = DummyContext(request)
        target = self._makeOne(request)
        result = target.create_movie_asset()
        
        self.assertEqual(result.location, '/this-is-asset-movie-list')
        self.assertEqual(request.context._asset, _asset)
        self.assertEqual(request.context.called, "add")

    def test_create_flash_asset_invalid(self):
        self.config.add_route('asset_flash_list', '/this-is-asset-flash-list')

        class DummyContext(object):
            forms = testing.DummyResource(FlashAssetForm=FailForm)
            storepath = "."
            def __init__(self, request):
                self.request = request
                self._asset = "asset-is-not-found"


        request = testing.DummyRequest()
        request.context = DummyContext(request)

        target = self._makeOne(request)
        result = target.create_flash_asset()

        self.assertEquals(result.location, '/this-is-asset-flash-list')
        self.assertEquals(request.context._asset, "asset-is-not-found")

    def test_create_flash_asset(self):
        self.config.add_route('asset_flash_list', '/this-is-asset-flash-list')

        _asset = object()
        class DummyContext(object):
            forms = testing.DummyResource(FlashAssetForm=SuccessForm)
            def __init__(self, request):
                self.request = request
                self._asset = "asset-is-not-found"

            def create_flash_asset(self, form):
                return _asset
            
            def add(self, asset):
                self._asset = asset
                self.called = "add"

        request = testing.DummyRequest()
        request.context = DummyContext(request)
        target = self._makeOne(request)
        result = target.create_flash_asset()
        
        self.assertEqual(result.location, '/this-is-asset-flash-list')
        self.assertEqual(request.context._asset, _asset)
        self.assertEqual(request.context.called, "add")
        
    
class AssetUpdateViewTests(AssetViewTestBase):
    def _getTarget(self):
        from altaircms.asset import views
        return views.AssetUpdateView

    def _makeOne(self, request):
        return self._getTarget()(request)

    def test_update_image_asset(self):
        self.config.add_route('asset_image_detail', '/image-detail/{asset_id}')
        _updated = testing.DummyResource(id=1)
        _created = object()
        assertion = self

        class DummyContext(object):
            forms = testing.DummyResource(ImageAssetUpdateForm=SuccessForm)
            storepath = "."
            def __init__(self, request):
                self.request = request
                self._asset = "asset-is-not-found"
            
            def update_image_asset(self, asset, form):
                assertion.assertEquals(asset, _created)
                return _updated

            def get_image_asset(self, asset_id):
                self._asset = _created
                return self._asset
            
            def add(self, asset):
                self._asset = asset
                self.called = "add"

        request = testing.DummyRequest(matchdict=dict(asset_id=1))
        request.context = DummyContext(request)
        target = self._makeOne(request)
        result = target.update_image_asset()

        self.assertEquals(result.location, "/image-detail/1")
        self.assertEquals(request.context._asset, _updated)
        self.assertNotEquals(request.context._asset, _created)
        self.assertEqual(request.context.called, "add")

    def test_update_image_asset_invalid_filepath(self):
        self.config.add_route('asset_image_input', '/image-input/{asset_id}')
        _created = testing.DummyResource(id=100)

        class DummyContext(object):
            forms = testing.DummyResource(ImageAssetUpdateForm=FailForm)
            storepath = "."
            def __init__(self, request):
                self.request = request
                self._asset = "asset-is-not-found"

            def get_image_asset(self, asset_id):
                self._asset = _created
                return self._asset

        request = testing.DummyRequest(matchdict=dict(asset_id=100))
        request.context = DummyContext(request)
        target = self._makeOne(request)
        result = target.update_image_asset()

        result = self._makeOne(request).update_image_asset()
        self.assertEquals(result.location, "/image-input/100")

    def test_update_movie_asset(self):
        self.config.add_route('asset_movie_detail', '/movie-detail/{asset_id}')
        _created = object()
        _updated = testing.DummyResource(id=1)
        assertion = self

        class DummyContext(object):
            forms = testing.DummyResource(MovieAssetUpdateForm=SuccessForm)
            storepath = "."
            def __init__(self, request):
                self.request = request
                self._asset = "asset-is-not-found"
            
            def update_movie_asset(self, asset, form):
                assertion.assertEquals(asset, _created)
                return _updated

            def get_movie_asset(self, asset_id):
                self._asset = _created
                return self._asset
            
            def add(self, asset):
                self._asset = asset
                self.called = "add"

        request = testing.DummyRequest(matchdict=dict(asset_id=1))
        request.context = DummyContext(request)
        target = self._makeOne(request)
        result = target.update_movie_asset()

        self.assertEquals(result.location, "/movie-detail/1")
        self.assertEquals(request.context._asset, _updated)
        self.assertNotEquals(request.context._asset, _created)
        self.assertEqual(request.context.called, "add")

    def test_update_movie_asset_invalid_filepath(self):
        self.config.add_route('asset_movie_input', '/movie-input/{asset_id}')
        _created = testing.DummyResource(id=100)

        class DummyContext(object):
            forms = testing.DummyResource(MovieAssetUpdateForm=FailForm)
            storepath = "."
            def __init__(self, request):
                self.request = request
                self._asset = "asset-is-not-found"

            def get_movie_asset(self, asset_id):
                self._asset = _created
                return self._asset
           

        request = testing.DummyRequest(matchdict=dict(asset_id=100))
        request.context = DummyContext(request)
        target = self._makeOne(request)
        result = target.update_movie_asset()

        result = self._makeOne(request).update_movie_asset()
        self.assertEquals(result.location, "/movie-input/100")

    def test_update_flash_asset(self):
        self.config.add_route('asset_flash_detail', '/flash-detail/{asset_id}')
        _updated = testing.DummyResource(id=1)
        _created = object()
        assertion = self

        class DummyContext(object):
            forms = testing.DummyResource(FlashAssetUpdateForm=SuccessForm)
            storepath = "."
            def __init__(self, request):
                self.request = request
                self._asset = "asset-is-not-found"
            
            def update_flash_asset(self, asset, form):
                assertion.assertEquals(asset, _created)
                return _updated

            def get_flash_asset(self, asset_id):
                self._asset = _created
                return self._asset
            
            def add(self, asset):
                self._asset = asset
                self.called = "add"

        request = testing.DummyRequest(matchdict=dict(asset_id=1))
        request.context = DummyContext(request)
        target = self._makeOne(request)
        result = target.update_flash_asset()

        self.assertEquals(result.location, "/flash-detail/1")
        self.assertEquals(request.context._asset, _updated)
        self.assertNotEquals(request.context._asset, _created)
        self.assertEqual(request.context.called, "add")

    def test_update_flash_asset_invalid_filepath(self):
        self.config.add_route('asset_flash_input', '/flash-input/{asset_id}')
        _created = testing.DummyResource(id=100)

        class DummyContext(object):
            forms = testing.DummyResource(FlashAssetUpdateForm=FailForm)
            storepath = "."
            def __init__(self, request):
                self.request = request
                self._asset = "asset-is-not-found"

            def get_flash_asset(self, asset_id):
                self._asset = _created
                return self._asset

        request = testing.DummyRequest(matchdict=dict(asset_id=100))
        request.context = DummyContext(request)
        target = self._makeOne(request)
        result = target.update_flash_asset()

        self.assertEquals(result.location, "/flash-input/100")
        self.assertEquals(request.context._asset, _created)

class AssetListViewTests(AssetViewTestBase):
    def _getTarget(self):
        from altaircms.asset import views
        return views.AssetListView

    def _makeOne(self, request):
        return self._getTarget()(request)

    def test_all_asset_list(self):
        class DummyContext(object):
            def __init__(self, request):
                self.request = request
                self.forms = testing.DummyResource(
                    ImageAssetForm=SuccessForm, 
                    MovieAssetForm=SuccessForm, 
                    FlashAssetForm=SuccessForm)

            def get_assets_all(self):
                return  [object()]

        request = testing.DummyRequest()
        request.context = DummyContext(request)
        
        target = self._makeOne(request)
        result = target.all_asset_list()

        self.assertEquals(sorted(result.keys()), 
                         sorted(["assets", "image_asset_form",
                                 "movie_asset_form", "flash_asset_form"]))

    def test_image_asset_list(self):
        class DummyContext(object):
            def __init__(self, request):
                self.request = request
                self.forms = testing.DummyResource(
                    AssetSearchForm=SuccessForm, 
                    ImageAssetForm=SuccessForm)

            def get_image_assets(self):
                return  [object()]

        request = testing.DummyRequest()
        request.context = DummyContext(request)
        
        target = self._makeOne(request)
        result = target.image_asset_list()

        self.assertEquals(sorted(result.keys()), 
                          sorted(["assets", "form", "search_form"]))

    def test_movie_asset_list(self):
        class DummyContext(object):
            def __init__(self, request):
                self.request = request
                self.forms = testing.DummyResource(
                    MovieAssetForm=SuccessForm)

            def get_movie_assets(self):
                return  [object()]

        request = testing.DummyRequest()
        request.context = DummyContext(request)
        
        target = self._makeOne(request)
        result = target.movie_asset_list()


        self.assertEquals(sorted(result.keys()), 
                         sorted(["assets", "form"]))

    def test_flash_asset_list(self):
        class DummyContext(object):
            def __init__(self, request):
                self.request = request
                self.forms = testing.DummyResource(
                    FlashAssetForm=SuccessForm)

            def get_flash_assets(self):
                return  [object()]

        request = testing.DummyRequest()
        request.context = DummyContext(request)
        
        target = self._makeOne(request)
        result = target.flash_asset_list()

        self.assertEquals(sorted(result.keys()), 
                         sorted(["assets", "form"]))


class AssetDetailViewTests(AssetViewTestBase):
    def _getTarget(self):
        from altaircms.asset import views
        return views.AssetDetailView

    def _makeOne(self, request):
        return self._getTarget()(request)

    def test_image_asset_detail(self):
        class DummyContext(object):
            def __init__(self, request):
                self.request = request
                self.forms = testing.DummyResource(
                    ImageAssetForm=SuccessForm)

            def get_image_asset(self, asset_id):
                return  object()

        request = testing.DummyRequest(matchdict=dict(asset_id=1))
        request.context = DummyContext(request)
        
        target = self._makeOne(request)
        result = target.image_asset_detail()

        self.assertEquals(sorted(result.keys()), sorted(["asset"]))


    def test_movie_asset_detail(self):
        class DummyContext(object):
            def __init__(self, request):
                self.request = request
                self.forms = testing.DummyResource(
                    MovieAssetForm=SuccessForm)

            def get_movie_asset(self, asset_id):
                return  object()

        request = testing.DummyRequest(matchdict=dict(asset_id=1))
        request.context = DummyContext(request)
        
        target = self._makeOne(request)
        result = target.movie_asset_detail()

        self.assertEquals(sorted(result.keys()), sorted(["asset"]))

    def test_flash_asset_detail(self):
        class DummyContext(object):
            def __init__(self, request):
                self.request = request
                self.forms = testing.DummyResource(
                    FlashAssetForm=SuccessForm)

            def get_flash_asset(self, asset_id):
                return  object()

        request = testing.DummyRequest(matchdict=dict(asset_id=1))
        request.context = DummyContext(request)
        
        target = self._makeOne(request)
        result = target.flash_asset_detail()

        self.assertEquals(sorted(result.keys()), sorted(["asset"]))

class AssetInputViewTests(AssetViewTestBase):
    def _getTarget(self):
        from altaircms.asset import views
        return views.AssetInputView

    def _makeOne(self, request):
        return self._getTarget()(request)

    def test_image_asset_input(self):
        class DummyContext(object):
            def __init__(self, request):
                self.request = request
                self.forms = testing.DummyResource(
                    ImageAssetUpdateForm=SuccessForm)

            def get_image_asset(self, asset_id):
                from altaircms.asset.models import ImageAsset
                asset = ImageAsset()
                asset.tags = []
                return  asset

        request = testing.DummyRequest(matchdict=dict(asset_id=1))
        request.context = DummyContext(request)
        
        target = self._makeOne(request)
        result = target.image_asset_input()

        self.assertEquals(sorted(result.keys()), sorted(["asset", "form"]))

    def test_movie_asset_input(self):
        class DummyContext(object):
            def __init__(self, request):
                self.request = request
                self.forms = testing.DummyResource(
                    MovieAssetUpdateForm=SuccessForm)

            def get_movie_asset(self, asset_id):
                from altaircms.asset.models import MovieAsset
                asset = MovieAsset()
                asset.tags = []
                return  asset

        request = testing.DummyRequest(matchdict=dict(asset_id=1))
        request.context = DummyContext(request)
        
        target = self._makeOne(request)
        result = target.movie_asset_input()

        self.assertEquals(sorted(result.keys()), sorted(["asset", "form"]))

    def test_flash_asset_input(self):
        class DummyContext(object):
            def __init__(self, request):
                self.request = request
                self.forms = testing.DummyResource(
                    FlashAssetUpdateForm=SuccessForm)

            def get_flash_asset(self, asset_id):
                from altaircms.asset.models import FlashAsset
                asset = FlashAsset()
                asset.tags = []
                return  asset

        request = testing.DummyRequest(matchdict=dict(asset_id=1))
        request.context = DummyContext(request)
        
        target = self._makeOne(request)
        result = target.flash_asset_input()

        self.assertEquals(sorted(result.keys()), sorted(["asset", "form"]))


class AssetDeleteViewTests(AssetViewTestBase):
    def _getTarget(self):
        from altaircms.asset import views
        return views.AssetDeleteView

    def _makeOne(self, request):
        return self._getTarget()(request)

    def test_image_asset_delete(self):
        self.config.add_route("asset_image_list", "image-asset-list")

        from altaircms.asset.models import ImageAsset
        _deleted = ImageAsset(filepath="/foo/bar.jpg")
        class DummyContext(object):
            def __init__(self, request):
                self.request = request
                self.called = []
            def get_image_asset(self, asset_id):
                return _deleted

            def delete_asset_file(self, asset_id):
                self.called.append("delete_file") 

            def delete(self, obj):
                self._asset = obj
                self.called.append("delete") 

        request = testing.DummyRequest(matchdict=dict(asset_id=1))
        request.context = DummyContext(request)
        
        target = self._makeOne(request)
        result = target.delete_image_asset()

        self.assertEquals(result.location, "/image-asset-list")
        self.assertEquals(request.context.called, ["delete_file", "delete"])
        self.assertEquals(request.context._asset, _deleted)

    def test_image_asset_delete_confirm(self):
        from altaircms.asset.models import ImageAsset
        _deleted = ImageAsset(filepath="/foo/bar.jpg")
        class DummyContext(object):
            def __init__(self, request):
                self.request = request

            def get_image_asset(self, asset_id):
                return _deleted

        request = testing.DummyRequest(matchdict=dict(asset_id=1))
        request.context = DummyContext(request)
        
        target = self._makeOne(request)
        result = target.image_delete_confirm()
        self.assertEquals(result, {"asset": _deleted})

    def test_movie_asset_delete(self):
        self.config.add_route("asset_movie_list", "movie-asset-list")

        from altaircms.asset.models import MovieAsset
        _deleted = MovieAsset(filepath="/foo/bar.jpg")
        class DummyContext(object):
            def __init__(self, request):
                self.request = request
                self.called = []
            def get_movie_asset(self, asset_id):
                return _deleted

            def delete_asset_file(self, asset_id):
                self.called.append("delete_file") 

            def delete(self, obj):
                self._asset = obj
                self.called.append("delete") 

        request = testing.DummyRequest(matchdict=dict(asset_id=1))
        request.context = DummyContext(request)
        
        target = self._makeOne(request)
        result = target.delete_movie_asset()

        self.assertEquals(result.location, "/movie-asset-list")
        self.assertEquals(request.context.called, ["delete_file", "delete"])
        self.assertEquals(request.context._asset, _deleted)

    def test_movie_asset_delete_confirm(self):
        from altaircms.asset.models import MovieAsset
        _deleted = MovieAsset(filepath="/foo/bar.jpg")
        class DummyContext(object):
            def __init__(self, request):
                self.request = request

            def get_movie_asset(self, asset_id):
                return _deleted

        request = testing.DummyRequest(matchdict=dict(asset_id=1))
        request.context = DummyContext(request)
        
        target = self._makeOne(request)
        result = target.movie_delete_confirm()
        self.assertEquals(result, {"asset": _deleted})

    def test_flash_asset_delete(self):
        self.config.add_route("asset_flash_list", "flash-asset-list")

        from altaircms.asset.models import FlashAsset
        _deleted = FlashAsset(filepath="/foo/bar.jpg")
        class DummyContext(object):
            def __init__(self, request):
                self.request = request
                self.called = []
            def get_flash_asset(self, asset_id):
                return _deleted

            def delete_asset_file(self, asset_id):
                self.called.append("delete_file") 

            def delete(self, obj):
                self._asset = obj
                self.called.append("delete") 

        request = testing.DummyRequest(matchdict=dict(asset_id=1))
        request.context = DummyContext(request)
        
        target = self._makeOne(request)
        result = target.delete_flash_asset()

        self.assertEquals(result.location, "/flash-asset-list")
        self.assertEquals(request.context.called, ["delete_file", "delete"])
        self.assertEquals(request.context._asset, _deleted)

    def test_flash_asset_delete_confirm(self):
        from altaircms.asset.models import FlashAsset
        _deleted = FlashAsset(filepath="/foo/bar.jpg")
        class DummyContext(object):
            def __init__(self, request):
                self.request = request

            def get_flash_asset(self, asset_id):
                return _deleted

        request = testing.DummyRequest(matchdict=dict(asset_id=1))
        request.context = DummyContext(request)
        
        target = self._makeOne(request)
        result = target.flash_delete_confirm()
        self.assertEquals(result, {"asset": _deleted})


class AssetDisplayViewTests(AssetViewTestBase):
    def _getTarget(self):
        from altaircms.asset import views
        return views.asset_display

    def test_asset_display_not_found(self):
        from altaircms.asset.models import FlashAsset
        _displayd = FlashAsset(filepath="/foo/bar.swf")
        assertion = self
        class DummyContext(object):
            storepath = "."
            def __init__(self, request):
                self.request = request

            def get_asset(self, asset_id):
                return _displayd

            def display_asset(self, filepath):
                assertion.assertIn(_displayd.filepath, filepath)
                return "this-is-image-file"

        request = testing.DummyRequest(matchdict=dict(asset_id=1))
        request.context = DummyContext(request)
        
        result = self._getTarget()(request)
        self.assertEquals(result.status, "200 OK")
        self.assertEquals(result.content_type, "application/octet-stream")
        self.assertEquals(result.body, "this-is-image-file")
        
if __name__ == "__main__":
    unittest.main()
