from unittest import TestCase
import logging

class DummyHandler(logging.Handler):
    def __init__(self, *args, **kwargs):
        super(DummyHandler, self).__init__(*args, **kwargs)
        self.records = []

    def emit(self, record):
        self.records.append(record)

class SpoolingHandlerTest(TestCase):
    def test(self):
        from .handlers import SpoolingHandler
        dummy = DummyHandler()
        h = SpoolingHandler(capacity=5000, target=dummy, flushLevel=logging.INFO)
        records = [
            logging.LogRecord('name', logging.DEBUG, 'pathname', 1, 'msg', (), None),
            logging.LogRecord('name', logging.DEBUG, 'pathname', 2, 'msg', (), None),
            logging.LogRecord('name', logging.INFO, 'pathname', 3, 'msg', (), None),
            logging.LogRecord('name', logging.DEBUG, 'pathname', 4, 'msg', (), None),
            ]
        h.handle(records[0])
        h.handle(records[1])
        self.assertEqual([], dummy.records)
        h.handle(records[2])
        h.handle(records[3])
        self.assertEqual(records, dummy.records)
