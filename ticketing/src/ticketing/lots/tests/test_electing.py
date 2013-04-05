import unittest
from pyramid import testing
from zope.interface.verify import verifyObject

class ElectingTests(unittest.TestCase):

    def _getTarget(self):
        from ..electing import Electing
        return Electing

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_it(self):
        from ..interfaces import IElecting
        request = testing.DummyRequest()
        lot = testing.DummyResource()
        target = self._makeOne(request, lot)

        verifyObject(IElecting, target)

    def test_elect_lot_entries(self):
        request = testing.DummyRequest()
        lot = testing.DummyResource(id=None)
        target = self._makeOne(lot, request)

        target.elect_lot_entries()
