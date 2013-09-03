import unittest
import mock
from pyramid.testing import DummyResource

def mktime(h, m, s):
    import time
    return time.mktime((2013,8,23,h,m,s,4,235,0))

def mkdatetime(h, m, s):
    from datetime import datetime
    return datetime(2013, 8, 23, h, m, s, 0)
    
class HandlerTest(unittest.TestCase):
    def _getTarget(self):
        from altairsite.front.renderer import LayoutModelLookupInterceptHandler
        return LayoutModelLookupInterceptHandler

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_need_intercept(self):
        layout_uploaded_at = mkdatetime(13, 0, 0)
        layout_spec = "altaircms:templates/front/layout"
        target = self._makeOne(None, layout_spec, layout_uploaded_at, None)

        self.assertTrue(target.need_intercept("altaircms:templates/front/layout/RT/index.html"))
        self.assertFalse(target.need_intercept("altaircms:templates/front/index.html"))
        self.assertFalse(target.need_intercept("/front/index.html"))

    def test_need_intercept__if_uploaded_at_is_None(self):
        layout_spec = "altaircms:templates/front/layout"
        target = self._makeOne(None, layout_spec, None, None)

        self.assertFalse(target.need_intercept("altaircms:templates/front/layout/RT/index.html"))
        self.assertFalse(target.need_intercept("altaircms:templates/front/index.html"))
        self.assertFalse(target.need_intercept("/front/index.html"))


    def test_need_refresh(self):
        layout_uploaded_at = mkdatetime(13, 0, 0)
        target = self._makeOne(None, None, layout_uploaded_at, None)

        self.assertTrue(target.need_refresh(mktime(12, 0, 0)))
        self.assertFalse(target.need_refresh(mktime(14, 0, 0)))

    def test_need_refresh__if_modifled_None(self):
        target = self._makeOne(None, None, None, None)
        self.assertFalse(target.need_refresh(None))


    def test_normalize_for_key(self):
        layout_uploaded_at = mkdatetime(13, 0, 0)
        target = self._makeOne(None, None, layout_uploaded_at, None)
        
        self.assertEquals(target.normalize_for_key("/front/index.html"), 
                          "/front/index.html@20130823130000")
        self.assertEquals(target.normalize_for_key("altaircms:front/layout/RT/index.html"),
                          "altaircms$front/layout/RT/index.html@20130823130000")

    def test_normalize_for_key__uploaded_at_is_None(self):
        target = self._makeOne(None, None, None, None)
        
        self.assertEquals(target.normalize_for_key("/front/index.html"),
                          "/front/index.html")
        self.assertEquals(target.normalize_for_key("altaircms:front/layout/RT/index.html"),
                          "altaircms$front/layout/RT/index.html")

    def test_build_url(self):
        prefix = "cms-layout-templates"
        layout_spec = "altaircms:templates/front/layout"
        target = self._makeOne(prefix, layout_spec, None, None)
        
        name = "altaircms:templates/front/layout/RT/index.html"
        result = target.build_url(name)
        self.assertEquals(result, "cms-layout-templates/RT/index.html")
        

    def test_load_template(self):
        prefix = "cms-layout-templates"
        layout_spec = "altaircms:templates/front/layout"

        def dummy_loader(key):
            self.assertEquals(key, "cms-layout-templates/RT/index.html")
            return "ok:${status}"

        target = self._makeOne(prefix, layout_spec, None, dummy_loader)
        lookup=DummyResource(template_args={})
        name = "altaircms:templates/front/layout/RT/index.html"
        uri = "altaircms:templates$front/layout/RT/index.html@2013081312"
        result = target.load_template(lookup, name, uri, None)

        self.assertEquals(result.render(status=200), "ok:200")

    def test_load_template__error(self):
        prefix = "cms-layout-templates"
        layout_spec = "altaircms:templates/front/layout"

        def dummy_loader(key):
            raise Exception("ng")
        
        target = self._makeOne(prefix, layout_spec, None, dummy_loader)
        lookup=DummyResource(template_args={})
        name = "altaircms:templates/front/layout/RT/index.html"
        uri = "altaircms:templates$front/layout/RT/index.html@2013081312"
        from pyramid.httpexceptions import HTTPNotFound
        with self.assertRaises(HTTPNotFound):
            target.load_template(lookup, name, uri, dummy_loader)


class LookupWrapperTest(unittest.TestCase):
    layout_spec = "altaircms:templates/front/layout/RT/index.html"
    def _getTarget(self):
        from altairsite.front.renderer import LookupInterceptWrapper
        return LookupInterceptWrapper
    
    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_get_template__need_intercept__false__call_original_lookup(self):
        class lookup:
            called = False
            @classmethod
            def get_template(cls, uri):
                cls.called = True
                return uri

        handler = DummyResource(need_intercept=(lambda uri: False))

        target = self._makeOne(lookup, handler)
        result = target.get_template(self.layout_spec)

        self.assertEqual(result, self.layout_spec)
        self.assertTrue(lookup.called)

    @mock.patch("altairsite.front.renderer.LookupInterceptWrapper._load")
    def test_get_template__first_call__filesystem_checks__load_is_called(self, m):
        class lookup:
            _collection = {}
            filesystem_checks = True

        handler = DummyResource(need_intercept=(lambda uri: True), 
                                normalize_for_key=(lambda s : ":template:"),
                                )
        target = self._makeOne(lookup, handler)
        result = target.get_template(self.layout_spec)

        m.assert_called_once_with(self.layout_spec, ":template:")
        self.assertEquals(result, m())

    @mock.patch("altairsite.front.renderer.LookupInterceptWrapper._check")
    def test_get_template__exists__filesystem_checks__check_is_called(self, m):
        class lookup:
            _collection = {":template:": "exist"}
            filesystem_checks = True

        handler = DummyResource(need_intercept=(lambda uri: True), 
                                normalize_for_key=(lambda s : ":template:"),
                                )
        target = self._makeOne(lookup, handler)
        result = target.get_template(self.layout_spec)

        m.assert_called_once_with(":template:", "exist")
        self.assertEquals(result, m())

    def test_get_template__exists__nocheck__check_is_called(self):
        class lookup:
            _collection = {":template:": "already exist"}
            filesystem_checks = False

        handler = DummyResource(need_intercept=(lambda uri: True), 
                                normalize_for_key=(lambda s : ":template:"),
                                )
        target = self._makeOne(lookup, handler)
        result = target.get_template(self.layout_spec)
        
        self.assertEquals(result, "already exist")

