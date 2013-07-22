import unittest
from datetime import datetime
from altair.app.ticketing.testing import _setup_db, _teardown_db

class CancelFilterTests(unittest.TestCase):
    def setUp(self):
        self.session = _setup_db([
            "altair.app.ticketing.lots.models",
            ])

    def tearDown(self):
        _teardown_db()

    def _getTarget(self):
        from ..import authcancel
        return authcancel.CancelFilter

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_no_data(self):
        order_no = "testing"
        
        target = self._makeOne()
        result = target.is_cancelable(order_no)

        self.assertTrue(result)

    def test_closed_data(self):
        from .. import models
        order_no = "testing"
        entry = models.LotEntry(entry_no=order_no,
                                closed_at=datetime.now())
        self.session.add(entry)
        target = self._makeOne()
        result = target.is_cancelable(order_no)

        self.assertTrue(result)

    def test_entry_data(self):
        from .. import models
        order_no = "testing"
        entry = models.LotEntry(entry_no=order_no)

        self.session.add(entry)
        target = self._makeOne()
        result = target.is_cancelable(order_no)

        self.assertFalse(result)
