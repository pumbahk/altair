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
        self.organization = Organization(short_name='testing')
        host = Host(host_name='example.com:80', organization=self.organization)
        self.session.add(host)

        from altair.sqlahelper import register_sessionmaker_with_engine
        self.config = testing.setUp()
        register_sessionmaker_with_engine(
            self.config.registry,
            'slave',
            self.session.bind
            )

    def tearDown(self):
        _teardown_db()

    def _getTarget(self):
        from ..resources import LotResource
        return LotResource

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def _entry(self, email=None, lot=None, entry_no=None,
               elected_at=None, canceled_at=None, rejected_at=None, performance=None):
        from altair.app.ticketing.core.models import ShippingAddress
        from altair.app.ticketing.lots.models import LotEntry, LotEntryWish
        wishes = []
        if performance is not None:
            wish = LotEntryWish(wish_order=1,
                                entry_wish_no=1,
                                performance=performance,
                                elected_at=elected_at,
                                canceled_at=canceled_at,
                                rejected_at=rejected_at)
            wishes.append(wish)
        return LotEntry(lot=lot,
                        entry_no=entry_no,
                        elected_at=elected_at,
                        canceled_at=canceled_at,
                        rejected_at=rejected_at,
                        shipping_address=ShippingAddress(email_1=email),
                        wishes=wishes)

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

    def test_check_entry_limit_no_check(self):
        lot, products = _add_lots(self.session, [], [])
        request = DummyRequest(
            matchdict={'lot_id': str(lot.id),
                       'event_id': str(lot.event.id)},
        )
        lot.entry_limit = 0
        email = 'test@example.com'
        entry = self._entry(email)
        lot.entries.append(entry)
        self.session.add(lot)
        self.session.flush()

        target = self._makeOne(request)
        result = target.check_entry_limit([], email=email)

        self.assertIsNone(result)

    def test_check_entry_limit_ng(self):
        from ..exceptions import OverEntryLimitException
        lot, products = _add_lots(self.session, [], [])
        request = DummyRequest(
            matchdict={'lot_id': str(lot.id),
                       'event_id': str(lot.event.id)},
        )
        lot.entry_limit = 1
        email = 'test@example.com'
        entry = self._entry(email)
        lot.entries.append(entry)
        self.session.add(lot)
        self.session.flush()

        target = self._makeOne(request)

        with self.assertRaises(OverEntryLimitException):
            target.check_entry_limit([], email=email)

    def test_check_entry_limit_ok(self):
        lot, products = _add_lots(self.session, [], [])
        request = DummyRequest(
            matchdict={'lot_id': str(lot.id),
                       'event_id': str(lot.event.id)},
        )
        lot.entry_limit = 1
        email = 'test@example.com'
        self.session.add(lot)
        self.session.flush()

        target = self._makeOne(request)
        result = target.check_entry_limit([], email=email)

        self.assertIsNone(result)

    def test_check_entry_limit_many_ok(self):
        lot, products = _add_lots(self.session, [], [])
        request = DummyRequest(
            matchdict={'lot_id': str(lot.id),
                       'event_id': str(lot.event.id)},
        )
        lot.entry_limit = 5
        email = 'test@example.com'
        entry = self._entry(email)
        for i in range(4):
            lot.entries.append(entry)
            self.session.add(lot)
        self.session.flush()

        target = self._makeOne(request)
        result = target.check_entry_limit([], email=email)

        self.assertIsNone(result)

    def test_check_entry_limit_many_ng(self):
        from ..exceptions import OverEntryLimitException
        lot, products = _add_lots(self.session, [], [])
        request = DummyRequest(
            matchdict={'lot_id': str(lot.id),
                       'event_id': str(lot.event.id)},
        )
        lot.entry_limit = 5
        email = 'test@example.com'
        for i in range(5):
            entry = self._entry(email)
            lot.entries.append(entry)
        self.session.add(lot)
        self.session.flush()

        target = self._makeOne(request)

        with self.assertRaises(OverEntryLimitException):
            target.check_entry_limit([], email=email)

    def test_check_entry_limit_performance_ok(self):
        from ..exceptions import OverEntryLimitException
        product_data = [{'name': u'Product-A', 'price': 100}]
        lot, products = _add_lots(self.session, product_data, [])
        request = DummyRequest(
            matchdict={'lot_id': str(lot.id),
                       'event_id': str(lot.event.id)},
        )
        lot.entry_limit = 0
        performance = lot.performances[0]
        performance.setting.entry_limit = 5
        performance.event.organization = self.organization
        email = 'test@example.com'
        wishes = []
        for i in range(4):
            entry = self._entry(email=email, performance=performance)
            lot.entries.append(entry)
            wishes.append(dict(performance_id=performance.id))
        self.session.add(lot)
        self.session.flush()

        target = self._makeOne(request)
        result = target.check_entry_limit(wishes, email=email)

        self.assertIsNone(result)

    def test_check_entry_limit_performance_ng(self):
        from ..exceptions import OverEntryLimitPerPerformanceException
        product_data = [{'name': u'Product-A', 'price': 100}]
        lot, products = _add_lots(self.session, product_data, [])
        request = DummyRequest(
            matchdict={'lot_id': str(lot.id),
                       'event_id': str(lot.event.id)},
        )
        lot.entry_limit = 0
        performance = lot.performances[0]
        performance.setting.entry_limit = 5
        performance.event.organization = self.organization
        email = 'test@example.com'
        wishes = []
        for i in range(5):
            entry = self._entry(email=email, performance=performance)
            lot.entries.append(entry)
            wishes.append(dict(performance_id=performance.id))
        self.session.add(lot)
        self.session.flush()

        target = self._makeOne(request)

        with self.assertRaises(OverEntryLimitPerPerformanceException):
            target.check_entry_limit(wishes, email=email)
