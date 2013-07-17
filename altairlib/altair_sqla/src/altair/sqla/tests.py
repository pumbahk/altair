import unittest
import mock

class DummyObject(object):
    def __init__(self, **kw):
        for k,v in kw.items():
            setattr(self, k, v)

class AssociationProxyManyTests(unittest.TestCase):
    def _getTarget(self):
        from . import AssociationProxyMany
        return AssociationProxyMany


    def test_it(self):
        target = self._getTarget()
        class Dummy(object):
            def __init__(self):
                self.dummy_attr = [
                    DummyObject(values=[i, i*10])
                    for i in range(3)
                    ]

            results = target('dummy_attr', 'values')

        dummy = Dummy()
        
        self.assertEqual(dummy.results,
                         [0, 0, 1, 10, 2, 20])
