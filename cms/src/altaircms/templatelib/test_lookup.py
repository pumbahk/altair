from pyramid import testing
import unittest
from altaircms.templatelib import get_renderer_factory

class FailbackFunctionAdapter(object):
    def __init__(self, fn):
        self.fn = fn
    def from_settings(self, *args, **kwargs):
        return self.fn

class HasFailbackMakoLookupTests(unittest.TestCase):
    settings = {"mako.directories": ["altaircms:templatelib"], 
                "s3.mako.directories": ["altaircms:templatelib"]}
    def setUp(self):
        self.config = testing.setUp(settings=self.settings)
    def tearDown(self):
        testing.tearDown()

    def _createInfo(self, _name, _package=None):
        class info:
            name = _name
            package = _package
            registry = self.config.registry
            settings = self.config.registry.settings
        return info

    def test_with_current_mako_renderer(self):
        from pyramid.mako_templating import PkgResourceTemplateLookup

        info = self._createInfo("altaircms.templatelib:sample.mako")
        factory = get_renderer_factory(self.config, info.name)
        template = factory(info).implementation()

        self.assertTrue(template)
        self.assertTrue(isinstance(template.lookup, PkgResourceTemplateLookup))
        ## as mako.template.TemplateLookup
        info = self._createInfo("sample.mako")
        template = factory(info).implementation()

    def test_as_current_mako_renderer(self):
        from altaircms.templatelib import HasFailbackTemplateLookup
        self.config.registry.settings.update(
            {"s3.mako.failback.lookup": "altaircms.templatelib.DefaultFailbackLookup", 
             "s3.mako.lookup.host": "http://localhost:42452", 
             "s3.mako.renderer.name": ".mako"})
        self.config.include("altaircms.templatelib")

        ## as PkgResourceTemplateLookup
        info = self._createInfo("altaircms.templatelib:sample.mako")
        factory = get_renderer_factory(self.config, info.name)
        template = factory(info).implementation()

        self.assertTrue(template)
        self.assertTrue(isinstance(template.lookup, HasFailbackTemplateLookup))

        ## as mako.template.TemplateLookup
        info = self._createInfo("sample.mako")
        factory = get_renderer_factory(self.config, info.name)
        template = factory(info).implementation()

        self.assertTrue(template)
        self.assertTrue(isinstance(template.lookup, HasFailbackTemplateLookup))

    def test_if_not_found_call_failback(self):
        _marker = object()
        def failback(lookup, uri):
            return _marker

        self.config.registry.settings.update(
            {"s3.mako.failback.lookup": FailbackFunctionAdapter(failback), 
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
            {"s3.mako.failback.lookup": FailbackFunctionAdapter(failback), 
             "s3.mako.renderer.name": ".mako"})
        self.config.include("altaircms.templatelib")

        info = self._createInfo("not found template.mako")
        factory = get_renderer_factory(self.config, info.name)

        from mako.exceptions import TopLevelLookupException
        with self.assertRaises(TopLevelLookupException):
            factory(info).implementation()

if __name__ == "__main__":
    unittest.main()
