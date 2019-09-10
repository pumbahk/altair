# -*- coding:utf-8 -*-
import unittest
from pyramid.testing import DummyModel
from altair.app.ticketing.testing import _setup_db, _teardown_db
from altair.app.ticketing.core.testing import CoreTestMixin


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


class GetQuantityForStockIdFromCart(unittest.TestCase):
    def setUp(self):
        self._make_test_data()

    @staticmethod
    def _call_test_target(*args, **kwargs):
        from altair.app.ticketing.cart_api.view_support import get_quantity_for_stock_id_from_cart
        return get_quantity_for_stock_id_from_cart(*args, **kwargs)

    def _make_test_data(self):
        self._stock_quantity_only_1 = DummyModel(id=1, stock_type=DummyModel(quantity_only=1))
        self._cpi_quantity_only_1 = DummyModel(
            quantity=1,
            product_item=DummyModel(
                stock_id=self._stock_quantity_only_1.id,
                stock=self._stock_quantity_only_1
            ),
            deleted_at=None
        )
        self._stock_quantity_only_2 = DummyModel(id=2, stock_type=DummyModel(quantity_only=1))
        self._cpi_quantity_only_2 = DummyModel(
            quantity=1,
            product_item=DummyModel(
                stock_id=self._stock_quantity_only_2.id,
                stock=self._stock_quantity_only_2
            ),
            deleted_at=None
        )
        self._stock_with_seat_1 = DummyModel(id=3, stock_type=DummyModel(quantity_only=0))
        self._cpi_with_seat_1 = DummyModel(
            seats=[DummyModel()],
            product_item=DummyModel(
                stock_id=self._stock_with_seat_1.id,
                stock=self._stock_with_seat_1
            ),
            deleted_at=None
        )
        self._stock_with_seat_2 = DummyModel(id=4, stock_type=DummyModel(quantity_only=0))
        self._cpi_with_seat_2 = DummyModel(
            seats=[DummyModel()],
            product_item=DummyModel(
                stock_id=self._stock_with_seat_2.id,
                stock=self._stock_with_seat_2
            ),
            deleted_at=None
        )

    def test_single_stock_quantity_only(self):
        """ 正常系 数受けで単一在庫のケース  """
        test_carted_product = DummyModel(
            elements=[self._cpi_quantity_only_1, self._cpi_quantity_only_1],
            deleted_at=None
        )
        test_cart = DummyModel(items=[test_carted_product, test_carted_product])
        result_dict = self._call_test_target(test_cart)
        self.assertEqual(result_dict[self._stock_quantity_only_1.id], 4)

    def test_multi_stock_quantity_only(self):
        """ 正常系 数受けで複数種類在庫のケース  """
        test_carted_product_1 = DummyModel(
            elements=[self._cpi_quantity_only_1, self._cpi_quantity_only_1],
            deleted_at=None
        )
        test_carted_product_2 = DummyModel(
            elements=[self._cpi_quantity_only_2, self._cpi_quantity_only_2, self._cpi_quantity_only_2],
            deleted_at=None
        )
        test_cart = DummyModel(items=[test_carted_product_1, test_carted_product_2])
        result_dict = self._call_test_target(test_cart)
        self.assertEqual(result_dict[self._stock_quantity_only_1.id], 2)
        self.assertEqual(result_dict[self._stock_quantity_only_2.id], 3)

    def test_single_stock_with_seat(self):
        """ 正常系 席ありで単一在庫のケース  """
        test_carted_product = DummyModel(
            elements=[self._cpi_with_seat_1, self._cpi_with_seat_1],
            deleted_at=None
        )
        test_cart = DummyModel(items=[test_carted_product, test_carted_product])
        result_dict = self._call_test_target(test_cart)
        self.assertEqual(result_dict[self._stock_with_seat_1.id], 4)

    def test_multi_stock_with_seat(self):
        """ 正常系 席ありで複数種類在庫のケース  """
        test_carted_product_1 = DummyModel(
            elements=[self._cpi_with_seat_1, self._cpi_with_seat_1],
            deleted_at=None
        )
        test_carted_product_2 = DummyModel(
            elements=[self._cpi_with_seat_2, self._cpi_with_seat_2, self._cpi_with_seat_2],
            deleted_at=None
        )
        test_cart = DummyModel(items=[test_carted_product_1, test_carted_product_2])
        result_dict = self._call_test_target(test_cart)
        self.assertEqual(result_dict[self._stock_with_seat_1.id], 2)
        self.assertEqual(result_dict[self._stock_with_seat_2.id], 3)


