# -*- encoding:utf-8 -*-
import unittest

class CustomPredictesTests(unittest.TestCase):
    def _callFUT(self, *args, **kwargs):
        from altairsite.mobile.custom_predicates import mobile_access_predicate
        return mobile_access_predicate(*args, **kwargs)

    def test_mobile_request(self):
        class request(object):
            environ = {"HTTP_USER_AGENT": "DoCoMo/2.0 P903i(c100;TB;W24H12)"}

        result = self._callFUT(None, request)
        self.assertTrue(result)

    def test_pc_request(self):
        class request(object):
            environ = {"HTTP_USER_AGENT": "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:13.0) Gecko/20100101 Firefox/13.0"}

        result = self._callFUT(None, request)
        self.assertFalse(result)

if __name__ == "__main__":
    unittest.main()
