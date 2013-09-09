# -*- coding:utf-8 -*-
import unittest
from webob.multidict import MultiDict

class FormMemoAttributeFormTests(unittest.TestCase):
    def _getTarget(self):
        from altair.app.ticketing.orders.forms import OrderAttributesEditFormFactory
        return OrderAttributesEditFormFactory

    def test_render(self):
        target = self._getTarget()
        N = 3
        form = target(N)()
        for field in form:
            self.assertIn(field.name, "memo_on_order")
            self.assertIn(field.label, u"補助文言")

    def test_get_errors(self):
        target = self._getTarget()
        N = 3
        form = target(N)(MultiDict({"memo_on_order3": u"あいうえおかきくけこさ"}))
        self.assertFalse(form.validate())
        #self.assertEquals(form.get_error_messages(), u"補助文言3:")

    def test_get_result(self):
        target = self._getTarget()
        N = 3
        form = target(N)(MultiDict({"memo_on_order3": u"あいうえおかきくけこ"}))
        self.assertTrue(form.validate())
        result = form.get_result()
        self.assertEquals(len(result), 3)
        self.assertEquals(result[0], ("memo_on_error1", ""))
        self.assertEquals(result[1], ("memo_on_error2", ""))
        self.assertEquals(result[2], ("memo_on_error3", u"あいうえおかきくけこ"))
