import unittest

class DummyMultiDict(dict):
    def getlist(self, k):
        return [self[k]]

class DynamicFormTest(unittest.TestCase):
    def _getTarget(self):
        from ..form import OurDynamicForm
        return OurDynamicForm

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_init_with_formdata(self):
        from ..fields.core import OurTextField
        x = self._makeOne(_fields=[
            ('a', OurTextField()),
            ('b', OurTextField()),
            ('c', OurTextField()),
            ],
            formdata=DummyMultiDict({'a': '1', 'b': '2', 'c': '3'})
            )
        self.assertTrue(x.validate())
        self.assertEqual(x['a'].data, '1')
        self.assertEqual(x['b'].data, '2')
        self.assertEqual(x['c'].data, '3')

    def test_init_with_data(self):
        from ..fields.core import OurTextField
        x = self._makeOne(_fields=[
            ('a', OurTextField()),
            ('b', OurTextField()),
            ('c', OurTextField()),
            ],
            **{'a': '1', 'b': '2', 'c': '3'}
            )
        self.assertTrue(x.validate())
        self.assertEqual(x['a'].data, '1')
        self.assertEqual(x['b'].data, '2')
        self.assertEqual(x['c'].data, '3')
