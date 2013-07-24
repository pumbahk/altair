# -*- coding:utf-8 -*-
import unittest
from collections import namedtuple
DummySseat = namedtuple("S", "name")

def get_tickets_build_pair(issued_no, seat_name):
    if seat_name:
        return (DummySseat(seat_name), {u"発券番号": issued_no})
    return (None, {u"発券番号": issued_no})

class DequeueOrderTests(unittest.TestCase): #3458
    def _callFUT(self, xs):
        from altair.app.ticketing.orders.utils import compare_by_comfortable_order
        return list(sorted(xs, key=compare_by_comfortable_order))

    def _entry(self, *args, **kwargs):
        return get_tickets_build_pair(*args, **kwargs)

    def test_it(self):
        entries=[
            self._entry(None, u"2列3番"),
            self._entry(None, u"2列1番"),
            self._entry(None, u"2列2番"),
            self._entry(None, u"2列10番"),
            ]
        result = self._callFUT(entries)
        self.assertEqual(result, [
            self._entry(None, u"2列1番"),
            self._entry(None, u"2列2番"),
            self._entry(None, u"2列3番"),
            self._entry(None, u"2列10番"),
            ])

    def test_with_block(self):
        entries=[
            self._entry(None, u"2列3番"),
            self._entry(None, u"2列1番"),
            self._entry(None, u"Aブロック1列1番"),
            self._entry(None, u"Aブロック2列1番"),
            self._entry(None, u"Aブロック1列2番"),
            self._entry(None, u"Bブロック1列1番"),
            ]
        result = self._callFUT(entries)

        self.assertEqual(result, [
            self._entry(None, u"2列1番"),
            self._entry(None, u"2列3番"),
            self._entry(None, u"Aブロック1列1番"),
            self._entry(None, u"Aブロック1列2番"),
            self._entry(None, u"Aブロック2列1番"),
            self._entry(None, u"Bブロック1列1番"),
            ])

    def test_with_no_seat(self):
        entries=[
            self._entry(None, u"2列3番"),
            self._entry(None, u"2列1番"),
            self._entry(2, None),
            self._entry(1, None),
            ]
        result = self._callFUT(entries)

        self.assertEqual(result, [
            self._entry(None, u"2列1番"),
            self._entry(None, u"2列3番"),
            self._entry(1, None),
            self._entry(2, None),
            ])
        
if __name__ == "__main__":
    unittest.main()
