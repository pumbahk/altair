# -*- coding:utf-8 -*-
import unittest
from pyramid.testing import DummyResource

class MaybeSelectFieldTests(unittest.TestCase):
    def _getTarget(self):
        from altairsite.search.formparts import MaybeSelectField
        return MaybeSelectField

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def _makeForm(self, field, *args, **kwargs):
        from wtforms import form
        class DummyForm(form.Form):
            target = field
        return DummyForm(*args, **kwargs)

    def test_rendering(self):
        target_field = self._makeOne(null_label=u"not found", choices=[("a", "a")])
        form = self._makeForm(target_field)
        self.assertIn('<option value="__None">not found</option>', form.target.__html__())

    def test_process_formdata(self):
        from webob.multidict import MultiDict

        target_field = self._makeOne(null_label=u"not found", choices=[("a", "a_label")])

        params = MultiDict({"target": self._getTarget().NONE_VALUE})
        form = self._makeForm(target_field, formdata=params)
        self.assertEquals(None, form.data["target"])

        params = MultiDict({"target":"a"})
        form = self._makeForm(target_field, formdata=params)
        self.assertEquals("a", form.data["target"])
        
        
class CheckBoxWidgetRenderingTests(unittest.TestCase):
    def _getTarget(self):
        from altairsite.search.formparts import CheckboxListWidget
        return CheckboxListWidget

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_with_rendering_status(self):
        target = self._makeOne()
        field = DummyResource(id="my-id")
        
        result = target(field, choices=[("check-box-name", u"チェックボックス脇の説明")], value=[])

        self.assertIn('id="my-id"', result)
        self.assertIn('<input type="checkbox" name="check-box-name"', result)
        self.assertIn(u'チェックボックス脇の説明', result)

    def test_with_rendering_status_checked(self):
        target = self._makeOne()
        field = DummyResource(id="my-id")
        
        result = target(field, choices=[("check-box-name", u"チェックボックス脇の説明")], value=["check-box-name"])

        self.assertIn('<input checked type="checkbox" name="check-box-name" value="y"', result)
        self.assertIn(u'チェックボックス脇の説明', result)

    def test_take_params_from_field_status(self):
        target = self._makeOne()
        field = DummyResource(id="my-id", choices=[("check-box-name", u"チェックボックス脇の説明")],)
        
        result = target(field, value=[])

        self.assertIn('<input type="checkbox" name="check-box-name"', result)
        self.assertIn(u'チェックボックス脇の説明', result)

class CheckBoxFieldValueTest(unittest.TestCase):

    def _getTarget(self):
        from altairsite.search.formparts import CheckboxListField
        return CheckboxListField

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def _makeForm(self, field, *args, **kwargs):
        from wtforms import form
        class DummyForm(form.Form):
            target = field
        return DummyForm(*args, **kwargs)

    def test_with_one_string(self):
        target_field = self._getTarget()
        form = self._makeForm(target_field(), target=u"てすと")

        result = form.target._value()
        self.assertEquals(result, [u"てすと"])

    def test_with_separated_string(self):
        target_field = self._getTarget()
        form = self._makeForm(target_field(), target=u"apple,banana,orange")

        result = form.target._value()
        self.assertEquals(result, [u"apple", u"banana", u"orange"])

    def test_with_iterable_object(self):
        target_field = self._getTarget()

        form = self._makeForm(target_field(), target=[1, 2, 3])
        result = form.target._value()
        self.assertEquals(result, [u"1", u"2", u"3"])

        form = self._makeForm(target_field(), target=set([1, 2, 3]))
        result = form.target._value()
        self.assertEquals(result, [u"1", u"2", u"3"])

    ## about choices value
    def test_predefine_choices(self):
        target_field = self._getTarget()
        target_field(choices=[("check-box-name", u"チェックボックス脇の説明"), 
                              ("check-box-name-2", u"チェックボックス脇の説明-2")])

    ## process form data test
    def test_process_formdata(self):
        target_field = self._makeOne(choices=[(unicode(x), x) for x in [1, 2, 3, 4, 5]])

        from webob.multidict import MultiDict
        postdata = MultiDict({"1":"y", "2":"y", "3":"y", "target":"", "foo":"bar"})
        form = self._makeForm(target_field, formdata=postdata)
        
        result = form.data["target"]
        self.assertEquals(sorted(result), sorted(["1", "2", "3"]))


if __name__ == "__main__":
    unittest.main()
