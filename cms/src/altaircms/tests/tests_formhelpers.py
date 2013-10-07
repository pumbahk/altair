# -*- coding:utf-8 -*-
import unittest

class MaybeSelectFieldTests(unittest.TestCase):
    def _getTarget(self):
        from altaircms.formhelpers import MaybeSelectField
        return MaybeSelectField

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_render_with_blank_text_paramater(self):
        from wtforms import Form
        class MForm(Form):
            vs = self._makeOne(label="values", choices=[], blank_text=u"yay--this-is-blank-text")
        target = MForm()
        self.assertIn(u"yay--this-is-blank-text", target.vs.__html__())

    def test_with_empty(self):
        from wtforms import Form
        class MForm(Form):
            vs = self._makeOne(label="values", choices=[])
        target = MForm()
        self.assertTrue(target.validate())
        self.assertEqual(target.data["vs"], None)

    def test_with_blank_text(self):
        from wtforms import Form
        from webob.multidict import MultiDict
        blank_value = "_None"
        assert self._getTarget().blank_value == blank_value
        postdata = MultiDict({"vs": blank_value})

        class MForm(Form):
            vs = self._makeOne(label="values", choices=[])
        target = MForm(postdata)
        self.assertTrue(target.validate())
        self.assertEqual(target.data["vs"], None)

    def test_with_collect_value(self):
        from wtforms import Form
        from webob.multidict import MultiDict
        postdata = MultiDict({"vs": u"1"})

        class MForm(Form):
            vs = self._makeOne(label="values", choices=[(("1", "one"))], coerce=unicode)
        target = MForm(postdata)
        self.assertTrue(target.validate())
        self.assertEqual(target.data["vs"], u"1")

    def test_with_collect_value_with_coerce(self):
        from wtforms import Form
        from webob.multidict import MultiDict
        postdata = MultiDict({"vs": u"1"})

        class MForm(Form):
            vs = self._makeOne(label="values", choices=[((1, "one"))], coerce=int)
        target = MForm(postdata)
        self.assertTrue(target.validate())
        self.assertEqual(target.data["vs"], 1)

    def test_with_collect_value_with_blank_value(self):
        from wtforms import Form
        from webob.multidict import MultiDict
        blank_value = "NIL"
        postdata = MultiDict({"vs": blank_value})

        class MForm(Form):
            vs = self._makeOne(label="values", choices=[((1, "one"))], coerce=int, blank_value=blank_value)
        target = MForm(postdata)
        target.validate()
        self.assertTrue(target.validate())
        self.assertEqual(target.data["vs"], None)


    def test_with_invalid_value(self):
        from wtforms import Form
        from webob.multidict import MultiDict
        postdata = MultiDict({"vs": u"this-is-invalid"})

        class MForm(Form):
            vs = self._makeOne(label="values", choices=[((1, "one"))], coerce=int)
        target = MForm(postdata)
        self.assertFalse(target.validate())
        self.assertTrue(target.errors)


    def test_with_invalid_value_blank_value(self):
        from wtforms import Form
        from webob.multidict import MultiDict
        postdata = MultiDict({"vs": u"NIL"})

        class MForm(Form):
            vs = self._makeOne(label="values", choices=[((1, "one"))], blank_value="NOT_NIL")
        target = MForm(postdata)
        self.assertFalse(target.validate())
        self.assertTrue(target.errors)

    def test_choices_values_is_changed_dynamically(self):
        from wtforms import Form
        from webob.multidict import MultiDict
        postdata = MultiDict({"vs": u"1"})

        class MForm(Form):
            vs = self._makeOne(label="values", choices=[])
        target = MForm(postdata)
        target.vs.choices = [(u"1", u"1")]
        self.assertTrue(target.validate())
        self.assertEqual(target.data["vs"], u"1")


class CheckboxListFieldTests(unittest.TestCase):
    def _getTarget(self):
        from altaircms.formhelpers import CheckboxListField
        return CheckboxListField

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_render_empty(self):
        from wtforms import Form
        class MForm(Form):
            vs = self._makeOne(label="values", choices=[])
        target = MForm()
        self.assertEqual(u'<div id="vs"></div>', target.vs.__html__())

    @unittest.skip ("* #5609: must fix")
    def test_render_list(self):
        from wtforms import Form
        class MForm(Form):
            vs = self._makeOne(label="values", choices=[("1", "foo"), ("2", u"あ")])
        target = MForm()
        self.assertEqual(u'<div id="vs"><input type="checkbox" name=vs value="1"/>foo<input type="checkbox" name=vs value="2"/>あ</div>', target.vs.__html__())

    def test_with_collect_value(self):
        from wtforms import Form
        from webob.multidict import MultiDict
        postdata = MultiDict({"vs": u"1"})

        class MForm(Form):
            vs = self._makeOne(label="values", choices=[(("1", "one"))], coerce=unicode)
        target = MForm(postdata)
        self.assertTrue(target.validate())
        self.assertEqual(target.data["vs"], [u"1"])

    def test_with_collect_value_with_coerce(self):
        from wtforms import Form
        from webob.multidict import MultiDict
        postdata = MultiDict({"vs": u"1"})

        class MForm(Form):
            vs = self._makeOne(label="values", choices=[((1, "one"))], coerce=int)
        target = MForm(postdata)
        self.assertTrue(target.validate())
        self.assertEqual(target.data["vs"], [1])

    def test_with_multiple_value(self):
        from wtforms import Form
        from webob.multidict import MultiDict
        postdata = MultiDict([("vs", u"1"), ("vs", u"2")])

        class MForm(Form):
            vs = self._makeOne(label="values", choices=[("1", "one"), ("2", "tow")], coerce=unicode)
        target = MForm(postdata)
        self.assertTrue(target.validate())
        self.assertEqual(target.data["vs"], [u"1", u"2"])

if __name__ == "__main__":
    unittest.main()
