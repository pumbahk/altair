import unittest

class Dummy(object):
    def __init__(self, **kwargs):
        for name, value in kwargs.items():
            setattr(self, name, value)

class getattr_exTests(unittest.TestCase):

    def _callFUT(self, *args, **kwargs):
        from . import getattr_ex
        return getattr_ex(*args, **kwargs)


    def test_single(self):
        dummy1 = Dummy(a=1)
        result = self._callFUT(dummy1, "a")
        self.assertEqual(result, 1)

    def test_nested(self):
        dummy1 = Dummy(a=Dummy(b=Dummy(c=999)))

        result = self._callFUT(dummy1, "a.b.c")
        self.assertEqual(result, 999)

    def test_nothing(self):
        dummy1 = Dummy(a=1)

        result = self._callFUT(dummy1, "a.b.c")
        self.assertIsNone(result)

    def test_none(self):
        result = self._callFUT(None, "a.b.c")
        self.assertIsNone(result)


class lineage_acquiresTests(unittest.TestCase):
    def _callFUT(self, *args, **kwargs):
        from . import lineage_acquires
        return lineage_acquires(*args, **kwargs)

    def test_empty(self):
        obj = object()
        result = self._callFUT(obj, [])
        self.assertEqual(result, [obj])

    def test_it(self):
        b = Dummy(c=999)
        a = Dummy(b=b)
        dummy1 = Dummy(a=a)
        result = self._callFUT(dummy1, ["a", "a.b"])
        self.assertEqual(result, [dummy1, a, b])


class AcquisitionTests(unittest.TestCase):

    def _getTarget(self):
        from . import Acquisition
        return Acquisition

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)


    def test_it(self):
        d1 = Dummy(value1=100, value2=None, value3=None,
                   d2=Dummy(value1=50, value2=200),
               )

        d3 = Dummy(value1=20, value2=300, value3=500)

        dummy = Dummy(d1=d1,
                      d3=d3)
        target = self._makeOne(dummy, ['d1', 'd1.d2', 'd3'])

        self.assertEqual(target.value1, 100)
        self.assertEqual(target.value2, 200)
        self.assertEqual(target.value3, 500)
