from pyramid import testing
import unittest
from altaircms.templatelib import get_renderer_factory
import os

def mako_lookup(request, name=None):
    from pyramid.mako_templating import IMakoLookup
    return request.registry.queryUtility(IMakoLookup, name=name)


_app = None

def run_mock_server(_tmpdir, port=42452):
    global _app
    import threading
    import urllib
    from pyramid.asset import (
        resolve_asset_spec,
        abspath_from_asset_spec,
        )
    from SimpleHTTPServer import SimpleHTTPRequestHandler
    class ExtraHTTPRequestHandler(SimpleHTTPRequestHandler):
        tmpdir = _tmpdir
        def getcwd(self):
            return self.tmpdir

        def translate_path(self, path):
            path = path.split('?',1)[0]
            path = path.split('#',1)[0]
            path = os.path.abspath(urllib.unquote(path))
            words = path.split('/')
            words = filter(None, words)
            path = self.getcwd()
            for word in words:
                drive, word = os.path.splitdrive(word)
                head, word = os.path.split(word)
                if word in (os.curdir, os.pardir):
                    continue
                path = os.path.join(path, word)
            return path

    from BaseHTTPServer import HTTPServer

    server_address = ('0.0.0.0', port)
    SimpleHTTPRequestHandler.protocol_version = "HTTP/1.0"
    _app = httpd = HTTPServer(server_address, ExtraHTTPRequestHandler)

    th = threading.Thread(target=httpd.serve_forever)
    th.daemon = True
    th.start()

## todo: move it. if slow test
class CollectTemplateFromNetworkIntegerationTests(unittest.TestCase):
    port = 42452
    TEMPLATE_SPEC = "altaircms.templatelib:templates"
    SINGLE_TEMPLATE = u"""
hello, this is single template. ${user}
"""
    BASE_TEMPLATE = u"""
header
${next.body()}
footter
"""
    INHERIT_TEMPLATE1 = u"""
<%inherit file="altaircms.templatelib:templates/base.s3mako"/>
body
"""
    INHERIT_TEMPLATE2 = u"""
<%inherit file="./base.s3mako"/>
body
"""
    _HEADER_TEMPLATE = u"""
this-is-header
"""
    _FOOTER_TEMPLATE = u"""
this-is-footer
"""
    INCLUDE_TEMPLATE = u"""
<%include file="_header.s3mako"/>
body
<%include file="altaircms.templatelib:templates/_footer.s3mako"/>
"""

    def fetch(self, path):
        import urllib
        url = "http://localhost:{0}{1}".format(self.port, path)
        return urllib.urlopen(url).read()

    @classmethod
    def setUpClass(cls):
        import tempfile
        import shutil

        template_dir = os.path.join(os.path.dirname(__file__), "templates")
        if os.path.exists(template_dir):
            shutil.rmtree(template_dir)
        os.mkdir(template_dir)

        cls.tmpdir = tempfile.mkdtemp()
        def _fname(fname):
            return os.path.join(cls.tmpdir, cls.TEMPLATE_SPEC, fname)
        os.mkdir(_fname(""))
        with open(_fname("single.s3mako"), "w") as wf:
            wf.write(cls.SINGLE_TEMPLATE)
        with open(_fname("base.s3mako"), "w") as wf:
            wf.write(cls.BASE_TEMPLATE)
        with open(_fname("inherit1.s3mako"), "w") as wf:
            wf.write(cls.INHERIT_TEMPLATE1)
        with open(_fname("inherit2.s3mako"), "w") as wf:
            wf.write(cls.INHERIT_TEMPLATE2)
        with open(_fname("_header.s3mako"), "w") as wf:
            wf.write(cls._HEADER_TEMPLATE)
        with open(_fname("_footer.s3mako"), "w") as wf:
            wf.write(cls._FOOTER_TEMPLATE)
        with open(_fname("include.s3mako"), "w") as wf:
            wf.write(cls.INCLUDE_TEMPLATE)


        run_mock_server(cls.tmpdir, port=cls.port)


        
    def setUp(self):
        settings = {"mako.directories": [self.TEMPLATE_SPEC], 
                    "s3.mako.directories": [self.TEMPLATE_SPEC], 
                    "s3.mako.failback.lookup": "altaircms.templatelib.DefaultFailbackLookup", 
                    "s3.mako.lookup.host": "http://localhost:42452", 
                    "s3.mako.renderer.name": ".s3mako"}
        self.config = testing.setUp(settings=settings)
        self.config.include("altaircms.templatelib")

    def tearDown(self):
        import glob
        from pyramid.path import AssetResolver
        testing.tearDown()
        d = AssetResolver().resolve(self.TEMPLATE_SPEC).abspath()
        for f in glob.glob(os.path.join(d, "*.s3mako")):
            os.remove(f)

    @classmethod
    def tearDownClass(cls):
        import shutil
        global _app
        _app.shutdown()
        shutil.rmtree(cls.tmpdir)

    def test_prepare(self):
        result = self.fetch("/altaircms.templatelib:templates/single.s3mako")
        self.assertEquals(result, self.SINGLE_TEMPLATE)

    def _createInfo(self, _name, _package=None):
        class info:
            name = _name
            package = _package
            registry = self.config.registry
            settings = self.config.registry.settings
        return info

    def _callFUT(self, info, kwargs):
        factory = get_renderer_factory(self.config, info.name)
        template = factory(info).implementation()
        return template.render_unicode(**kwargs).strip()        

    def test_single_assetspec(self):
        info = self._createInfo("altaircms.templatelib:templates/single.s3mako")
        result = self._callFUT(info, {"user": "foo"})
        self.assertEquals(result, u"hello, this is single template. foo")

    def test_single_filename(self):
        info = self._createInfo("single.s3mako")
        result = self._callFUT(info, {"user": "foo"})
        self.assertEquals(result, u"hello, this is single template. foo")

    def test_single_filename2(self):
        info = self._createInfo("./single.s3mako")
        result = self._callFUT(info, {"user": "foo"})
        self.assertEquals(result, u"hello, this is single template. foo")

    def test_single_filename3(self):
        info = self._createInfo("./foo/../single.s3mako")
        result = self._callFUT(info, {"user": "foo"})
        self.assertEquals(result, u"hello, this is single template. foo")

    def test_inherit1(self):
        info = self._createInfo("inherit1.s3mako")
        result = self._callFUT(info, {})
        self.assertEquals(result, u"header\n\n\nbody\n\nfootter")

    def test_inherit2(self):
        info = self._createInfo("inherit2.s3mako")
        result = self._callFUT(info, {})
        self.assertEquals(result, u"header\n\n\nbody\n\nfootter")

    def test_inherit2_assetspec(self):
        info = self._createInfo("altaircms.templatelib:templates/inherit2.s3mako")
        result = self._callFUT(info, {})
        self.assertEquals(result, u"header\n\n\nbody\n\nfootter")

    def test_include(self):
        info = self._createInfo("altaircms.templatelib:templates/include.s3mako")
        result = self._callFUT(info, {})
        self.assertEquals(result, u"this-is-header\n\nbody\n\nthis-is-footer")

        
if __name__ == "__main__":
    unittest.main()
