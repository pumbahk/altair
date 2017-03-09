import unittest
from pyramid import testing
from pyramid.util import InstancePropertyMixin
from pyramid.exceptions import ConfigurationError

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

    def test_validate(self):
        from . import PrefixedStaticURLInfo
        info = PrefixedStaticURLInfo("prefix")
        try:
            info.validate()
        except ConfigurationError:
            pass
        self.assertTrue(True)

    def test_directive(self):
        self.assertTrue(self.config.add_cdn_static_path)

    def test_static_url(self):
        from . import S3StaticPathFactory
        factory = S3StaticPathFactory(":bucket-name:")
        self.config.add_cdn_static_path(factory)
        self.config.add_static_view("static", path="altair.cdnpath:static")

        request = makeRequest(self.config)
        self.assertEquals(request.static_url("altair.cdnpath:static/foo.txt"),
                          "//:bucket-name:.s3.amazonaws.com/static/foo.txt")

    def test_static_url_same_scheme(self):
        from . import S3StaticPathFactory
        factory = S3StaticPathFactory(":bucket-name:")
        self.config.add_cdn_static_path(factory)
        self.config.add_static_view("static", path="altair.cdnpath:static")

        request = makeRequest(self.config)
        request.environ["wsgi.url_scheme"] = "https"
        self.assertEquals(request.static_url("altair.cdnpath:static/foo.txt"),
                          "//:bucket-name:.s3.amazonaws.com/static/foo.txt")
        

    def test_with_exclude(self):
        from . import S3StaticPathFactory
        factory = S3StaticPathFactory(":bucket-name:", exclude=lambda path: path.endswith(".js"))

        self.config.add_cdn_static_path(factory)
        self.config.add_static_view("static", path="altair.cdnpath:static")

        request = makeRequest(self.config)
        self.assertEquals(request.static_url("altair.cdnpath:static/foo.js", _app_url="http://foo.bar.jp"),
                          "//foo.bar.jp/static/foo.js")
        self.assertEquals(request.static_url("altair.cdnpath:static/foo.txt", _app_url="http://foo.bar.jp"),
                          "//:bucket-name:.s3.amazonaws.com/static/foo.txt")
        
    def test_get_correct_prefix(self):
        from . import S3StaticPathFactory
        factory = S3StaticPathFactory(":bucket-name:")
        prefix = factory._get_correct_prefix("/prefix")
        self.assertEqual(prefix, "/prefix")
