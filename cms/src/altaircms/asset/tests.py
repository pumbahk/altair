# coding: utf-8
import os
import cgi

from pyramid import testing
from webob.multidict import MultiDict

from altaircms.models import DBSession

from altaircms.base.tests import BaseTest
from altaircms.asset.views import AssetRESTAPIView
from altaircms.asset.models import ImageAsset

"""
browser = None
def setUpModule():
    from selenium import selenium
    global browser
    browser = selenium("localhost", 4444, "*chrome", "http://localhost:8521/")
    browser.start()
    return browser


def tearDownModule():
    browser.stop()

def _getFile(name='test.py'):
    import os
    path = os.path.join(os.path.abspath(os.path.dirname(__file__)), name)
    filename = os.path.split(path)[-1]
    return path, filename
"""

class TestAssetView(BaseTest):
    def setUp(self):
        self.request = testing.DummyRequest()
        super(TestAssetView, self).setUp()

    def tearDown(self):
        import transaction
        transaction.abort()

    def test_create(self):
        # null post
        self.request.POST = MultiDict()

        resp = AssetRESTAPIView(self.request).create()
        self.assertEqual(resp.status_int, 400)
        self.assertTrue(isinstance(resp.message, dict))
        self.assertTrue(resp.message['type'])
        # self.assertTrue(resp.message['uploadfile'])
        self.assertEqual(DBSession.query(ImageAsset).count(), 0)

        # post filled
        self._fill_post_request()

        resp = AssetRESTAPIView(self.request).create()
        self.assertEqual(resp.status_int, 201)
        self.assertTrue(isinstance(resp.content_location, str))
        self.assertEqual(DBSession.query(ImageAsset).count(), 1)

        #@TODO: ファイルの保存確認？

    def test_read(self):
        self._create_imageasset()
        resp = AssetRESTAPIView(self.request, 1).read()

        self.assertEqual(resp.status_int, 200)
        self.assertEqual(resp.body['id'], 1)
        self.assertEqual(resp.body['mimetype'], 'image/jpeg')
        self.assertEqual(resp.body['filepath'], 'hoge.jpg')

    def test_update(self):
        self._create_imageasset()

        image_asset = DBSession.query(ImageAsset).one()
        self.assertEqual(image_asset.filepath, 'hoge.jpg')
        self.assertEqual(image_asset.mimetype, 'image/jpeg')

        # post filled
        self._fill_post_request()


        resp = AssetRESTAPIView(self.request, 1).update()
        image_asset = DBSession.query(ImageAsset).one()
        self.assertEqual(resp.status_int, 200)
        self.assertEqual(image_asset.filepath, 'test.jpg')  # @FIXME: test.jpgに更新されない
        self.assertEqual(image_asset.alt, 'alt text')
        self.assertEqual(image_asset.width, 320)
        self.assertEqual(image_asset.height, 240)

    def test_delete(self):
        self._create_imageasset()

        resp = AssetRESTAPIView(self.request, 1).delete()
        self.assertEqual(resp.status_int, 200)
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

