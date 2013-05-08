import unittest
from pyramid import testing
from pyramid.util import InstancePropertyMixin

class DummyRequest(testing.DummyRequest, InstancePropertyMixin):
    pass

def makeRequest(config):
    from pyramid.events import NewRequest
    request = DummyRequest()
    config.registry.notify(NewRequest(request))
    return request

class IntegrationTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.config.include("altair.cdnpath")
        self.config.add_static_view("static", path="altair.cdnpath:static")

    def test_directive(self):
        self.assertTrue(self.config.add_cdn_static_path)

    def test_property(self):
        from . import S3StaticPathFactory
        factory = S3StaticPathFactory(":bucket-name:")
        self.config.add_cdn_static_path(factory)

        request = makeRequest(self.config)

        self.assertTrue(request.cdn.static_url)
        self.assertEquals(request.cdn, request.cdn) #cached?

    def test_static_url(self):
        from . import S3StaticPathFactory
        factory = S3StaticPathFactory(":bucket-name:")
        self.config.add_cdn_static_path(factory)

        request = makeRequest(self.config)

        self.assertEquals(request.cdn.static_url("altair.cdnpath:static/foo.txt"),
                          "http://:bucket-name:.s3.amazonaws.com/static/foo.txt")

        self.assertEquals(request.cdn.static_url("/static/foo.txt"),
                          "http://:bucket-name:.s3.amazonaws.com/static/foo.txt")

        
    def tearDown(self):
        testing.tearDown()

