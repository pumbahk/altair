# coding: utf-8
import os
import cgi
import transaction

from pyramid import testing
from webob.multidict import MultiDict

from altaircms.models import DBSession
from altaircms.lib.testutils import BaseTest
from altaircms.asset.views import AssetRESTAPIView
from altaircms.asset.models import Asset, ImageAsset


class TestAssetView(BaseTest):
    def setUp(self):
        self.request = testing.DummyRequest()
        super(TestAssetView, self).setUp()

    def tearDown(self):
        transaction.commit()

    def test_create(self):
        # null post
        self.request.POST = MultiDict()

        (created, object, errors) = AssetRESTAPIView(self.request).create()
        self.assertFalse(created)
        self.assertEqual(object, None)
        self.assertTrue(errors['type'])
        self.assertEqual(DBSession.query(ImageAsset).count(), 0)

        # post filled
        self._fill_post_request()

        (created, object, errors) = AssetRESTAPIView(self.request).create()
        self.assertTrue(created)
        self.assertTrue(isinstance(object, ImageAsset))
        self.assertEqual(DBSession.query(ImageAsset).count(), 1)

        #@TODO: ファイルの保存確認？

    def test_read(self):
        self._create_imageasset()
        resp = AssetRESTAPIView(self.request, 1).read()

        self.assertTrue(isinstance(resp, dict))
        self.assertEqual(resp['id'], 1)
        self.assertEqual(resp['mimetype'], 'image/jpeg')
        self.assertEqual(resp['filepath'], 'hoge.jpg')

    def test_update(self):
        self._create_imageasset()

        image_asset = DBSession.query(ImageAsset).one()
        self.assertEqual(image_asset.filepath, 'hoge.jpg')
        self.assertEqual(image_asset.mimetype, 'image/jpeg')

        # post filled
        self._fill_post_request()


        (status, image_asset, errors) = AssetRESTAPIView(self.request, 1).update()
        self.assertTrue(status)
        self.assertEqual(image_asset.filepath, 'test.jpg')  # @FIXME: test.jpgに更新されない
        self.assertEqual(image_asset.alt, 'alt text')
        self.assertEqual(image_asset.width, 320)
        self.assertEqual(image_asset.height, 240)

    def test_delete(self):
        self._create_imageasset()

        resp = AssetRESTAPIView(self.request, 1).delete()
        self.assertTrue(resp)
        self.assertEqual(DBSession.query(ImageAsset).count(), 0)

    def _create_imageasset(self):
        obj = ImageAsset()
        obj.filepath = 'hoge.jpg'
        obj.mimetype = 'image/jpeg'

        DBSession.add(obj)

    def _fill_post_request(self):
        upload = DummyUpload()

        self.request.POST = MultiDict([
            (u'type', u'image'),
            (u'alt', u'alt text'),
            (u'width', u'320'),
            (u'height', u'240'),
            (u'filepath', upload['filename']),
            (u'submit', u'submit')
        ])
        self.request.FILES = MultiDict([
            (u'filepath', upload)
        ])


# code from https://github.com/Pylons/deform/blob/master/deform/tests/test_widget.py
class DummyTmpStore(dict):
    def preview_url(self, uid):
        return 'preview_url'


class DummyUpload(dict):
    def __init__(self):
        self['file'] = open(os.path.join(os.path.dirname(__file__), 'test.jpg'), 'rb')
        self['filename'] = 'test.jpg'
        self['type'] = 'mimetype'
        self['length'] = 'size'


def _cgi_FieldStorage__repr__patch(self):
    """ monkey patch for FieldStorage.__repr__

    Unbelievably, the default __repr__ on FieldStorage reads
    the entire file content instead of being sane about it.
    This is a simple replacement that doesn't do that
    """
    if self.file:
        return "FieldStorage(%r, %r)" % (self.name, self.filename)
    return "FieldStorage(%r, %r, %r)" % (self.name, self.filename, self.value)

cgi.FieldStorage.__repr__ = _cgi_FieldStorage__repr__patch

if __name__ == "__main__":
    import unittest
    unittest.main()

