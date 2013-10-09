import unittest
from webob.multidict import MultiDict

class DealCondPartFormQueryTest(unittest.TestCase):
    def _getTarget(self):
        from altairsite.search.forms import DealCondPartForm
        return DealCondPartForm

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def _callFUT(self, target, *args, **kwargs):
        self.assertTrue(target.validate())
        return target.make_query_params(*args, **kwargs)
        
    def test_dealcond_one(self):
        params = MultiDict(deal_cond="1")
        target = self._makeOne(params)
        target.deal_cond.choices = [("1", "one")]
        self.assertIn("deal_cond", target._fields.keys())
        
        result = self._callFUT(target)
        self.assertEqual(result, {"deal_cond": [u"1"]})

    def test_dealcond_multiple(self):
        params = MultiDict([("deal_cond","1"), ("deal_cond","2")])
        target = self._makeOne(params)
        target.deal_cond.choices = [("1", "one"), ("2", "two")]
        self.assertIn("deal_cond", target._fields.keys())
        
        result = self._callFUT(target)
        self.assertEqual(result, {"deal_cond": [u"1", u"2"]})

    def test_dealcond_with_invalid(self):
        params = MultiDict([("deal_cond","1"), ("deal_cond","2"), ("deal_cond", "hehehheheh")])
        target = self._makeOne(params)
        target.deal_cond.choices = [("1", "one"), ("2", "two")]
        self.assertIn("deal_cond", target._fields.keys())

        self.assertFalse(target.validate())


class GenrePartFormQueryTest(unittest.TestCase):
    def _getTarget(self):
        from altairsite.search.forms import GenrePartForm
        return GenrePartForm

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def _callFUT(self, target, *args, **kwargs):
        self.assertTrue(target.validate())
        return target.make_query_params(*args, **kwargs)
        
    @unittest.skip ("* #5609: must fix")
    def test_top_categories(self):
        params = MultiDict(music="on")
        target = self._makeOne(params)
        self.assertIn("music", target._fields.keys())
        
        result = self._callFUT(target)

        self.assertEquals(["music"], result["top_categories"])
        self.assertEquals([], result["sub_categories"])

    @unittest.skip ("* #5609: must fix")
    def test_sub_categories(self):
        params = MultiDict(anime="on")
        target = self._makeOne(params)

        self.assertIn("anime", [k for k, _ in target.music_subgenre.choices])

        result = self._callFUT(target)

        self.assertEquals([], result["top_categories"])
        self.assertEquals(["anime"], result["sub_categories"])

    @unittest.skip ("* #5609: must fix")
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
        params = MultiDict(pref_shutoken="tokyo")
        target = self._makeOne(params)
        
        result = self._callFUT(target)

        self.assertEquals([], result["areas"])
        self.assertEquals(["tokyo"], result["prefectures"])


    def test_with_junk_parameters(self):
        params = MultiDict(pref_shutoken="doko_ka_shiranai_tokoro")
        target = self._makeOne(params)

        with self.assertRaises(AssertionError):
            self._callFUT(target)

if __name__ == "__main__":
    unittest.main()
