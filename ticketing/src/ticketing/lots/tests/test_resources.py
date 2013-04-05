import unittest
from pyramid import testing
from ticketing.testing import _setup_db,_teardown_db
from ..testing import _add_lots



class LotResourceTests(unittest.TestCase):
    def setUp(self):
        self.session = _setup_db(modules=[
            'ticketing.lots.models',
            ])

    def tearDown(self):
        _teardown_db()

    def _getTarget(self):
        from ..resources import LotResource
        return LotResource

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)


    def test_it(self):
        request = testing.DummyRequest()
        target = self._makeOne(request)

        self.assertEqual(target.request, request)


    def test_lot_none(self):
        request = testing.DummyRequest(
            matchdict={'lot_id': '8888'},
        )
        target = self._makeOne(request)

        self.assertEqual(target.lot, None)

    def test_lot(self):
        lot, products = _add_lots(self.session, [], [])
        request = testing.DummyRequest(
            matchdict={'lot_id': str(lot.id),
                       'event_id': str(lot.event.id)},
            
        )
        target = self._makeOne(request)

        self.assertEqual(target.lot, lot)

    def test_event(self):
        lot, products = _add_lots(self.session, [], [])
        request = testing.DummyRequest(
            matchdict={'lot_id': str(lot.id),
                       'event_id': str(lot.event.id)},
            
        )
        target = self._makeOne(request)

        self.assertEqual(target.event, lot.event)        
