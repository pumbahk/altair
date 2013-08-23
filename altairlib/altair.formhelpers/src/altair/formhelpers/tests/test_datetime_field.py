from unittest import TestCase
from webob.multidict import MultiDict
from wtforms.form import WebobInputWrapper
from datetime import date, datetime
import itertools

class OurDateTimeFieldTest(TestCase):
    def _getTarget(self):
        from altair.formhelpers.fields.datetime import OurDateTimeField
        return OurDateTimeField

    def _makeOne(self, *args, **kwargs):
        unbound_field = self._getTarget()(*args, **kwargs)
        return unbound_field.bind(None, 'test')

    def test_rest_of_fields_missing(self):
        from altair.formhelpers.fields.datetime import  Min, Max

        defaults_map = {
            'year': (None, None, None),
            'month': (1, 1, 12),
            'day': (1, 1, 31),
            'hour': (0, 0, 23),
            'minute': (0, 0, 59),
            'second': (0, 0, 59),
            }

        field_values = [
            {
                'formdata': ('test.year', '2000'),
                'data': ('year', 2000)
                },
            {
                'formdata': ('test.month', '1'),
                'data': ('month', 1) 
                },
            {
                'formdata': ('test.day', '2'),
                'data': ('day', 2)
                },
            {
                'formdata': ('test.hour', '3'),
                'data': ('hour', 3)
                },
            {
                'formdata': ('test.minute', '4'),
                'data': ('minute', 4)
                },
            {
                'formdata': ('test.second', '5'),
                'data': ('second', 5)
                }
            ]

        target = self._getTarget()
        keys = ('year', 'month', 'day', 'hour', 'minute', 'second')
        missing_value_defaults_combinations = list(
            zip((target._missing_value_defaults[k], Min, Max), defaults_map[k])
            for k in keys
            )
        for combination in itertools.product(*missing_value_defaults_combinations):
            defaults = zip(keys, combination)
            missing_value_defaults = dict((k, v[0]) for k, v in defaults)
            for n in range(0, len(field_values)):
                if n == 0:
                    expected = None
                else:
                    args = dict((k, v[1]) for k, v in defaults)
                    for field_value in field_values[0:n]:
                        args[field_value['data'][0]] = field_value['data'][1]
                    expected = datetime(**args)
                params = dict(field_value['formdata'] for field_value in field_values[0:n])
                formdata = MultiDict(params)
                field = self._makeOne(missing_value_defaults=missing_value_defaults)
                field.process(WebobInputWrapper(MultiDict(formdata)))
                self.assertEqual(field.data, expected)
                self.assertEqual(field.raw_data, expected and [expected.strftime('%Y-%m-%d %H:%M:%S')])

    def test_some_fields_missing(self):
        field = self._makeOne()
        field.process(WebobInputWrapper(MultiDict({'test.month': '1'})))
        self.assertEqual(["Required field `year' is not supplied"], field.process_errors)
        self.assertEqual(field.data, None)
        self.assertEqual(field.raw_data, None)


    def test_invalid_value(self):
        field = self._makeOne()
        field.process(WebobInputWrapper(MultiDict({'test.year': 'XXXX'})))
        self.assertEqual(["Invalid value for year", 'Not a valid datetime value'], field.process_errors)
        self.assertEqual(field.data, None)
        self.assertEqual(field.raw_data, None)

