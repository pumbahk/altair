# -*- coding:utf-8 -*-
import unittest
from collections import defaultdict

DummyInfodata = lambda : defaultdict(str)

class InfoRendererTests(unittest.TestCase):
    def _makeOne(self, *args, **kwargs):
        from altair.app.ticketing.mails.forms import SubjectInfoRenderer
        return SubjectInfoRenderer(*args, **kwargs)

    def _getDummyDefault(self, default_value):
        from altair.app.ticketing.mails.forms import SubjectInfo
        class DummyDefaultGet(object):
            def getval(o):
                return default_value
            field_x = SubjectInfo(name="field_x", label=u"フィールドx", getval=getval)
        return DummyDefaultGet()

    def test_visible_with_value(self):
        class Obj(object):
            pass
        data = DummyInfodata()
        data["field_x"] = {"use": True,  "kana": u"フィールドx", "value": u"<set-value>"}
        target = self._makeOne(Obj(), data, self._getDummyDefault("<default-field-x-value>"))
        result = target.get("field_x")
        self.assertEqual(result.status, True)
        self.assertEqual(result.label, u"フィールドx")
        self.assertEqual(result.body, u"<set-value>")

    def test_visible_without_value(self):
        class Obj(object):
            x = "<default-field-x-value>"
        data = DummyInfodata()
        data["field_x"] = {"use": True,  "kana": u"フィールドx"}

        target = self._makeOne(Obj(), data, self._getDummyDefault("<default-field-x-value>"))
        result = target.get("field_x")
        self.assertEqual(result.status, True)
        self.assertEqual(result.label, u"フィールドx")
        self.assertEqual(result.body, u"<default-field-x-value>")

    def test_unvisible_return_emptry_string(self):
        class Obj(object):
            pass
        data = DummyInfodata()
        data["field_x"] = {"use": False,  "kana": u"フィールドx"}
        target = self._makeOne(Obj(), data, self._getDummyDefault("<default-field-x-value>"))
        result = target.get("field_x")
        self.assertEqual(result.status, False)
        self.assertEqual(result.label, u"")
        self.assertEqual(result.body, u"")

    def test_unvisible_return_emptry_string2(self):
        class Obj(object):
            pass
        data = DummyInfodata()
        data["field_x"] = {"use": False,  "kana": u"フィールドx", "value": u"<set-value>"}
        target = self._makeOne(Obj(), data, self._getDummyDefault("<default-field-x-value>"))
        result = target.get("field_x")
        self.assertEqual(result.status, False)
        self.assertEqual(result.label, u"")
        self.assertEqual(result.body, u"")

    def test_missing_data_delegate_default_impl(self):
        class Obj(object):
            pass
        data = DummyInfodata()
        target = self._makeOne(Obj(), data, self._getDummyDefault("<default-field-x-value>"))
        result = target.get("field_x")
        self.assertEqual(result.status, True)
        self.assertEqual(result.label, u"フィールドx")
        self.assertEqual(result.body, u"<default-field-x-value>")

    def test_unbound_data_delegate_default_impl(self):
        class Obj(object):
            pass
        data = None
        target = self._makeOne(Obj(), data, self._getDummyDefault("<default-field-x-value>"))
        result = target.get("field_x")
        self.assertEqual(result.status, True)
        self.assertEqual(result.label, u"フィールドx")
        self.assertEqual(result.body, u"<default-field-x-value>")

if __name__ == "__main__":
    unittest.main()
