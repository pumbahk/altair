# -*- coding:utf-8 -*-

import unittest
import mock
from pyramid.testing import DummyResource, DummyModel
from altair.app.ticketing.testing import DummyRequest


class SkidataQRDeliveryPluginTest(unittest.TestCase):
    @staticmethod
    def __make_test_target(*args, **kwargs):
        from altair.app.ticketing.payments.plugins.skidata_qr import SkidataQRDeliveryPlugin
        return SkidataQRDeliveryPlugin(*args, **kwargs)

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

    def test_validate_order(self):
        pass

    def test_validate_order_cancellation(self):
        pass

    def test_prepare(self):
        pass

    @mock.patch('altair.app.ticketing.payments.plugins.skidata_qr.SkidataBarcode.insert_new_barcode_by_token')
    @mock.patch('altair.app.ticketing.payments.plugins.skidata_qr.OrderedProductItemToken.find_all_by_order_no')
    def test_finish_success(self, find_all_by_order_no, insert_new_barcode_by_token):
        """ finishの正常系テスト """
        find_all_by_order_no.return_value = [DummyModel(), DummyModel()]
        test_plugin = self.__make_test_target()
        test_plugin.finish(DummyRequest(), DummyModel(order_no='TEST0000001'))
        self.assertTrue(insert_new_barcode_by_token.called)

    def test_finish2(self):
        pass

    def test_finished(self):
        pass

    @mock.patch('altair.app.ticketing.payments.plugins.skidata_qr.SkidataBarcode.update_token')
    @mock.patch('altair.app.ticketing.payments.plugins.skidata_qr.get_db_session')
    @mock.patch('altair.app.ticketing.payments.plugins.skidata_qr.OrderedProductItemToken.find_all_by_order_no')
    @mock.patch('altair.app.ticketing.payments.plugins.skidata_qr.SkidataBarcode.find_all_by_order_no')
    def test_refresh_to_modify_with_quantity_only(self, find_all_skidata, find_all_token, get_db_session, update_token):
        """  refreshの正常系テスト 数受けの予約更新　予約商品増減なし """
        test_order = DummyModel(order_no=u'TEST000001')
        find_all_skidata.return_value = [
            DummyModel(id=1, ordered_product_item_token=self._create_token_with_quantity_only(1, u'テスト商品', 0)),
            DummyModel(id=1, ordered_product_item_token=self._create_token_with_quantity_only(2, u'テスト商品', 1)),
        ]
        find_all_token.return_value = [
            self._create_token_with_quantity_only(10, u'テスト商品', 0),
            self._create_token_with_quantity_only(11, u'テスト商品', 1)
        ]
        get_db_session.return_value = None

        test_plugin = self.__make_test_target()
        test_plugin.refresh(DummyRequest(), test_order)

        self.assertTrue(update_token.called)

    @mock.patch('altair.app.ticketing.payments.plugins.skidata_qr.SkidataBarcode.update_token')
    @mock.patch('altair.app.ticketing.payments.plugins.skidata_qr.SkidataBarcode.insert_new_barcode_by_token')
    @mock.patch('altair.app.ticketing.payments.plugins.skidata_qr.get_db_session')
    @mock.patch('altair.app.ticketing.payments.plugins.skidata_qr.OrderedProductItemToken.find_all_by_order_no')
    @mock.patch('altair.app.ticketing.payments.plugins.skidata_qr.SkidataBarcode.find_all_by_order_no')
    def test_refresh_to_add_with_quantity_only(self, find_all_skidata, find_all_token, get_db_session,
                                               insert_new_barcode_by_token, update_token):
        """  refreshの正常系テスト 数受けの予約更新　予約商品を増やす """
        test_order = DummyModel(order_no=u'TEST000001')
        find_all_skidata.return_value = [
            DummyModel(id=1, ordered_product_item_token=self._create_token_with_quantity_only(1, u'テスト商品', 0)),
        ]
        find_all_token.return_value = [
            self._create_token_with_quantity_only(10, u'テスト商品', 0),
            self._create_token_with_quantity_only(11, u'テスト商品', 1)
        ]
        get_db_session.return_value = None

        test_plugin = self.__make_test_target()
        test_plugin.refresh(DummyRequest(), test_order)

        self.assertTrue(insert_new_barcode_by_token.called)
        self.assertTrue(update_token.called)

    @mock.patch('altair.app.ticketing.payments.plugins.skidata_qr.SkidataBarcode.update_token')
    @mock.patch('altair.app.ticketing.payments.plugins.skidata_qr.SkidataBarcode.cancel')
    @mock.patch('altair.app.ticketing.payments.plugins.skidata_qr.get_db_session')
    @mock.patch('altair.app.ticketing.payments.plugins.skidata_qr.OrderedProductItemToken.find_all_by_order_no')
    @mock.patch('altair.app.ticketing.payments.plugins.skidata_qr.SkidataBarcode.find_all_by_order_no')
    def test_refresh_to_cancel_with_quantity_only(self, find_all_skidata, find_all_token,
                                                  get_db_session, cancel, update_token):
        """  refreshの正常系テスト 数受けの予約更新　予約商品を減らす """
        test_order = DummyModel(order_no=u'TEST000001')
        find_all_skidata.return_value = [
            DummyModel(id=1, ordered_product_item_token=self._create_token_with_quantity_only(1, u'テスト商品', 0)),
            DummyModel(id=1, ordered_product_item_token=self._create_token_with_quantity_only(2, u'テスト商品', 1)),
        ]
        find_all_token.return_value = [
            self._create_token_with_quantity_only(10, u'テスト商品', 0)
        ]
        get_db_session.return_value = None

        test_plugin = self.__make_test_target()
        test_plugin.refresh(DummyRequest(), test_order)

        self.assertTrue(cancel.called)
        self.assertTrue(update_token.called)

    @mock.patch('altair.app.ticketing.payments.plugins.skidata_qr.SkidataBarcode.update_token')
    @mock.patch('altair.app.ticketing.payments.plugins.skidata_qr.get_db_session')
    @mock.patch('altair.app.ticketing.payments.plugins.skidata_qr.OrderedProductItemToken.find_all_by_order_no')
    @mock.patch('altair.app.ticketing.payments.plugins.skidata_qr.SkidataBarcode.find_all_by_order_no')
    def test_refresh_to_modify_with_seat(self, find_all_skidata, find_all_token, get_db_session, update_token):
        """  refreshの正常系テスト 席ありの予約更新　予約商品増減なし """
        test_order = DummyModel(order_no=u'TEST000001')
        find_all_skidata.return_value = [
            DummyModel(id=1, ordered_product_item_token=self._create_token_with_seat(1, u'テスト商品', u'22番席')),
            DummyModel(id=1, ordered_product_item_token=self._create_token_with_seat(2, u'テスト商品', u'23番席'))
        ]
        find_all_token.return_value = [
            self._create_token_with_seat(10, u'テスト商品', u'22番席'),
            self._create_token_with_seat(11, u'テスト商品', u'23番席')
        ]
        get_db_session.return_value = None

        test_plugin = self.__make_test_target()
        test_plugin.refresh(DummyRequest(), test_order)

        self.assertTrue(update_token.called)

    @mock.patch('altair.app.ticketing.payments.plugins.skidata_qr.SkidataBarcode.update_token')
    @mock.patch('altair.app.ticketing.payments.plugins.skidata_qr.SkidataBarcode.insert_new_barcode_by_token')
    @mock.patch('altair.app.ticketing.payments.plugins.skidata_qr.get_db_session')
    @mock.patch('altair.app.ticketing.payments.plugins.skidata_qr.OrderedProductItemToken.find_all_by_order_no')
    @mock.patch('altair.app.ticketing.payments.plugins.skidata_qr.SkidataBarcode.find_all_by_order_no')
    def test_refresh_to_add_with_seat(self, find_all_skidata, find_all_token, get_db_session,
                                               insert_new_barcode_by_token, update_token):
        """  refreshの正常系テスト 席ありの予約更新　予約商品を増やす """
        test_order = DummyModel(order_no=u'TEST000001')
        find_all_skidata.return_value = [
            DummyModel(id=1, ordered_product_item_token=self._create_token_with_seat(1, u'テスト商品', u'22番席'))
        ]
        find_all_token.return_value = [
            self._create_token_with_seat(10, u'テスト商品', u'22番席'),
            self._create_token_with_seat(11, u'テスト商品', u'23番席')
        ]
        get_db_session.return_value = None

        test_plugin = self.__make_test_target()
        test_plugin.refresh(DummyRequest(), test_order)

        self.assertTrue(insert_new_barcode_by_token.called)
        self.assertTrue(update_token.called)

    @mock.patch('altair.app.ticketing.payments.plugins.skidata_qr.SkidataBarcode.update_token')
    @mock.patch('altair.app.ticketing.payments.plugins.skidata_qr.SkidataBarcode.cancel')
    @mock.patch('altair.app.ticketing.payments.plugins.skidata_qr.get_db_session')
    @mock.patch('altair.app.ticketing.payments.plugins.skidata_qr.OrderedProductItemToken.find_all_by_order_no')
    @mock.patch('altair.app.ticketing.payments.plugins.skidata_qr.SkidataBarcode.find_all_by_order_no')
    def test_refresh_to_cancel_with_seat(self, find_all_skidata, find_all_token,
                                                  get_db_session, cancel, update_token):
        """  refreshの正常系テスト 席ありの予約更新　予約商品を減らす """
        test_order = DummyModel(order_no=u'TEST000001')
        find_all_skidata.return_value = [
            DummyModel(id=1, ordered_product_item_token=self._create_token_with_seat(1, u'テスト商品', u'22番席')),
            DummyModel(id=1, ordered_product_item_token=self._create_token_with_seat(2, u'テスト商品', u'23番席')),
        ]
        find_all_token.return_value = [
            self._create_token_with_seat(10, u'テスト商品', u'22番席')
        ]
        get_db_session.return_value = None

        test_plugin = self.__make_test_target()
        test_plugin.refresh(DummyRequest(), test_order)

        self.assertTrue(cancel.called)
        self.assertTrue(update_token.called)

    def test_cancel(self):
        pass

    def test_refund(self):
        pass

    def test_get_order_info(self):
        pass


