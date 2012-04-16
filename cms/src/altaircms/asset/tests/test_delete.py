import unittest
from pyramid import testing

class DeleteFileDummy(object):
    def __init__(self):
        self.deleted = None

    def __call__(self, path):
        self.deleted = path

class AssetDeleteTests(unittest.TestCase):
    def _getTarget(self):
        from altaircms.asset.resources import AssetResource
        return AssetResource

    def _makeOne(self, request):
        return self._getTarget()(request)

    def test_delete_image_asset(self):
        from altaircms.asset.models import ImageAsset
        asset = ImageAsset(filepath="foo.jpg")
        delete_file_dummy = DeleteFileDummy()        

        target = self._makeOne(testing.DummyRequest())
        target.storepath = "."
        target.delete_asset_file(asset, delete_file_dummy)

        self.assertEquals(delete_file_dummy.deleted, "./foo.jpg")
