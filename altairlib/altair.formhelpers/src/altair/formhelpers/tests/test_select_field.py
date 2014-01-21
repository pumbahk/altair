from unittest import TestCase
from webob.multidict import MultiDict
from wtforms.form import WebobInputWrapper
from mock import Mock
import itertools

class OurSelectFieldTest(TestCase):
    def _getTarget(self):
        from altair.formhelpers.fields.select import LazySelectField
        return LazySelectField

    def _makeOne(self, *args, **kwargs):
        unbound_field = self._getTarget()(*args, **kwargs)
        return unbound_field.bind(None, 'test')

    def test_invalid_choice(self):
        coercer = Mock()
        coercer.return_value = 'coerced'
        field = self._makeOne(
            coerce=coercer,
            choices=[(u'a', 'a')]
            )
        field.process(WebobInputWrapper(MultiDict(test='b')))
        self.assertEqual(len(field.errors), 0)
        field.validate(None)
        self.assertEqual(len(field.errors), 1)

    def test_coerce(self):
        coercer = Mock()
        coercer.return_value = 'coerced'
        field = self._makeOne(
            coerce=coercer,
            choices=[(u'a', 'a')]
            )
        field.process(WebobInputWrapper(MultiDict(test='a')))
        self.assertEqual(field.data, 'coerced')
