import unittest
from pyramid import testing
from pyramid.util import InstancePropertyMixin

class DummyRequest(testing.DummyRequest, InstancePropertyMixin):
    pass

def makeRequest(config):
    from pyramid.events import NewRequest
    request = DummyRequest()
    request.environ = {}
    config.registry.notify(NewRequest(request))
    return request

class IntegrationTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.config.include("altair.cdnpath")

    def tearDown(self):
        testing.tearDown()

    def test_directive(self):
        self.assertTrue(self.config.add_cdn_static_path)

    def test_static_url(self):
        from . import S3StaticPathFactory
        factory = S3StaticPathFactory(":bucket-name:")
        self.config.add_cdn_static_path(factory)
        self.config.add_static_view("static", path="altair.cdnpath:static")

        request = makeRequest(self.config)
        self.assertEquals(request.static_url("altair.cdnpath:static/foo.txt"),
                          "http://:bucket-name:.s3.amazonaws.com/static/foo.txt")

    def test_static_url_same_scheme(self):
        from . import S3StaticPathFactory
        factory = S3StaticPathFactory(":bucket-name:")
        self.config.add_cdn_static_path(factory)
        self.config.add_static_view("static", path="altair.cdnpath:static")

        request = makeRequest(self.config)
        request.environ["wsgi.url_scheme"] = "https"
        self.assertEquals(request.static_url("altair.cdnpath:static/foo.txt"),
                          "https://:bucket-name:.s3.amazonaws.com/static/foo.txt")
        

    def test_with_exclude(self):
        from . import S3StaticPathFactory
        factory = S3StaticPathFactory(":bucket-name:", exclude=lambda path: path.endswith(".js"))

        self.config.add_cdn_static_path(factory)
        self.config.add_static_view("static", path="altair.cdnpath:static")

        request = makeRequest(self.config)
        self.assertEquals(request.static_url("altair.cdnpath:static/foo.js", _app_url="http://foo.bar.jp"),
                          "http://foo.bar.jp/static/foo.js")
        self.assertEquals(request.static_url("altair.cdnpath:static/foo.txt", _app_url="http://foo.bar.jp"),
                          "http://:bucket-name:.s3.amazonaws.com/static/foo.txt")
        
    
