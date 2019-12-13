# -*- coding: utf-8 -*-

import unittest
import mock
from pyramid.testing import DummyModel


class CreateNewBarcodeTest(unittest.TestCase):
    @staticmethod
    def __call_test_target(*args, **kwargs):
        from altair.app.ticketing.skidata.api import create_new_barcode
        return create_new_barcode(*args, **kwargs)

    @mock.patch('altair.app.ticketing.skidata.api.SkidataBarcode.insert_new_barcode')
    @mock.patch('altair.app.ticketing.skidata.api.OrderedProductItemToken.find_all_by_order_no')
    def test_create_new_barcode_success(self, find_all_by_order_no, insert_new_barcode):
        """ create_new_barcodeの正常系テスト """
        # TODO SkidataへWhitelistを送信する場合としない場合のテストケースを追加
        # find_all_by_order_no.return_value = [DummyModel(id=1), DummyModel(id=2)]
        # self.__call_test_target(request=testing.DummyRequest(), order_no='TEST0000001')
        # self.assertTrue(insert_new_barcode.called)


class UpdateBarcodeToRereshOrder(unittest.TestCase):
    @staticmethod
    def __call_test_target(*args, **kwargs):
        from altair.app.ticketing.skidata.api import update_barcode_to_refresh_order
        return update_barcode_to_refresh_order(*args, **kwargs)

    @staticmethod
    def _create_token_with_quantity_only(token_id, item_name, serial):
        return DummyModel(
            id=token_id,
            serial=serial,
            item=DummyModel(
                product_item=DummyModel(
                    name=item_name,
                    product=DummyModel(
                        seat_stock_type=DummyModel(
                            quantity_only=True
                        )
                    )
                )
            )
        )

    @staticmethod
    def _create_token_with_seat(token_id, item_name, seat_name):
        return DummyModel(
            id=token_id,
            seat=DummyModel(name=seat_name),
            item=DummyModel(
                product_item=DummyModel(
                    name=item_name,
                    product=DummyModel(
                        seat_stock_type=DummyModel(
                            quantity_only=False
                        )
                    )
                )
            )
        )

    @mock.patch('altair.app.ticketing.payments.plugins.skidata_qr.SkidataBarcode.update_token')
    @mock.patch('altair.app.ticketing.payments.plugins.skidata_qr.get_db_session')
    @mock.patch('altair.app.ticketing.payments.plugins.skidata_qr.OrderedProductItemToken.find_all_by_order_no')
    def test_update_to_modify_with_quantity_only(self, find_all_by_order_no, get_db_session, update_token):
        """ 正常系テスト 数受けの予約更新　予約商品増減なし """
        test_existing_barcode_list = [
            DummyModel(id=1, ordered_product_item_token=self._create_token_with_quantity_only(1, u'テスト商品', 0)),
            DummyModel(id=1, ordered_product_item_token=self._create_token_with_quantity_only(2, u'テスト商品', 1)),
        ]
        find_all_by_order_no.return_value = [
            self._create_token_with_quantity_only(10, u'テスト商品', 0),
            self._create_token_with_quantity_only(11, u'テスト商品', 1)
        ]
        get_db_session.return_value = None

        self.__call_test_target(u'TEST000001', test_existing_barcode_list)
        self.assertTrue(update_token.called)

    @mock.patch('altair.app.ticketing.payments.plugins.skidata_qr.SkidataBarcode.update_token')
    @mock.patch('altair.app.ticketing.payments.plugins.skidata_qr.SkidataBarcode.insert_new_barcode')
    @mock.patch('altair.app.ticketing.payments.plugins.skidata_qr.get_db_session')
    @mock.patch('altair.app.ticketing.payments.plugins.skidata_qr.OrderedProductItemToken.find_all_by_order_no')
    def test_update_to_add_with_quantity_only(self, find_all_by_order_no, get_db_session, insert_new_barcode,
                                              update_token):
        """ 正常系テスト 数受けの予約更新　予約商品を増やす """
        test_existing_barcode_list = [
            DummyModel(id=1, ordered_product_item_token=self._create_token_with_quantity_only(1, u'テスト商品', 0)),
        ]
        find_all_by_order_no.return_value = [
            self._create_token_with_quantity_only(10, u'テスト商品', 0),
            self._create_token_with_quantity_only(11, u'テスト商品', 1)
        ]
        get_db_session.return_value = None

        self.__call_test_target(u'TEST000001', test_existing_barcode_list)
        self.assertTrue(insert_new_barcode.called)
        self.assertTrue(update_token.called)

    @mock.patch('altair.app.ticketing.payments.plugins.skidata_qr.SkidataBarcode.update_token')
    @mock.patch('altair.app.ticketing.payments.plugins.skidata_qr.SkidataBarcode.cancel')
    @mock.patch('altair.app.ticketing.payments.plugins.skidata_qr.get_db_session')
    @mock.patch('altair.app.ticketing.payments.plugins.skidata_qr.OrderedProductItemToken.find_all_by_order_no')
    def test_refresh_to_cancel_with_quantity_only(self, find_all_by_order_no, get_db_session, cancel, update_token):
        """ 正常系テスト 数受けの予約更新　予約商品を減らす """
        test_existing_barcode_list = [
            DummyModel(id=1, ordered_product_item_token=self._create_token_with_quantity_only(1, u'テスト商品', 0)),
            DummyModel(id=1, ordered_product_item_token=self._create_token_with_quantity_only(2, u'テスト商品', 1)),
        ]
        find_all_by_order_no.return_value = [
            self._create_token_with_quantity_only(10, u'テスト商品', 0)
        ]
        get_db_session.return_value = None

        self.__call_test_target(u'TEST000001', test_existing_barcode_list)
        self.assertTrue(cancel.called)
        self.assertTrue(update_token.called)

    @mock.patch('altair.app.ticketing.payments.plugins.skidata_qr.SkidataBarcode.update_token')
    @mock.patch('altair.app.ticketing.payments.plugins.skidata_qr.get_db_session')
    @mock.patch('altair.app.ticketing.payments.plugins.skidata_qr.OrderedProductItemToken.find_all_by_order_no')
    def test_refresh_to_modify_with_seat(self, find_all_by_order_no, get_db_session, update_token):
        """ 正常系テスト 席ありの予約更新　予約商品増減なし """
        test_existing_barcode_list = [
            DummyModel(id=1, ordered_product_item_token=self._create_token_with_seat(1, u'テスト商品', u'22番席')),
            DummyModel(id=1, ordered_product_item_token=self._create_token_with_seat(2, u'テスト商品', u'23番席'))
        ]
        find_all_by_order_no.return_value = [
            self._create_token_with_seat(10, u'テスト商品', u'22番席'),
            self._create_token_with_seat(11, u'テスト商品', u'23番席')
        ]
        get_db_session.return_value = None

        self.__call_test_target(u'TEST000001', test_existing_barcode_list)
        self.assertTrue(update_token.called)

    @mock.patch('altair.app.ticketing.payments.plugins.skidata_qr.SkidataBarcode.update_token')
    @mock.patch('altair.app.ticketing.payments.plugins.skidata_qr.SkidataBarcode.insert_new_barcode')
    @mock.patch('altair.app.ticketing.payments.plugins.skidata_qr.get_db_session')
    @mock.patch('altair.app.ticketing.payments.plugins.skidata_qr.OrderedProductItemToken.find_all_by_order_no')
    def test_refresh_to_add_with_seat(self, find_all_by_order_no, get_db_session, insert_new_barcode, update_token):
        """ 正常系テスト 席ありの予約更新　予約商品を増やす """
        test_existing_barcode_list = [
            DummyModel(id=1, ordered_product_item_token=self._create_token_with_seat(1, u'テスト商品', u'22番席'))
        ]
        find_all_by_order_no.return_value = [
            self._create_token_with_seat(10, u'テスト商品', u'22番席'),
            self._create_token_with_seat(11, u'テスト商品', u'23番席')
        ]
        get_db_session.return_value = None

        self.__call_test_target(u'TEST000001', test_existing_barcode_list)
        self.assertTrue(insert_new_barcode.called)
        self.assertTrue(update_token.called)

    @mock.patch('altair.app.ticketing.payments.plugins.skidata_qr.SkidataBarcode.update_token')
    @mock.patch('altair.app.ticketing.payments.plugins.skidata_qr.SkidataBarcode.cancel')
    @mock.patch('altair.app.ticketing.payments.plugins.skidata_qr.get_db_session')
    @mock.patch('altair.app.ticketing.payments.plugins.skidata_qr.OrderedProductItemToken.find_all_by_order_no')
    def test_refresh_to_cancel_with_seat(self, find_all_by_order_no, get_db_session, cancel, update_token):
        """  refreshの正常系テスト 席ありの予約更新　予約商品を減らす """
        test_existing_barcode_list = [
            DummyModel(id=1, ordered_product_item_token=self._create_token_with_seat(1, u'テスト商品', u'22番席')),
            DummyModel(id=1, ordered_product_item_token=self._create_token_with_seat(2, u'テスト商品', u'23番席')),
        ]
        find_all_by_order_no.return_value = [
            self._create_token_with_seat(10, u'テスト商品', u'22番席')
        ]
        get_db_session.return_value = None

        self.__call_test_target(u'TEST000001', test_existing_barcode_list)
        self.assertTrue(cancel.called)
        self.assertTrue(update_token.called)
