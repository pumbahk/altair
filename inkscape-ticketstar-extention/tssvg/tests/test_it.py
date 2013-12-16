# -*- coding:utf-8 -*-
import unittest

import sys
import os

sys.path.append(os.path.join(
   os.path.abspath(os.path.dirname(os.path.dirname(__file__))),
    "../"
   ))
sys.path.append(os.path.join(
   os.path.abspath(os.path.dirname(os.path.dirname(__file__))),
    "../../"
   ))

class OutputExtensionTests(unittest.TestCase):
    def _getTarget(self):
        from tssvg_output import getapp
        return getapp

    def test_it(self):
        ### MS PGothic(internal) -> ＭＳ Ｐゴシック
        ### ＭＳ Ｐゴシック(internal) ->  ＭＳ Ｐゴシック

        from StringIO import StringIO
        mapping = {
            "MS PGothic": u"ＭＳ Ｐゴシック"
        }
        app = self._getTarget()(mapping=mapping)
        targetfile = os.path.join(os.path.dirname(__file__), "sample.svg")

        ## check file format
        with open(targetfile) as rf:
            content = rf.read().decode("utf-8")
            self.assertTrue(u"font-family: MS PGothic" in content)
            self.assertTrue(u"font-family: ＭＳ Ｐゴシック" in content)

        io = StringIO()
        stdout_old, sys.stdout = sys.stdout, io
        try:
            app.affect([targetfile])
        finally:
            sys.stdout = stdout_old

        result = io.getvalue().decode("utf-8")
        self.assertTrue(u"font-family:ＭＳ Ｐゴシック" in result)
        self.assertFalse(u"font-family: MS PGothic" in result)

class InputExtensionTests(unittest.TestCase):
    def _getTarget(self):
        from tssvg_input import getapp
        return getapp

    def test_it(self):
        ### ＭＳ Ｐゴシック -> MS PGothic(internal)
        ### MS PGothic -> MS PGothic(internal)

        from StringIO import StringIO
        cache = {}
        app = self._getTarget()(cache)
        targetfile = os.path.join(os.path.dirname(__file__), "sample.svg")
        ## check file format
        with open(targetfile) as rf:
            content = rf.read().decode("utf-8")
            self.assertTrue(u"font-family: MS PGothic" in content)
            self.assertTrue(u"font-family: ＭＳ Ｐゴシック" in  content)

        io = StringIO()
        stdout_old, sys.stdout = sys.stdout, io
        try:
            app.affect([targetfile])
        finally:
            sys.stdout = stdout_old

        result = io.getvalue().decode("utf-8")
        self.assertTrue(u"font-family:ＭＳ Ｐゴシック" in result)
        self.assertFalse(u"font-family: MS PGothic" in result)

if __name__ == '__main__':
    unittest.main()
