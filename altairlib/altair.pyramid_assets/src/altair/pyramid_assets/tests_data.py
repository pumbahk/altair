from unittest import TestCase

class DataSchemeAssetDescriptorTest(TestCase):
    def _makeTarget(self, *args, **kwargs):
        from .data import DataSchemeAssetDescriptor
        return DataSchemeAssetDescriptor(*args, **kwargs)

    def test_absspec(self):
        self.assertEquals(self._makeTarget('test', 'text/plain', [('charset', 'utf-8')], None).absspec(), "data:text/plain;charset=utf-8,test")
        self.assertEquals(self._makeTarget('test', 'text/plain', [('charset', 'utf-8')], 'base64').absspec(), "data:text/plain;charset=utf-8;base64,dGVzdA%3D%3D")
        self.assertEquals(self._makeTarget('test', 'text/plain', [('foo', '"bar')], None).absspec(), 'data:text/plain;foo="\\"bar",test')

    def test_stream(self):
        target = self._makeTarget('test', 'text/plain', [('charset', 'utf-8')], None)
        self.assertEquals(target.stream().read(), "test")

    def test_isdir(self):
        target = self._makeTarget('test', 'text/plain', [('charset', 'utf-8')], None)
        self.assertFalse(target.isdir())

class DataSchemeAssetResolverTest(TestCase):
    def _makeTarget(self, *args, **kwargs):
        from .data import DataSchemeAssetResolver
        return DataSchemeAssetResolver(*args, **kwargs)

    def test_resolve_not_data_scheme(self):
        with self.assertRaises(ValueError):
            self._makeTarget().resolve(u'file:') 

    def test_resolve_1(self):
        result = self._makeTarget().resolve(u'data:text/plain,test') 
        self.assertEquals(result.content_type, u"text/plain")
        self.assertEquals(result.params, [])
        self.assertEquals(result.content, u'test')
        self.assertEquals(result.content_encoding, None)

    def test_resolve_2(self):
        result = self._makeTarget().resolve(u'data:text/plain;a=b,test') 
        self.assertEquals(result.content_type, u"text/plain")
        self.assertEquals(result.params, [('a', 'b')])
        self.assertEquals(result.content, u'test')
        self.assertEquals(result.content_encoding, None)

    def test_resolve_3(self):
        result = self._makeTarget().resolve(u'data:text/plain;a="\\"b",test') 
        self.assertEquals(result.content_type, u"text/plain")
        self.assertEquals(result.params, [('a', '"b')])
        self.assertEquals(result.content, u'test')
        self.assertEquals(result.content_encoding, None)

