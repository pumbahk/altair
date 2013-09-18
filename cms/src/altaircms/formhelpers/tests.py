# -*- coding:utf-8 -*-
import unittest
from webob.multidict import MultiDict

class MaybeIntegerField(unittest.TestCase):
    def _getTarget(self):
        from altaircms.formhelpers import MaybeIntegerField
        return MaybeIntegerField

    def _makeOne(self, *args, **kwargs):
        from altaircms.formhelpers import Form
        Field = self._getTarget()
        class MyForm(Form):
            n = Field()
        return MyForm(*args, **kwargs)

    def test_render(self):
        form = self._makeOne()
        self.assertEqual(form.n.data, "")

    def test_render__exists(self):
        form = self._makeOne(n=10)
        self.assertEqual(form.n.data, 10)

    def test_post__empty(self):
        form = self._makeOne(MultiDict(n=""))
        self.assertTrue(form.validate())
        self.assertEqual(form.n.data, None)
        self.assertEqual(form.data["n"], None)        

    def test_post__exists(self):
        form = self._makeOne(MultiDict(n="10"))
        self.assertTrue(form.validate())
        self.assertEqual(form.n.data, 10)
        self.assertEqual(form.data["n"], 10)        
        

if __name__ == "__main__":
    unittest.main()
