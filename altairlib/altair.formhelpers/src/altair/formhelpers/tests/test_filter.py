# encoding: utf-8

from unittest import TestCase

class HalfwidthFilterTest(TestCase):
    def _getTarget(self):
        from ..filters import halfwidth
        return halfwidth

    def _callFUT(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_it(self):
        self.assertEqual(self._callFUT(u"ＡＢＣＤＥ"), u"ABCDE")
        self.assertEqual(self._callFUT(u"￥"), u"\u00a5")
        self.assertEqual(self._callFUT(u"〜"), u"~")
