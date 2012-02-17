# coding: utf-8
import os
import cgi

from pyramid import testing

from altaircms.tests import BaseTest
from altaircms.asset.views import AssetRESTAPIView


"""
class TestAssetView(BaseTest):
    def setUp(self):
        self.request = testing.DummyRequest()
        super(TestAssetView, self).setUp()

    def _makeOne(self, tmpstore, **kw):
        from deform.widget import FileUploadWidget
        return FileUploadWidget(tmpstore, **kw)

    def test_create(self):
        self.request.POST = {}

        resp = AssetRESTAPIView(self.request).create()
        self.assertEqual(resp.status_int, 400)
        self.assertTrue(isinstance(resp.message, dict))
        self.assertEqual(resp.message['type'], 'Required')
        self.assertEqual(resp.message['uploadfile'], 'Required')

        upload = DummyUpload()
        upload = cgi.FieldStorage(fp=DummyUpload())
        self.request.POST = {
            'type': 'image',
            'uploadfile': upload,
            'submit': 'submit',
        }

        resp = AssetRESTAPIView(self.request).create()
        self.assertEqual(resp.status_int, 201)
        self.assertTrue(isinstance(resp.message, dict))
"""


# code from https://github.com/Pylons/deform/blob/master/deform/tests/test_widget.py
class DummyTmpStore(dict):
    def preview_url(self, uid):
        return 'preview_url'


class DummyUpload(dict):
    def __init__(self):
        self['file'] = open(os.path.join(os.path.dirname(__file__), 'test.jpg'), 'rb')
        self['filename'] = 'filename'
        self['type'] = 'mimetype'
        self['length'] = 'size'
        # upload = 'hogehoge'
        # uid = 1234


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