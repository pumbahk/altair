# -*- coding:utf-8 -*-
import unittest

class NaturalOrderTests(unittest.TestCase):
    def _callFUT(self, *args, **kwargs):
        from altair.app.ticketing.tickets.preview.fillvalues import natural_order
        return natural_order(*args, **kwargs)

    def test_it(self):
        xs = ["line11", "line1", "line3", "line"]
        result = self._callFUT(xs)
        self.assertEqual(result, ["line", "line1", "line3", "line11"])

    def test_it2(self):
        xs = ["1.line", "11.line", "3.line"]
        result = self._callFUT(xs)
        self.assertEqual(result, ["1.line", "3.line", "11.line"])

    def test_it3(self):
        xs = ["bar-1.2.3", "foo-2.1", "foo-1.2.4", "foo-1.2.2"]
        result = self._callFUT(xs)
        self.assertEqual(result, ["bar-1.2.3", "foo-1.2.2", "foo-1.2.4", "foo-2.1"])
