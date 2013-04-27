from pyramid import testing
import unittest
import os

def mako_lookup(request, name=None):
    from pyramid.mako_templating import IMakoLookup
    return request.registry.queryUtility(IMakoLookup, name=name)

def get_renderer_factory(request, filename):
    from pyramid.interfaces import IRendererFactory
    ext = os.path.splitext(filename)[1]
    return request.registry.queryUtility(IRendererFactory, name=ext)

class TestBase(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp(settings={"mako.directories": ["altaircms:tests"], 
                                              "s3.mako.directories": ["altaircms:tests"]})
    def tearDown(self):
        testing.tearDown()

class HasFailbackMakoLookupTests(TestBase):
    def _createInfo(self, _name, _package=None):
        class info:
            name = _name
            package = _package
            registry = self.config.registry
            settings = self.config.registry.settings
        return info

    def test_with_current_mako_renderer(self):
        from pyramid.mako_templating import PkgResourceTemplateLookup

        info = self._createInfo("altaircms.tests:templates/single.mako")
        factory = get_renderer_factory(self.config, info.name)
        template = factory(info).implementation()

        self.assertTrue(template)
        self.assertTrue(isinstance(template.lookup, PkgResourceTemplateLookup))
        ## as mako.template.TemplateLookup
        info = self._createInfo("templates/single.mako")
        template = factory(info).implementation()

    def test_as_current_mako_renderer(self):
        from altaircms.templatelib import HasFailbackTemplateLookup
        self.config.registry.settings.update(
            {"s3.mako.failback.lookup": "altaircms.templatelib.default_failback_lookup", 
             "s3.mako.renderer.name": ".mako"})
        self.config.include("altaircms.templatelib")

        ## as PkgResourceTemplateLookup
        info = self._createInfo("altaircms.tests:templates/single.mako")
        factory = get_renderer_factory(self.config, info.name)
        template = factory(info).implementation()

        self.assertTrue(template)
        self.assertTrue(isinstance(template.lookup, HasFailbackTemplateLookup))

        ## as mako.template.TemplateLookup
        info = self._createInfo("templates/single.mako")
        factory = get_renderer_factory(self.config, info.name)
        template = factory(info).implementation()

        self.assertTrue(template)
        self.assertTrue(isinstance(template.lookup, HasFailbackTemplateLookup))

    def test_if_not_found_call_failback(self):
        _marker = object()
        def failback(lookup, uri):
            return _marker

        self.config.registry.settings.update(
            {"s3.mako.failback.lookup": failback, 
             "s3.mako.renderer.name": ".mako"})
        self.config.include("altaircms.templatelib")

        info = self._createInfo("not found template.mako")
        factory = get_renderer_factory(self.config, info.name)
        template = factory(info).implementation()

        self.assertEquals(template, _marker)

    def test_failback_occur_exception(self):
        class MyException(Exception):
            pass

        def failback(lookup, unri):
            raise MyException("failback is failure. anything wrong?")

        self.config.registry.settings.update(
            {"s3.mako.failback.lookup": failback, 
             "s3.mako.renderer.name": ".mako"})
        self.config.include("altaircms.templatelib")

        info = self._createInfo("not found template.mako")
        factory = get_renderer_factory(self.config, info.name)

        from mako.exceptions import TopLevelLookupException
        with self.assertRaises(TopLevelLookupException):
            factory(info).implementation()

_app = None
def run_mock_server(port=42452):
    global _app
    import threading
    from SimpleHTTPServer import SimpleHTTPRequestHandler
    from BaseHTTPServer import HTTPServer

    server_address = ('0.0.0.0', port)
    SimpleHTTPRequestHandler.protocol_version = "HTTP/1.0"
    _app = httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)

    th = threading.Thread(target=httpd.serve_forever)
    th.daemon = True
    th.start()

## todo: move it. if slow test
class CollectTemplateFromNetworkIntegerationTests(TestBase):
    port = 42452
    def fetch(self, path):
        import urllib
        url = "http://localhost:{0}{1}".format(self.port, path)
        return urllib.urlopen(url).read()

    @classmethod
    def setUpClass(cls):
        run_mock_server(port=cls.port)
        
    @classmethod
    def tearDownClass(cls):
        global _app
        _app.shutdown()

    def test_prepare(self):
        self.assertTrue(self.fetch("/templates/single.mako"))


if __name__ == "__main__":
    unittest.main()
