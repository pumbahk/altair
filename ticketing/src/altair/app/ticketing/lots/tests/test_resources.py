import unittest
from pyramid import testing
from altair.app.ticketing.testing import _setup_db,_teardown_db, DummyRequest
from ..testing import _add_lots


class LotResourceTests(unittest.TestCase):
    def setUp(self):
        self.session = _setup_db(modules=[
            'altair.app.ticketing.core.models',
            'altair.app.ticketing.lots.models',
            ])
        from altair.app.ticketing.core.models import Host, Organization
        organization = Organization(short_name='testing')
        host = Host(host_name='example.com:80', organization=organization)
        self.session.add(host)

    def tearDown(self):
        _teardown_db()

    def _getTarget(self):
        from ..resources import LotResource
        return LotResource

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)


    def test_it(self):
        request = DummyRequest()
        target = self._makeOne(request)

        self.assertEqual(target.request, request)


    def test_lot_none(self):
        request = DummyRequest(
            matchdict={'lot_id': '8888'},
        )
        target = self._makeOne(request)

        self.assertEqual(target.lot, None)

    def test_lot(self):
        lot, products = _add_lots(self.session, [], [])
        request = DummyRequest(
            matchdict={'lot_id': str(lot.id),
                       'event_id': str(lot.event.id)},
            
        )
        target = self._makeOne(request)

        self.assertEqual(target.lot, lot)

    def test_event(self):
        lot, products = _add_lots(self.session, [], [])
        request = DummyRequest(
            matchdict={'lot_id': str(lot.id),
                       'event_id': str(lot.event.id)},
            
        )
        target = self._makeOne(request)

        self.assertEqual(target.event, lot.event)        
