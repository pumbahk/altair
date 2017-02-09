# -*- coding:utf-8 -*-
from unittest import TestCase
from nose.tools import ok_, eq_
import mock

from .api import can_use_coupon, can_use_coupon_order, get_host


class APITestCase(TestCase):
    @staticmethod
    def test_can_use_coupon():
        pass

    @staticmethod
    def test_can_use_coupon_order():
        order = mock.MagicMock(printed_at=False)
        ret = can_use_coupon_order(None, order)
        eq_(ret, True)

        order = mock.MagicMock(printed_at=True)
        ret = can_use_coupon_order(None, order)
        eq_(ret, False)

    @staticmethod
    def test_get_host():
        pass