class UpdateDifferentStocksAfterProductSelection(unittest.TestCase, CoreTestMixin):
    def setUp(self):
        self._session = _setup_db(
            modules=[
                'altair.app.ticketing.core.models',
                'altair.app.ticketing.cart.models',
                'altair.app.ticketing.orders.models'
            ]
        )
        CoreTestMixin.setUp(self)
        self._make_test_data()

    def tearDown(self):
        _teardown_db()

    @staticmethod
    def _call_test_target(*args, **kwargs):
        from altair.app.ticketing.cart_api.view_support import update_different_stocks_after_product_selection
        return update_different_stocks_after_product_selection(*args, **kwargs)

    def _make_test_data(self):
        from altair.app.ticketing.core.models import StockType, StockHolder, Stock, StockStatus

        self.stock_type = StockType(id=1)
        self._session.add(self.stock_type)

        self.stock_holder_own = StockHolder(id=1,)
        self.stock_holder_other = StockHolder(id=2)
        self._session.add_all([self.stock_holder_own, self.stock_holder_other])

        self._session.add(self.performance)
        self._session.flush()

        self.stock_own = Stock(
            id=1,
            performance_id=self.performance.id,
            stock_type_id=self.stock_type.id,
            stock_holder_id=self.stock_holder_own.id,
            quantity=100
        )
        self.stock_other = Stock(
            id=2,
            performance_id=self.performance.id,
            stock_type_id=self.stock_type.id,
            stock_holder_id=self.stock_holder_other.id,
            quantity=50
        )
        self._session.add_all([self.stock_own, self.stock_other])

        self.stock_status_own = StockStatus(
            stock_id=self.stock_own.id,
            quantity=95
        )
        self.stock_status_other = StockStatus(
            stock_id=self.stock_other.id,
            quantity=self.stock_other.quantity
        )
        self._session.add_all([self.stock_status_own, self.stock_status_other])

    def test_success(self):
        """ 正常系 商品割当前後で在庫が異なるケース """
        test_stock_diff = 3
        test_quantity_for_stock_id_before = {
            self.stock_own.id: self.stock_own.quantity - self.stock_status_own.quantity
        }
        test_quantity_for_stock_id_after = {
            self.stock_own.id: self.stock_own.quantity - self.stock_status_own.quantity - test_stock_diff,
            self.stock_other.id: test_stock_diff,
        }
        stock_own_quantity_before = self.stock_status_own.quantity
        stock_other_quantity_before = self.stock_status_other.quantity

        self._call_test_target(self._session, test_quantity_for_stock_id_before, test_quantity_for_stock_id_after)
        self.assertEqual(self.stock_status_own.quantity - stock_own_quantity_before, test_stock_diff)
        self.assertEqual(stock_other_quantity_before - self.stock_status_other.quantity, test_stock_diff)

    def test_no_stock_status_before_product_selection(self):
        """ 異常系 商品割当前のStockStatusが存在しない """
        from altair.app.ticketing.cart_api.exceptions import NoStockStatusException
        test_stock_diff = 3
        test_quantity_for_stock_id_before = {
            -1: self.stock_own.quantity - self.stock_status_own.quantity
        }
        test_quantity_for_stock_id_after = {
            self.stock_own.id: self.stock_own.quantity - self.stock_status_own.quantity - test_stock_diff,
            self.stock_other.id: test_stock_diff,
        }
        with self.assertRaises(NoStockStatusException):
            self._call_test_target(self._session, test_quantity_for_stock_id_before, test_quantity_for_stock_id_after)

    def test_no_stock_status_after_product_selection(self):
        """ 異常系 商品割当後のStockStatusが存在しない """
        from altair.app.ticketing.cart_api.exceptions import NoStockStatusException
        test_stock_diff = 3
        test_quantity_for_stock_id_before = {
            self.stock_own.id: self.stock_own.quantity - self.stock_status_own.quantity
        }
        test_quantity_for_stock_id_after = {
            self.stock_own.id: self.stock_own.quantity - self.stock_status_own.quantity - test_stock_diff,
            -1: test_stock_diff,
        }
        with self.assertRaises(NoStockStatusException):
            self._call_test_target(self._session, test_quantity_for_stock_id_before, test_quantity_for_stock_id_after)

    def test_no_enough_stock_after_product_selection(self):
        """ 異常系 商品割当後の在庫が不足している """
        from altair.app.ticketing.cart.stocker import NotEnoughStockException
        test_stock_diff = 3
        test_quantity_for_stock_id_before = {
            self.stock_own.id: self.stock_own.quantity - self.stock_status_own.quantity
        }
        test_quantity_for_stock_id_after = {
            self.stock_own.id: self.stock_own.quantity - self.stock_status_own.quantity - test_stock_diff,
            self.stock_other.id: test_stock_diff,
        }
        self.stock_other.quantity = 2
        self.stock_status_other.quantity = 2
        with self.assertRaises(NotEnoughStockException):
            self._call_test_target(self._session, test_quantity_for_stock_id_before, test_quantity_for_stock_id_after)
