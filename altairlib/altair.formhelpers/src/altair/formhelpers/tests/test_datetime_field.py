from unittest import TestCase
from webob.multidict import MultiDict
from wtforms.form import WebobInputWrapper
from datetime import date, datetime

class OurDateTimeFieldTest(TestCase):
    def _getTarget(self):
        from altair.formhelpers.fields.datetime import OurDateTimeField
        return OurDateTimeField

    def _makeOne(self, *args, **kwargs):
        unbound_field = self._getTarget()(*args, **kwargs)
        return unbound_field.bind(None, 'test')

    def test_all_field_missing(self):
        field = self._makeOne()
        field.process(WebobInputWrapper(MultiDict()))
        self.assertEqual(len(field.process_errors), 0)
        self.assertEqual(field.data, None)
        self.assertEqual(field.raw_data, None)

    def test_rest_of_fields_missing(self):
        defaults = {
            'month': 1,
            'day': 1,
            'hour': 0,
            'minute': 0,
            'second': 0
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

        for n in range(1, len(field_values)):
            args = dict(defaults)
            for field_value in field_values[0:n]:
                args[field_value['data'][0]] = field_value['data'][1]
            expected = datetime(**args)
            formdata = MultiDict(dict(field_value['formdata'] for field_value in field_values[0:n]))
            field = self._makeOne()
            field.process(WebobInputWrapper(MultiDict(formdata)))
            self.assertEqual(field.data, expected)
            self.assertEqual(field.raw_data, [expected.strftime('%Y-%m-%d %H:%M:%S')])

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

