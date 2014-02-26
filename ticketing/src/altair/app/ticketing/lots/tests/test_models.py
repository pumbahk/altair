# -*- coding:utf-8 -*-

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

    def _entry(self, email=None, lot=None, entry_no=None,
               elected_at=None, canceled_at=None, rejected_at=None):
        from altair.app.ticketing.core.models import ShippingAddress
        from altair.app.ticketing.lots.models import LotEntry
        return LotEntry(lot=lot,
                        entry_no=entry_no,
                        elected_at=elected_at,
                        canceled_at=canceled_at,
                        rejected_at=rejected_at,
                        shipping_address=ShippingAddress(email_1=email))

    def _wish(self, email=None, lot=None, entry_no=None, wish_order=0):
        from altair.app.ticketing.lots.models import LotEntryWish
        entry = self._entry(email, lot=lot, entry_no=entry_no)
        wish = LotEntryWish(lot_entry=entry,
                            wish_order=wish_order)
        return wish


    def test_remained_entries_empty(self):
        target = self._makeOne()
        self.assertEqual(target.remained_entries, [])

    def test_remained_entries(self):
        from datetime import datetime
        target = self._makeOne()
        # 当選
        self._entry(entry_no="testing-elected",
                    lot=target, elected_at=datetime.now())
        # 落選
        self._entry(entry_no="testing-rejected",
                    lot=target, rejected_at=datetime.now())
        # キャンセル
        self._entry(entry_no="testing-canceled",
                    lot=target, canceled_at=datetime.now())

        # 申込のみ
        self._entry(entry_no="testing-accepted",
                    lot=target)

        self.session.add(target)
        self.session.flush()

        self.assertEqual([e.entry_no for e in target.remained_entries],
                         ['testing-rejected',
                          'testing-canceled'])

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

    def test_electing_wishes_empty(self):
        target = self._makeOne(entry_limit=5)
        result = target.electing_wishes([])
        self.assertEqual(result, 0)

    def test_electing_wishes_one(self):
        from ..models import LotElectWork
        target = self._makeOne(entry_limit=5)
        self._wish(lot=target,
                   email="testing@example.com",
                   entry_no="testing",
                   wish_order=2)
        self.session.add(target)
        result = target.electing_wishes([
            ('testing', 2),
        ])
        self.assertEqual(result, 1)
        self.assertEqual(self.session.query(LotElectWork).filter(
            LotElectWork.lot_id==target.id,
            LotElectWork.lot_entry_no=='testing',
            LotElectWork.wish_order==2,
            LotElectWork.entry_wish_no=='testing-2',
        ).count(), 1)

    def test_electing_wishes_dup(self):
        from ..models import LotElectWork
        target = self._makeOne(entry_limit=5)
        self._wish(lot=target,
                   email="testing@example.com",
                   entry_no="testing",
                   wish_order=2)
        self.session.add(
            LotElectWork(
                lot_id=target.id,
                lot_entry_no='testing',
                wish_order=2,
                entry_wish_no='testing-2',
            ),
        )

        result = target.electing_wishes([
            ('testing', 2),
        ])
        self.assertEqual(result, 0)
        self.assertEqual(self.session.query(LotElectWork).filter(
            LotElectWork.lot_id==target.id,
            LotElectWork.lot_entry_no=='testing',
            LotElectWork.wish_order==2,
        ).count(), 1)


    def test_rejectable_entries(self):
        target = self._makeOne(entry_limit=5)
        self.session.add(target)
        self.session.flush()

        result = target.rejectable_entries

        self.assertEqual(result, [])

    def test_rejectable_entries_one(self):
        from datetime import datetime
        from ..models import LotElectWork, LotRejectWork
        target = self._makeOne(entry_limit=5)
        self._entry(lot=target,
                   email="testing@example.com",
                   entry_no="testing-rejectable")
        self._entry(lot=target,
                    email="testing@example.com",
                    entry_no="testing-elected",
                    elected_at=datetime.now())
        self._entry(lot=target,
                    email="testing@example.com",
                    entry_no="testing-rejected",
                    rejected_at=datetime.now())
        self._entry(lot=target,
                    email="testing@example.com",
                    entry_no="testing-canceled",
                    canceled_at=datetime.now())
        self._entry(lot=target,
                   email="testing@example.com",
                   entry_no="testing-electing")
        LotElectWork(lot=target,
                     lot_entry_no="testing-electing")
        self._entry(lot=target,
                   email="testing@example.com",
                   entry_no="testing-rejecting")
        LotRejectWork(lot=target,
                      lot_entry_no='testing-rejecting')
        self.session.add(target)
        self.session.flush()

        result = target.rejectable_entries

        self.assertEqual([l.entry_no for l in result],
                         ["testing-rejectable"])

    def test_available_on_app_context(self):
        from altair.app.ticketing.core.models import SalesSegment
        from datetime import datetime
        target = self._makeOne(
            sales_segment=SalesSegment(
                start_at=None,
                end_at=None
                )
            )
        self.assertTrue(target.available_on(datetime(1990, 1, 1)))
        self.assertTrue(target.available_on(datetime(2000, 1, 1)))
        self.assertTrue(target.available_on(datetime(2010, 1, 1)))

        target = self._makeOne(
            sales_segment=SalesSegment(
                start_at=datetime(2000, 1, 1),
                end_at=None
                )
            )
        self.assertFalse(target.available_on(datetime(1990, 1, 1)))
        self.assertTrue(target.available_on(datetime(2000, 1, 1)))
        self.assertTrue(target.available_on(datetime(2010, 1, 1)))

        target = self._makeOne(
            sales_segment=SalesSegment(
                start_at=datetime(2000, 1, 1),
                end_at=datetime(2005, 1, 1)
                )
            )
        self.assertFalse(target.available_on(datetime(1990, 1, 1)))
        self.assertTrue(target.available_on(datetime(2000, 1, 1)))
        self.assertFalse(target.available_on(datetime(2010, 1, 1)))


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
        from altair.app.ticketing.core.models import PaymentDeliveryMethodPair,\
            SalesSegment, FeeTypeEnum
            
        from ..models import LotEntry, Lot
        
        system_fee = 315

        pdmp = PaymentDeliveryMethodPair(system_fee=system_fee,
                                         system_fee_type=FeeTypeEnum.Once.v[0])
        ss = SalesSegment()
        lot = Lot(sales_segment=ss)
        lot_entry = LotEntry(payment_delivery_method_pair=pdmp, lot=lot)
        
        target = self._makeOne(lot_entry=lot_entry)
        self.assertEqual(target.system_fee, system_fee)
