import unittest
from altair.app.ticketing.testing import _setup_db, _teardown_db

class LotTests(unittest.TestCase):
    def setUp(self):
        self.session = _setup_db(
            [
                'altair.app.ticketing.lots.models',
            ])

    def tearDown(self):
        _teardown_db()

    def _getTarget(self):
        from ..models import Lot
        return Lot

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def _entry(self, email):
        from altair.app.ticketing.core.models import ShippingAddress
        from altair.app.ticketing.lots.models import LotEntry
        return LotEntry(shipping_address=ShippingAddress(email_1=email))


    def test_remained_entries_empty(self):
        target = self._makeOne()
        self.assertEqual(target.remained_entries, [])

    def test_check_entry_limit_no_check(self):
        email = 'test@example.com'
        entry = self._entry(email)
        target = self._makeOne(entry_limit=0)
        target.entries.append(entry)
        self.session.add(target)
        self.session.flush()
        result = target.check_entry_limit(email)
        self.assertTrue(result)

    def test_check_entry_limit_ng(self):
        email = 'test@example.com'
        entry = self._entry(email)
        target = self._makeOne(entry_limit=1)
        target.entries.append(entry)
        self.session.add(target)
        self.session.flush()
        result = target.check_entry_limit(email)

        self.assertFalse(result)

    def test_check_entry_limit_ok(self):
        email = 'test@example.com'
        target = self._makeOne(entry_limit=1)
        self.session.add(target)
        self.session.flush()
        result = target.check_entry_limit(email)

        self.assertTrue(result)

    def test_check_entry_limit_many_ok(self):
        email = 'test@example.com'
        target = self._makeOne(entry_limit=5)
        entry = self._entry(email)
        for i in range(4):
            target.entries.append(entry)
            self.session.add(target)
        self.session.flush()
        result = target.check_entry_limit(email)

        self.assertTrue(result)

    def test_check_entry_limit_many_ng(self):
        email = 'test@example.com'
        target = self._makeOne(entry_limit=5)
        for i in range(5):
            entry = self._entry(email)
            target.entries.append(entry)
        self.session.add(target)
        self.session.flush()
        result = target.check_entry_limit(email)

        self.assertFalse(result)


class LotEntryTests(unittest.TestCase):
    def _getTarget(self):
        from ..models import LotEntry
        return LotEntry

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_elect(self):
        from ..models import LotEntryWish
        target = self._makeOne()
        target.wishes = [LotEntryWish(),
                         LotEntryWish(),
                         LotEntryWish()]

        result = target.elect(target.wishes[1])

        self.assertIsNotNone(target.elected_at)
        self.assertIsNone(target.wishes[0].elected_at)
        self.assertIsNotNone(target.wishes[1].elected_at)
        self.assertIsNone(target.wishes[2].elected_at)
        self.assertEqual(result.lot_entry, target)

    def test_reject(self):
        from ..models import LotEntryWish
        target = self._makeOne()
        target.wishes = [LotEntryWish(),
                         LotEntryWish(),
                         LotEntryWish()]

        result = target.reject()

        self.assertIsNotNone(target.rejected_at)
        self.assertIsNotNone(target.wishes[0].rejected_at)
        self.assertIsNotNone(target.wishes[1].rejected_at)
        self.assertIsNotNone(target.wishes[2].rejected_at)
        self.assertEqual(result.lot_entry, target)

class LotEntryWishTests(unittest.TestCase):
    def _getTarget(self):
        from ..models import LotEntryWish
        return LotEntryWish

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_system_fee(self):
        from altair.app.ticketing.core.models import PaymentDeliveryMethodPair
        from ..models import LotEntry
        target = self._makeOne(lot_entry=LotEntry(payment_delivery_method_pair=PaymentDeliveryMethodPair(system_fee=315)))

        self.assertEqual(target.system_fee, 315)
