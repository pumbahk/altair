import unittest
from pyramid import testing
from ticketing.testing import _setup_db, _teardown_db
from altair.mq.testing import DummyMessage


class lot_wish_cartTests(unittest.TestCase):
    def _callFUT(self, *args, **kwargs):
        from ..workers import lot_wish_cart
        return lot_wish_cart(*args, **kwargs)

    def test_it(self):
        from ticketing.core.models import Performance
        from ..models import LotEntryWish, LotEntry, Lot
        wish = LotEntryWish(
            performance=Performance(),
            lot_entry=LotEntry(lot=Lot(),
                               entry_no='testing-entry'))
        result = self._callFUT(wish)

        self.assertEqual(result.order_no, 'testing-entry')


class WorkerResourceTests(unittest.TestCase):
    def setUp(self):
        self.session = _setup_db(modules=[
            'ticketing.core.models',
            'ticketing.lots.models',
        ])

    def tearDown(self):
        _teardown_db()

    def _add_lot(self):
        from ..models import Lot
        lot = Lot()
        self.session.add(lot)
        self.session.flush()
        return lot

    def _getTarget(self):
        from ..workers import WorkerResource
        return WorkerResource

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_lot(self):
        lot = self._add_lot()
        lot_id = str(lot.id)
        message = DummyMessage(params={'lot_id': lot_id})
        target = self._makeOne(message=message)

        self.assertEqual(target.lot_id, lot_id)
        self.assertEqual(target.lot, lot)

class elect_lots_taskTests(unittest.TestCase):
    def _callFUT(self, *args, **kwargs):
        from ..workers import elect_lots_task
        return elect_lots_task(*args, **kwargs)

    def test_no_lot(self):
        context = testing.DummyResource(
            lot_id='testing',
            lot=None,
        )
        dummy_message = DummyMessage()
        self._callFUT(context, dummy_message)
