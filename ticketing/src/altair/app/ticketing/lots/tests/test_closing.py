import unittest
from pyramid import testing

class DummyEntry(object):
    def __init__(self, entry_no):
        self.entry_no = entry_no
        self.called = []

    def close(self):
        self.called.append('close')

class DummyLot(testing.DummyModel):
    def __init__(self, *args, **kwargs):
        testing.DummyModel.__init__(self, *args, **kwargs)
        self.called = []

    def finish_lotting(self):
        self.called.append('finish_lotting')

class LotCloseTests(unittest.TestCase):
    def _getTarget(self):
        from .. import closing
        return closing.LotCloser

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_empty(self):
        lot = DummyLot(id=999999, remained_entries=[])
        target = self._makeOne(lot, None)

        target.close()
        self.assertEqual(lot.called, ["finish_lotting"])

    def test_one(self):
        entry = DummyEntry(entry_no="testing-entry-no")
        lot = DummyLot(id=989898989, remained_entries=[entry])
        target = self._makeOne(lot, None)

        target.close()

        self.assertEqual(entry.called, ["close"])
        self.assertEqual(lot.called, ["finish_lotting"])
