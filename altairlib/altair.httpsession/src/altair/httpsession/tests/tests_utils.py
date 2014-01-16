from unittest import TestCase

class AsBoolTest(TestCase):
    def _getTarget(self):
        from ..utils import asbool
        return asbool

    def _callFUT(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_string(self):
        self.assertTrue(self._callFUT('true'))
        self.assertTrue(self._callFUT('yes'))
        self.assertTrue(self._callFUT('1'))
        self.assertFalse(self._callFUT('false'))
        self.assertFalse(self._callFUT('no'))
        self.assertFalse(self._callFUT('0'))

    def test_integer(self):
        self.assertTrue(self._callFUT(1))
        self.assertFalse(self._callFUT(0))

    def test_bool(self):
        self.assertTrue(self._callFUT(True))
        self.assertFalse(self._callFUT(False))

