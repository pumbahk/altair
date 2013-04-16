# -*- coding:utf-8 -*-
import unittest 

class SearchQueryTests(unittest.TestCase):
    def _callFUT(self, message):
        from altairsite.search.searcher import _extract_tags
        return _extract_tags({"k": message}, "k")

    def test_single(self):
        result = self._callFUT(u"あいう")
        self.assertEqual(result, [u"あいう"])

    def test_multiple(self):
        result = self._callFUT(u"あいう かきく")
        self.assertEqual(result, [u"あいう", u"かきく"])

    def test_quoted(self):
        result = self._callFUT(u'"abc def"')
        self.assertEqual(result, [u'"abc def"'])

    def test_quoted2(self):
        result = self._callFUT(u"\"ディズニーアイス\"")
        self.assertEqual(result, [u'"ディズニーアイス"'])

    def test_invalid(self):
        result = self._callFUT(u'"')
        self.assertEqual(result, [])

    def test_invalid2(self):
        result = self._callFUT(u'"foo')
        self.assertEqual(result, ["foo"])

    def test_invalid3(self):
        result = self._callFUT(u"ミスサイゴン(7/3,6,8/18,19)")
        self.assertEqual(result, [u"ミスサイゴン(7/3,6,8/18,19)"])

    def test_complex(self):
        result = self._callFUT(u'abc def "efg hij"　\'klm opq\'')
        self.assertEqual(result, [u"abc", u"def", u'"efg hij"', u'"klm opq"'])

if __name__ == "__main__":
    unittest.main()
