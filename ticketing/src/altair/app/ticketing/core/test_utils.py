# -*- coding:utf-8 -*-

import unittest

def _split_by_dot(s):
    return s.split(".")

class TreeDictFromFlattenTests(unittest.TestCase):
    def _callFUT(self, *args, **kwargs):
        from .utils import tree_dict_from_flatten
        return tree_dict_from_flatten(*args, **kwargs)

    def test_simple0(self):
        result = self._callFUT({"a": "x", "b": "y"}, _split_by_dot)
        self.assertEquals(result, {"a": "x", "b": "y"})

    def test_it0(self):
        d = {"a": "x", "b.c.d.e": "y"}
        result = self._callFUT(d, _split_by_dot)
        self.assertEquals(result, {"a": "x", "b": {"c": {"d": {"e": "y"}}}})

    def test_it(self):
        d = {"a": "x", "b.c.d.e": "y", "b.c.d2": "z"}
        result = self._callFUT(d, _split_by_dot)
        self.assertEquals(result, {"a": "x", "b": {"c": {"d": {"e": "y"}, "d2": "z"}}})

class MergeDictRecursiveTests(unittest.TestCase):
    def _callFUT(self, *args, **kwargs):
        from .utils import merge_dict_recursive
        return merge_dict_recursive(*args, **kwargs)

    def test_simple0(self):
        result = self._callFUT({}, {})
        self.assertEqual(result, {})

    def test_simple1(self):
        d1 = {"k": "v"}
        d2 = {}
        result = self._callFUT(d1, d2)
        self.assertEqual(result, {"k": "v"})

    def test_simple2(self):
        d1 = {}
        d2 = {"k": "v"}
        result = self._callFUT(d1, d2)
        self.assertEqual(result, {"k": "v"})

    def test_simple3(self):
        d1 = {"k": {"x": "y"}}
        d2 = {"k": {"a": {"b": "c"}}}
        result = self._callFUT(d1, d2)
        self.assertEqual(result, {"k": {"x": "y", "a": {"b": "c"}}})


    def test_it(self):
        d1 = {'k1': {'k2': 2, 'k5': 5}}
        d2 = {'k1': {'k2': {'k3': 3}}, 'k4': 4}
        result = self._callFUT(d1, d2)
        self.assertEqual(result, {'k1': {'k2': {'k3': 3}, 'k5': 5}, 'k4': 4})

    def test__list_is_replace(self):
        d1 = {'k1': {'k2': [2]}}
        d2 = {'k1': {'k2': [3]}}
        result = self._callFUT(d1, d2)
        self.assertEqual(result, {'k1': {'k2': [3]}})