# move?
class IntegrationTest(unittest.TestCase):
    layout_spec = "altaircms:templates/front/layout/RT/index.html"
    adjusted = "altaircms$templates/front/layout/RT/index.html"

    def _makeOne(self, *args, **kwargs):
        from altairsite.front.renderer import LookupInterceptWrapper
        return LookupInterceptWrapper(*args, **kwargs)

    def _getHandler(self, expected_url, response_message=":response-message:"):
        from altairsite.front.renderer import LayoutModelLookupInterceptHandler
        prefix = "cms-layout-templates"
        layout_spec = "altaircms:templates/front/layout"
        uploaded_at = mkdatetime(10, 0, 0)
        def dummy_loader(url):
            if url == expected_url:
                return response_message
            raise Exception
        return LayoutModelLookupInterceptHandler(prefix, layout_spec, uploaded_at, dummy_loader)


    def test_first_call__load_template__from_external_resource(self):
        from mako.lookup import TemplateLookup
        lookup = TemplateLookup()

        handler = self._getHandler(expected_url="cms-layout-templates/RT/index.html", response_message=":external-resource:")
        target = self._makeOne(lookup, handler)
        result = target.get_template(self.layout_spec)
        self.assertEquals(result.render(), ":external-resource:")

    @mock.patch("mako.lookup.TemplateLookup.get_template")
    def test_first_call__not_layout_spec__use_original_lookup(self, m):
        from mako.lookup import TemplateLookup
        lookup = TemplateLookup()
        
        handler = self._getHandler(expected_url="cms-layout-templates/RT/index.html", response_message=":external-resource:")
        target = self._makeOne(lookup, handler)

        result = target.get_template("altaircms:templates/another/foo.html")

        m.assert_called_once_with("altaircms:templates/another/foo.html")
        self.assertEqual(result, m())
        
    @mock.patch("mako.lookup.TemplateLookup.get_template")
    def test_first_call__without_uploaded_at__use_original_lookup(self, m):
        from mako.lookup import TemplateLookup
        lookup = TemplateLookup()

        handler = self._getHandler(expected_url="cms-layout-templates/RT/index.html", response_message=":external-resource:")
        handler.uploaded_at = None
        target = self._makeOne(lookup, handler)

        result = target.get_template(self.layout_spec)

        m.assert_called_once_with(self.layout_spec)
        self.assertEqual(result, m())

    def test_second_call__using_cache(self):
        from mako.lookup import TemplateLookup
        lookup = TemplateLookup()
       
        handler = self._getHandler(expected_url="cms-layout-templates/RT/index.html", response_message=":external-resource:")
        target = self._makeOne(lookup, handler)

        ## put cache(as called once).
        lookup.put_string(handler.normalize_for_key(self.layout_spec), ":cached:")

        result = target.get_template(self.layout_spec)

        self.assertEquals(result.render(), ":cached:")

    @mock.patch("mako.lookup.TemplateLookup.get_template")
    def test_second_call__without_uploaded_at__use_original_lookup(self, m):
        from mako.lookup import TemplateLookup
        lookup = TemplateLookup()
        
        handler = self._getHandler(expected_url="cms-layout-templates/RT/index.html", response_message=":external-resource:")
        handler.uploaded_at = None
        target = self._makeOne(lookup, handler)

        ## put cache(as called once).
        lookup.put_string(handler.normalize_for_key(self.layout_spec), ":cached:")

        result = target.get_template(self.layout_spec)

        m.assert_called_once_with(self.layout_spec)
        self.assertEqual(result, m())


    def test_second_call__cache_is_older__load_template__from_external_resource(self):
        from mako.lookup import TemplateLookup
        lookup = TemplateLookup()
        
        handler = self._getHandler(expected_url="cms-layout-templates/RT/index.html", response_message=":external-resource:")
        handler.uploaded_at = None
        target = self._makeOne(lookup, handler)

        ## put cache(as called once).
        kname = handler.normalize_for_key(self.layout_spec)
        lookup.put_string(kname, ":cached:")

        ## hack
        lookup.get_template(kname).module._modified_time = mktime(10, 0, 0)
        handler.uploaded_at = mkdatetime(12, 0, 0)
        self.assertEquals(lookup.get_template(kname).last_modified, mktime(10, 0, 0))
        self.assertTrue(handler.need_refresh(lookup.get_template(kname).last_modified))
        ##

        result = target.get_template(self.layout_spec)
        self.assertEqual(result.render(), ":external-resource:")


if __name__ == "__main__":
    unittest.main()

