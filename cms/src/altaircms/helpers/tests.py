# -*- coding:utf-8 -*-
import unittest

class UnqoutePathSegmentTests(unittest.TestCase):
    def _callFUT(self, *args, **kwargs):
        from altaircms.helpers.link import unquote_path_segment
        return unquote_path_segment(*args, **kwargs)

    def _quoted(self, v):
        from pyramid.traversal import quote_path_segment
        return quote_path_segment(v)

    def test_without_slash(self):
        result = self._callFUT(self._quoted("foo-bar"))
        self.assertEquals(result, "foo-bar")

    def test_with_slash(self):
        self.assertEquals(self._quoted("foo/bar"), "foo%2Fbar")

    def test_with_slash2(self):
        self.assertEquals(self._quoted("foo/bar/boo/foo-foo"), "foo%2Fbar%2Fboo%2Ffoo-foo")

        result = self._callFUT(self._quoted("foo/bar/boo/foo-foo"))
        self.assertEquals(result, "foo/bar/boo/foo-foo")

    def test_have_slash_and_quoted(self):
        result = self._callFUT(self._quoted("%2Ffoo/bar"))
        self.assertNotEquals(result, "%2Ffoo%2Fbar")

    def test_have_slash_and_quoted2(self):
        result = self._callFUT(self._quoted("foo/bar%ffwe%2%3%2F"))
        self.assertNotEquals(result,self._quoted("foo%2Fbar%ffwe%2%3%2F"))

class URLQueryReplacerTest(unittest.TestCase):
    def _getTarget(self, *args, **kwargs):
        from altaircms.helpers import url_query_replacer
        return url_query_replacer(*args, **kwargs)

    def test_it(self):
        target = self._getTarget("/")
        result = target("1")
        print result

if __name__ == "__main__":
    unittest.main()

