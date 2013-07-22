import unittest
from pyramid import testing

class DummyEntry(object):
    def __init__(self):
        self.called = []
    def close(self):
        self.called.append('close')

class LotCloseTests(unittest.TestCase):
    def _getTarget(self):
        from .. import closing
        return closing.LotCloser

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_empty(self):
        lot = testing.DummyModel(remained_entries=[])
        target = self._makeOne(lot, None)

        target.close()

    def test_one(self):
        entry = DummyEntry()
        lot = testing.DummyModel(remained_entries=[entry])
        target = self._makeOne(lot, None)

        target.close()

        self.assertEqual(entry.called, ["close"])
