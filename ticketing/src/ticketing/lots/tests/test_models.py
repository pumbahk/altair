import unittest

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
        from ticketing.core.models import PaymentDeliveryMethodPair
        from ..models import LotEntry
        target = self._makeOne(lot_entry=LotEntry(payment_delivery_method_pair=PaymentDeliveryMethodPair(system_fee=315)))

        self.assertEqual(target.system_fee, 315)
