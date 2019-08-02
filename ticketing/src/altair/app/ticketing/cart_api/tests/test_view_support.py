# -*- coding:utf-8 -*-
import unittest
from pyramid.testing import DummyModel


class ValidateSeatsInCartTest(unittest.TestCase):
    @staticmethod
    def _call_test_target(*args, **kwargs):
        from altair.app.ticketing.cart_api.view_support import validate_seats_in_cart
        return validate_seats_in_cart(*args, **kwargs)

    @staticmethod
    def _make_test_cart_with_seats():
        test_carted_product_items_1 = [
            DummyModel(seats=[
                DummyModel(l0_id=u'TEST-1-1'),
                DummyModel(l0_id=u'TEST-1-2'),
            ]),
            DummyModel(seats=[
                DummyModel(l0_id=u'TEST-1-3'),
                DummyModel(l0_id=u'TEST-1-4'),
            ])
        ]
        test_carted_product_items_2 = [
            DummyModel(seats=[
                DummyModel(l0_id=u'TEST-2-1'),
                DummyModel(l0_id=u'TEST-2-2'),
            ]),
            DummyModel(seats=[
                DummyModel(l0_id=u'TEST-2-3'),
                DummyModel(l0_id=u'TEST-2-4'),
            ])
        ]
        return DummyModel(
            order_no=u'TEST00001',
            items=[
                DummyModel(elements=test_carted_product_items_1),
                DummyModel(elements=test_carted_product_items_2)
            ]
        )

    @staticmethod
    def _make_test_cart_with_no_seats():
        test_carted_product_items_1 = [DummyModel(seats=[]), DummyModel(seats=[])]
        test_carted_product_items_2 = [DummyModel(seats=[]), DummyModel(seats=[])]
        return DummyModel(
            order_no=u'TEST00001',
            items=[
                DummyModel(elements=test_carted_product_items_1),
                DummyModel(elements=test_carted_product_items_2)
            ]
        )

    def test_validate_seats_in_cart(self):
        """ validate_seats_in_cartの正常系テスト 席ありの場合 """
        from random import shuffle

        test_cart_with_seat = self._make_test_cart_with_seats()
        test_request_seat_l0_ids = [u'TEST-1-1', u'TEST-1-2', u'TEST-1-3', u'TEST-1-4', u'TEST-2-1', u'TEST-2-2',
                                    u'TEST-2-3', u'TEST-2-4']
        shuffle(test_request_seat_l0_ids)

        self._call_test_target(test_cart_with_seat, test_request_seat_l0_ids)

    def test_validate_seats_in_cart_with_quantity_only(self):
        """ validate_seats_in_cartの正常系テスト 数受けの場合 """
        test_cart_with_no_seats = self._make_test_cart_with_no_seats()
        test_request_seat_l0_ids = []

        self._call_test_target(test_cart_with_no_seats, test_request_seat_l0_ids)

    def test_validate_seats_in_cart_mismatch_number_of_seat(self):
        """ validate_seats_in_cartの異常系テスト 席数がミスマッチ """
        from altair.app.ticketing.cart_api.exceptions import MismatchSeatInCartException
        test_cart_with_seat = self._make_test_cart_with_seats()
        test_request_seat_l0_ids = [u'TEST-1-1', u'TEST-1-2', u'TEST-1-3']

        with self.assertRaises(MismatchSeatInCartException):
            self._call_test_target(test_cart_with_seat, test_request_seat_l0_ids)

    def test_validate_seats_in_cart_mismatch_l0_id(self):
        """ validate_seats_in_cartの異常系テスト l0_idがミスマッチ """
        from altair.app.ticketing.cart_api.exceptions import MismatchSeatInCartException
        from random import shuffle
        test_cart_with_seat = self._make_test_cart_with_seats()
        test_request_seat_l0_ids = [u'TEST-1-1', u'TEST-1-2', u'TEST-1-3', u'TEST-5-4', u'TEST-2-1', u'TEST-2-2',
                                    u'TEST-2-3', u'TEST-2-4']
        shuffle(test_request_seat_l0_ids)

        with self.assertRaises(MismatchSeatInCartException):
            self._call_test_target(test_cart_with_seat, test_request_seat_l0_ids)

    def test_validate_seats_in_cart_with_quantity_only_mismatch_number_of_seat(self):
        """ validate_seats_in_cartの異常系テスト 数受けなのに席を指定してくる場合 """
        from altair.app.ticketing.cart_api.exceptions import MismatchSeatInCartException
        test_cart_with_no_seats = self._make_test_cart_with_no_seats()
        test_request_seat_l0_ids = [u'TEST-1-1', u'TEST-1-2', u'TEST-1-3']

        with self.assertRaises(MismatchSeatInCartException):
            self._call_test_target(test_cart_with_no_seats, test_request_seat_l0_ids)