class DeliverConfirmViewletTest(unittest.TestCase):
    @staticmethod
    def __call_test_target(*args, **kwargs):
        from altair.app.ticketing.payments.plugins.skidata_qr import deliver_confirm_viewlet
        return deliver_confirm_viewlet(*args, **kwargs)

    def test_success(self):
        pass


class DeliverCompletionViewletTest(unittest.TestCase):
    @staticmethod
    def __call_test_target(*args, **kwargs):
        from altair.app.ticketing.payments.plugins.skidata_qr import deliver_completion_viewlet
        return deliver_completion_viewlet(*args, **kwargs)

    @mock.patch('altair.app.ticketing.payments.plugins.skidata_qr.SkidataBarcode.find_all_by_order_no')
    @mock.patch('altair.app.ticketing.payments.plugins.skidata_qr.get_db_session')
    def test_success(self, get_db_session, find_all_by_order_no):
        """ 正常系テスト """
        test_context = DummyResource(order=DummyModel(order_no = 'TEST0000001'))
        get_db_session.return_value = DummyModel()
        test_barcode_list = [DummyModel(), DummyModel()]
        find_all_by_order_no.return_value = test_barcode_list

        return_dict = self.__call_test_target(test_context, DummyRequest())
        self.assertIsNotNone(return_dict.get('barcode_list'))
        self.assertEqual(return_dict.get('barcode_list'), test_barcode_list)


class DeliverCompletionMailViewlet(unittest.TestCase):
    @staticmethod
    def __call_test_target(*args, **kwargs):
        from altair.app.ticketing.payments.plugins.skidata_qr import deliver_completion_mail_viewlet
        return deliver_completion_mail_viewlet(*args, **kwargs)

    def test_success(self):
        pass


class DeliveryNoticeViewlet(unittest.TestCase):
    @staticmethod
    def __call_test_target(*args, **kwargs):
        from altair.app.ticketing.payments.plugins.skidata_qr import delivery_notice_viewlet
        return delivery_notice_viewlet(*args, **kwargs)

    def test_success(self):
        pass
