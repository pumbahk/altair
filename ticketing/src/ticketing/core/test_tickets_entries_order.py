# -*- coding:utf-8 -*-
import unittest

class DummyTicketPrintQueueEntry(object):
    def __init__(self, summary, seat_name=None):
        class seat:
            name = seat_name
        self.seat = seat
        self.seat_id = bool(seat_name) or None
        self.summary = summary

    def __eq__(self,  other):
        return self.summary == other.summary and self.seat_id == other.seat_id and self.seat.name == other.seat.name

class DequeueOrderTests(unittest.TestCase): #3458
    def _callFUT(self,  *args,  **kwargs):
        from ticketing.core.models import TicketPrintQueueEntry
        return TicketPrintQueueEntry.sorted_entries(*args, **kwargs)

    def _entry(self, *args, **kwargs):
        return DummyTicketPrintQueueEntry(*args, **kwargs)

    def test_it(self):
        entries=[
            self._entry("summary", u"2列3番"),
            self._entry("summary", u"2列1番"),
            self._entry("summary", u"2列2番"),
            self._entry("summary", u"2列10番"),
            ]
        result = self._callFUT(entries)

        self.assertEqual(result, [
            self._entry("summary", u"2列1番"),
            self._entry("summary", u"2列2番"),
            self._entry("summary", u"2列3番"),
            self._entry("summary", u"2列10番"),
            ])

    def test_with_block(self):
        entries=[
            self._entry("summary", u"2列3番"),
            self._entry("summary", u"2列1番"),
            self._entry("summary", u"Aブロック1列1番"),
            self._entry("summary", u"Aブロック2列1番"),
            self._entry("summary", u"Aブロック1列2番"),
            self._entry("summary", u"Bブロック1列1番"),
            ]
        result = self._callFUT(entries)

        self.assertEqual(result, [
            self._entry("summary", u"2列1番"),
            self._entry("summary", u"2列3番"),
            self._entry("summary", u"Aブロック1列1番"),
            self._entry("summary", u"Aブロック1列2番"),
            self._entry("summary", u"Aブロック2列1番"),
            self._entry("summary", u"Bブロック1列1番"),
            ])

    def test_with_no_seat(self):
        entries=[
            self._entry("summary", u"2列3番"),
            self._entry("summary", u"2列1番"),
            self._entry("summary"),
            self._entry("another"),
            ]
        result = self._callFUT(entries)

        self.assertEqual(result, [
            self._entry("summary", u"2列1番"),
            self._entry("summary", u"2列3番"),
            self._entry("another"),
            self._entry("summary"),
            ])
        
if __name__ == "__main__":
    unittest.main()
