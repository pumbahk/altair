import unittest
from webob.multidict import MultiDict

class GenrePartFormQueryTest(unittest.TestCase):
    def _getTarget(self):
        from altairsite.search.forms import GenrePartForm
        return GenrePartForm

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def _callFUT(self, target, *args, **kwargs):
        self.assertTrue(target.validate())
        return target.make_query_params(*args, **kwargs)
        
    def test_top_categories(self):
        params = MultiDict(music="on")
        target = self._makeOne(params)
        self.assertIn("music", target._fields.keys())
        
        result = self._callFUT(target)

        self.assertEquals(["music"], result["top_categories"])
        self.assertEquals([], result["sub_categories"])

    def test_sub_categories(self):
        params = MultiDict(jpop="on")
        target = self._makeOne(params)
        self.assertIn("jpop", [k for k, _ in target.music_subgenre.choices])

        result = self._callFUT(target)

        self.assertEquals([], result["top_categories"])
        self.assertEquals(["jpop"], result["sub_categories"])

    def test_with_junk_parameters(self):
        params = MultiDict(foo="on", bar="bar")
        target = self._makeOne(params)

        result = self._callFUT(target)

        self.assertEquals([], result["top_categories"])
        self.assertEquals([], result["sub_categories"])


class AreaPartFormQueryTest(unittest.TestCase):
    def _getTarget(self):
        from altairsite.search.forms import AreaPartForm
        return AreaPartForm

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def _callFUT(self, target, *args, **kwargs):
        self.assertTrue(target.validate())
        return target.make_query_params(*args, **kwargs)
        
    def test_area(self):
        params = MultiDict(tohoku="on")
        target = self._makeOne(params)
        
        result = self._callFUT(target)

        self.assertEquals(["tohoku"], result["areas"])
        self.assertEquals(sorted(['fukushima', 'miyagi', 'aomori', 'akita', 'iwate', 'yamagata']),
                          sorted(result["prefectures"]))

    def test_prefectures(self):
        params = MultiDict(tokyo="on")
        target = self._makeOne(params)
        
        result = self._callFUT(target)

        self.assertEquals([], result["areas"])
        self.assertEquals(["tokyo"], result["prefectures"])


    def test_with_junk_parameters(self):
        params = MultiDict(doko_ka_shiranai_tokoro="on")
        target = self._makeOne(params)

        result = self._callFUT(target)

        self.assertEquals([], result["areas"])
        self.assertEquals([], result["prefectures"])


if __name__ == "__main__":
    unittest.main()
