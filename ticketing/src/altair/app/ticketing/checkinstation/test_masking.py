# -*- coding:utf-8 -*-
import unittest
from datetime import datetime

def setUpModule():
    from altair.app.ticketing.testing import _setup_db
    _setup_db([
        "altair.app.ticketing.core.models", 
        "altair.app.ticketing.checkinstation.models", 
           ], echo=False)

def tearDownModule():
    from altair.app.ticketing.testing import _teardown_db
    _teardown_db()

class FixtureFactory(object):
    def __init__(self):
        self.item_id = 0
        self.serial = "x"
        self.operator_id = 1
        self.device_id = "test device this is"
        self.secret = "this is secret"

    def Token(self, id):
        from altair.app.ticketing.core.models import OrderedProductItemToken
        self.item_id += 1
        self.serial += "x"
        return OrderedProductItemToken(id=id, 
                                       ordered_product_item_id=self.item_id, 
                                       serial=self.serial
        )

    def Identity(self, id):
        from altair.app.ticketing.checkinstation.models import CheckinIdentity
        return CheckinIdentity(id=id, 
                               operator_id=self.operator_id,
                               device_id=self.device_id, 
                               secret=self.secret
        )

class MaskingTokenTests(unittest.TestCase):
    def tearDown(self):
        import transaction
        transaction.abort()

    def _getTarget(self):
        from altair.app.ticketing.checkinstation.masking import TokenReservationFilter
        return TokenReservationFilter

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_new__empty(self):
        """初回は全部印刷できる"""
        from altair.app.ticketing.models import DBSession as session
        fixture = FixtureFactory()

        request = None
        identity = fixture.Identity(id=1111)
        token_list = [fixture.Token(id=1), 
                      fixture.Token(id=2), 
                  ]
        session.add_all(token_list)

        target = self._makeOne(request, identity, token_list)
        now = datetime(2000, 1, 1)
        unmasked, masked = target.get_partationed_reservations(now)

        self.assertEqual(masked, [])
        self.assertEqual(len(unmasked), 2)
        self.assertTrue(unmasked[0].token in token_list)
        self.assertTrue(unmasked[1].token in token_list)

    def test_new__masking_by_other(self):
        """他の端末が印刷処理に入っていたら印刷できない"""
        from altair.app.ticketing.models import DBSession as session
        from altair.app.ticketing.checkinstation.models import CheckinTokenReservation
        fixture = FixtureFactory()

        request = None
        identity = fixture.Identity(id=1111)
        token_list = [fixture.Token(id=1), 
                      fixture.Token(id=2), 
                  ]
        session.add_all(token_list)

        ### 他端末が既に発券作業をしている
        another_identity = fixture.Identity(id=2222)
        reservations = []
        for token in token_list:
            r = CheckinTokenReservation(token=token,
                                        identity=another_identity,
                                        expire_at=datetime(2000, 1, 1))
            session.add(r)
            reservations.append(r)


        target = self._makeOne(request, identity, token_list)
        now = datetime(2000, 1, 1)
        unmasked, masked = target.get_partationed_reservations(now)

        self.assertEqual(len(masked), 2)
        self.assertTrue(masked[0] in reservations)
        self.assertTrue(masked[1] in reservations)
        self.assertEqual(unmasked, [])

        ## 事前に登録しておいたものと選択不可能なものが等しい
        self.assertEqual(sorted(masked), sorted(reservations))

    def test_new__masking_by_other__but_expired(self):
        """他の端末が印刷処理に入ってもexpireされていたら印刷できる"""
        from altair.app.ticketing.models import DBSession as session
        from altair.app.ticketing.checkinstation.models import CheckinTokenReservation
        fixture = FixtureFactory()

        request = None
        identity = fixture.Identity(id=1111)
        token_list = [fixture.Token(id=1), 
                      fixture.Token(id=2), 
                  ]
        session.add_all(token_list)

        ### 他端末が既に発券作業をしている(1999)
        another_identity = fixture.Identity(id=2222)
        reservations = []
        for token in token_list:
            r = CheckinTokenReservation(token=token,
                                        identity=another_identity,
                                        expire_at=datetime(1999, 1, 1))
            session.add(r)
            reservations.append(r)


        target = self._makeOne(request, identity, token_list)
        now = datetime(2000, 1, 1)
        unmasked, masked = target.get_partationed_reservations(now)


        self.assertEqual(masked, [])
        self.assertEqual(len(unmasked), 2)
        self.assertTrue(unmasked[0].token in token_list)
        self.assertTrue(unmasked[1].token in token_list)

        ## 事前に登録しておいたものと選択可能なものが等しい
        self.assertEqual(sorted(unmasked), sorted(reservations))

    def test_forward__masking_by_self(self):
        """自分自身が印刷処理に入ったものの、ちょっと戻ってしまった場合ももちろん印刷できる"""
        from altair.app.ticketing.models import DBSession as session
        from altair.app.ticketing.checkinstation.models import CheckinTokenReservation
        fixture = FixtureFactory()

        request = None
        identity = fixture.Identity(id=1111)
        token_list = [fixture.Token(id=1), 
                      fixture.Token(id=2), 
                  ]
        session.add_all(token_list)

        reservations = []
        for token in token_list:
            r = CheckinTokenReservation(token=token,
                                        identity=identity,
                                        expire_at=datetime(2000, 1, 1))
            session.add(r)
            reservations.append(r)


        target = self._makeOne(request, identity, token_list)
        now = datetime(2000, 1, 1)
        unmasked, masked = target.get_partationed_reservations(now)


        self.assertEqual(masked, [])
        self.assertEqual(len(unmasked), 2)
        self.assertTrue(unmasked[0].token in token_list)
        self.assertTrue(unmasked[1].token in token_list)

        ## 事前に登録しておいたものと選択可能なものが等しい
        self.assertEqual(sorted(unmasked), sorted(reservations))
