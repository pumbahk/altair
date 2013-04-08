import unittest
import mock
from pyramid import testing

class ElectingTests(unittest.TestCase):

    def _getTarget(self):
        from ..electing import Electing
        return Electing

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_it(self):
        from ..interfaces import IElecting
        from zope.interface.verify import verifyObject
        request = testing.DummyRequest()
        lot = testing.DummyResource()
        target = self._makeOne(request, lot)

        verifyObject(IElecting, target)

    def test_elect_lot_entries(self):
        request = testing.DummyRequest()
        mock_lot = mock.Mock()
        elected_wishes = [mock.Mock(entry=mock_lot.entry)]
        rejected_wishes = [mock.Mock(entry=mock_lot.entry)]
        mock_lot.get_elected_wishes.return_value = elected_wishes
        mock_lot.get_rejected_wishes.return_value = rejected_wishes

        target = self._makeOne(mock_lot, request)

        target.elect_lot_entries()

        mock_lot.entry.elect.assert_called_with(elected_wishes[0])
        mock_lot.entry.reject.assert_called_with()
        mock_lot.finish_lotting.assert_called_with()
