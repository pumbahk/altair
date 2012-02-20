# coding: utf-8
import os
import cgi

from pyramid import testing
from webob.multidict import MultiDict

from altaircms.tests import BaseTest
from altaircms.asset.views import AssetRESTAPIView

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
"""

def _getFile(name='test.py'):
    import os
    path = os.path.join(os.path.abspath(os.path.dirname(__file__)), name)
    filename = os.path.split(path)[-1]
    return path, filename

class TestAssetView(BaseTest):
    def setUp(self):
        self.request = testing.DummyRequest()
        #setUpModule()

        super(TestAssetView, self).setUp()

    def tearDown(self):
        #tearDownModule()
        pass

    def _makeOne(self, tmpstore, **kw):
        from deform.widget import FileUploadWidget
        return FileUploadWidget(tmpstore, **kw)

    def test_create(self):
        self.request.POST = {}

        # null post
        resp = AssetRESTAPIView(self.request).create()
        self.assertEqual(resp.status_int, 400)
        self.assertTrue(isinstance(resp.message, dict))
        self.assertEqual(resp.message['type'], 'Required')
        self.assertEqual(resp.message['uploadfile'], 'Required')

        # post filled
        upload = cgi.FieldStorage(u'Binaries--file', u'test.js')

        self.request.POST = MultiDict([
            (u'_charset_', u'UTF-8'),
            (u'__formid__', u'deform'),
            (u'type', u'image'),
            (u'alt', u'alt text'),
            (u'width', u'320'),
            (u'height', u'240'),
            (u'__start__', u'uploadfile:mapping'),
            (u'upload', upload),
            (u'__end__', 'uploadfile:mapping'),
            (u'submit', u'submit')
        ])

        resp = AssetRESTAPIView(self.request).create()
        self.assertEqual(resp.status_int, 201)
        self.assertTrue(isinstance(resp.content_location, str))


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