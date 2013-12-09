# -*- coding:utf-8 -*-
import unittest
import sys
import os

sys.path.append(os.path.join(
      os.path.abspath(os.path.dirname(os.path.dirname(__file__))),
      "../../"
      ))

class ReplaceMappingTests(unittest.TestCase):
    def _makeOne(self, *args, **kwargs):
        from tssvg import ReplaceMapping
        return ReplaceMapping(*args, **kwargs)

    def test_it(self):
        vals = [("x", "x"), ("y", "y"),( "z", "z")]
        target = self._makeOne(["x", "z"], lambda k: "*replaced*")
        result = target(vals)
        self.assertEqual(result, 
                         [("x", "*replaced*"), ("y", "y"), ("z", "*replaced*")])

class StyleReplacerTests(unittest.TestCase):
    def _getReplacer(self, target_keys):
        from tssvg import ReplaceMapping
        mapping = {
            "MS PGothic": "MS PGothic",
            u"ＭＳ Ｐゴシック".encode("utf-8"): "MS PGothic"
        }
        def convert(x):
            return mapping[x]
        return ReplaceMapping(target_keys, convert)

    def _makeOne(self, *args, **kwargs):
        from tssvg import StyleReplacer
        return StyleReplacer(*args, **kwargs)

    def test_it__en(self):
        target_keys = ["font-family", "-inkscape-font-specification"]
        style_attr = u"""line-height: 125%; fill: #000; fill-opacity: 1; stroke: none; font-family: MS PGothic; -inkscape-font-specification: MS PGothic""".encode("utf-8")

        mapping = self._getReplacer(target_keys)
        target = self._makeOne(mapping)
        result = target(style_attr)
        self.assertTrue("font-family:MS PGothic" in result)
        self.assertTrue("-inkscape-font-specification:MS PGothic" in result)

    def test_it__ja(self):
        target_keys = ["font-family", "-inkscape-font-specification"]
        style_attr = u"""line-height: 125%; fill: #000; fill-opacity: 1; stroke: none; font-family: ＭＳ Ｐゴシック; -inkscape-font-specification: ＭＳ Ｐゴシック""".encode("utf-8")

        mapping = self._getReplacer(target_keys)
        target = self._makeOne(mapping)
        result = target(style_attr)
        self.assertTrue("font-family:MS PGothic" in result)
        self.assertTrue("-inkscape-font-specification:MS PGothic" in result)



if __name__ == '__main__':
    unittest.main()
