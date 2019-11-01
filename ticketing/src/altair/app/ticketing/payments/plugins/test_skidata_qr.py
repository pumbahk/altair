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

    @mock.patch('altair.app.ticketing.payments.plugins.skidata_qr.SkidataBarcode.insert_new_barcode')
    @mock.patch('altair.app.ticketing.payments.plugins.skidata_qr.OrderedProductItemToken.find_all_by_order_no')
    def test_finish_success(self, find_all_by_order_no, insert_new_barcode):
        """ finishの正常系テスト """
        find_all_by_order_no.return_value = [DummyModel(id=1), DummyModel(id=2)]
        test_plugin = self.__make_test_target()
        test_plugin.finish(DummyRequest(), DummyModel(order_no='TEST0000001'))
        self.assertTrue(insert_new_barcode.called)

    @mock.patch('altair.app.ticketing.payments.plugins.skidata_qr.SkidataBarcode.insert_new_barcode')
    @mock.patch('altair.app.ticketing.payments.plugins.skidata_qr.SkidataBarcode.find_by_token_id')
    @mock.patch('altair.app.ticketing.payments.plugins.skidata_qr.OrderedProductItemToken.find_all_by_order_no')
    def test_finish2_with_new_barcode(self, find_all_by_order_no, find_by_token_id, insert_new_barcode):
        """ finish2の正常系テスト QR新規作成 """
        from sqlalchemy.orm.exc import NoResultFound
        find_all_by_order_no.return_value = [DummyModel(id=1), DummyModel(id=2)]
        find_by_token_id.side_effect = NoResultFound
        test_plugin = self.__make_test_target()
        test_plugin.finish2(DummyRequest(), DummyModel(order_no='TEST0000001'))
        self.assertTrue(insert_new_barcode.called)

    @mock.patch('altair.app.ticketing.payments.plugins.skidata_qr.SkidataBarcode.insert_new_barcode')
    @mock.patch('altair.app.ticketing.payments.plugins.skidata_qr.SkidataBarcode.find_by_token_id')
    @mock.patch('altair.app.ticketing.payments.plugins.skidata_qr.OrderedProductItemToken.find_all_by_order_no')
    def test_finish2_with_existing_barcode(self, find_all_by_order_no, find_by_token_id, insert_new_barcode):
        """ finish2の正常系テスト QR作成済 """
        find_all_by_order_no.return_value = [DummyModel(id=1), DummyModel(id=2)]
        find_by_token_id.return_value = DummyModel()
        test_plugin = self.__make_test_target()
        test_plugin.finish2(DummyRequest(), DummyModel(order_no='TEST0000001'))
        self.assertFalse(insert_new_barcode.called)

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
    @mock.patch('altair.app.ticketing.payments.plugins.skidata_qr.SkidataBarcode.insert_new_barcode')
    @mock.patch('altair.app.ticketing.payments.plugins.skidata_qr.get_db_session')
    @mock.patch('altair.app.ticketing.payments.plugins.skidata_qr.OrderedProductItemToken.find_all_by_order_no')
    @mock.patch('altair.app.ticketing.payments.plugins.skidata_qr.SkidataBarcode.find_all_by_order_no')
    def test_refresh_to_add_with_quantity_only(self, find_all_skidata, find_all_token, get_db_session,
                                               insert_new_barcode, update_token):
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

        self.assertTrue(insert_new_barcode.called)
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
    @mock.patch('altair.app.ticketing.payments.plugins.skidata_qr.SkidataBarcode.insert_new_barcode')
    @mock.patch('altair.app.ticketing.payments.plugins.skidata_qr.get_db_session')
    @mock.patch('altair.app.ticketing.payments.plugins.skidata_qr.OrderedProductItemToken.find_all_by_order_no')
    @mock.patch('altair.app.ticketing.payments.plugins.skidata_qr.SkidataBarcode.find_all_by_order_no')
    def test_refresh_to_add_with_seat(self, find_all_skidata, find_all_token, get_db_session,
                                               insert_new_barcode, update_token):
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

        self.assertTrue(insert_new_barcode.called)
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

    @mock.patch('altair.app.ticketing.payments.plugins.skidata_qr.SkidataBarcode.update_token')
    @mock.patch('altair.app.ticketing.payments.plugins.skidata_qr.ProtoOPIToken_SkidataBarcode.find_by_token_id')
    def test_link_existing_barcode_to_new_order_with_existing_barcode(self, find_by_token_id, update_token):
        """ link_existing_barcode_to_new_orderの正常系テスト 既存のQRを紐付ける """
        test_new_order = DummyModel(
            items=[
                DummyModel(
                    elements=[
                        DummyModel(
                            tokens=[
                                self._create_token_with_quantity_only(1, u'テスト1', 0),
                                self._create_token_with_quantity_only(2, u'テスト2', 1)
                            ]
                        )
                    ]
                )
            ]
        )
        test_proto_order = DummyModel(
            items=[
                DummyModel(
                    elements=[
                        DummyModel(
                            tokens=[
                                self._create_token_with_quantity_only(5, u'テスト1', 0),
                                self._create_token_with_quantity_only(6, u'テスト2', 1)
                            ]
                        )
                    ]
                )
            ]
        )
        find_by_token_id.return_value = DummyModel(skidata_barcode_id=1)

        test_plugin = self.__make_test_target()
        test_plugin.link_existing_barcode_to_new_order(test_new_order, test_proto_order)
        self.assertTrue(update_token.called)

    @mock.patch('altair.app.ticketing.payments.plugins.skidata_qr.SkidataBarcode.update_token')
    @mock.patch('altair.app.ticketing.payments.plugins.skidata_qr.ProtoOPIToken_SkidataBarcode.find_by_token_id')
    def test_link_existing_barcode_to_new_order_without_existing_barcode(self, find_by_token_id, update_token):
        """ link_existing_barcode_to_new_orderの正常系テスト 既存のQRなし """
        from sqlalchemy.orm.exc import NoResultFound
        test_new_order = DummyModel(
            items=[
                DummyModel(
                    elements=[
                        DummyModel(
                            tokens=[
                                self._create_token_with_quantity_only(1, u'テスト1', 0),
                                self._create_token_with_quantity_only(2, u'テスト2', 1)
                            ]
                        )
                    ]
                )
            ]
        )
        test_proto_order = DummyModel(
            items=[
                DummyModel(
                    elements=[
                        DummyModel(
                            tokens=[
                                self._create_token_with_quantity_only(5, u'テスト1', 0),
                                self._create_token_with_quantity_only(6, u'テスト2', 1)
                            ]
                        )
                    ]
                )
            ]
        )
        find_by_token_id.side_effect = NoResultFound

        test_plugin = self.__make_test_target()
        test_plugin.link_existing_barcode_to_new_order(test_new_order, test_proto_order)
        self.assertFalse(update_token.called)

    def test_link_existing_barcode_to_new_order_with_invalid_consistency(self):
        """ link_existing_barcode_to_new_orderの異常系テスト Tokenの整合性不一致 """
        from altair.app.ticketing.payments.plugins.skidata_qr import InvalidSkidataConsistency
        test_new_order = DummyModel(
            items=[
                DummyModel(
                    elements=[
                        DummyModel(
                            tokens=[
                                self._create_token_with_quantity_only(1, u'テスト1', 0),
                                self._create_token_with_quantity_only(2, u'テスト2', 1)
                            ]
                        )
                    ]
                )
            ]
        )
        test_proto_order = DummyModel(
            id=1,
            items=[
                DummyModel(
                    elements=[
                        DummyModel(
                            tokens=[
                                self._create_token_with_quantity_only(5, u'テスト5', 2),
                                self._create_token_with_quantity_only(6, u'テスト6', 3)
                            ]
                        )
                    ]
                )
            ]
        )
        test_plugin = self.__make_test_target()
        with self.assertRaises(InvalidSkidataConsistency):
            test_plugin.link_existing_barcode_to_new_order(test_new_order, test_proto_order)


class DeliverConfirmViewletTest(unittest.TestCase):
    @staticmethod
    def __call_test_target(*args, **kwargs):
        from altair.app.ticketing.payments.plugins.skidata_qr import deliver_confirm_viewlet
        return deliver_confirm_viewlet(*args, **kwargs)

    @mock.patch('altair.app.ticketing.payments.plugins.skidata_qr.get_delivery_method_info')
    def test_success(self, get_delivery_method_info):
        from markupsafe import Markup

        def mock_info(request, delivery_method, key_name):
            if key_name is 'name':
                return delivery_method.name
            if key_name is 'description':
                return delivery_method.description

        get_delivery_method_info.side_effect = mock_info
        test_delivery_method = DummyModel(
            name=u'テスト',
            description=u'これはテストです'
        )
        test_context = DummyResource(
            cart=DummyModel(
                payment_delivery_pair=DummyModel(
                    delivery_method=test_delivery_method
                )
            )
        )

        return_dict = self.__call_test_target(test_context, DummyRequest())
        self.assertEqual(return_dict.get('delivery_name'), test_delivery_method.name)
        self.assertIsInstance(return_dict.get('description'), Markup)


class DeliverCompletionViewletTest(unittest.TestCase):
    @staticmethod
    def __call_test_target(*args, **kwargs):
        from altair.app.ticketing.payments.plugins.skidata_qr import deliver_completion_viewlet
        return deliver_completion_viewlet(*args, **kwargs)

    @mock.patch('altair.app.ticketing.payments.plugins.skidata_qr.SkidataBarcode.find_all_by_order_no')
    @mock.patch('altair.app.ticketing.payments.plugins.skidata_qr.get_db_session')
    @mock.patch('altair.app.ticketing.payments.plugins.skidata_qr.get_delivery_method_info')
    def test_success(self, get_delivery_method_info, get_db_session, find_all_by_order_no):
        """ 正常系テスト """
        from markupsafe import Markup

        def mock_info(request, delivery_method, key_name):
            if key_name is 'name':
                return delivery_method.name
            if key_name is 'description':
                return delivery_method.description

        get_delivery_method_info.side_effect = mock_info
        test_delivery_method = DummyModel(
            name=u'テスト',
            description=u'これはテストです'
        )
        test_context = DummyResource(
            order=DummyModel(
                order_no = 'TEST0000001',
                payment_delivery_pair=DummyModel(
                    delivery_method=test_delivery_method
                )
            )
        )
        get_db_session.return_value = DummyModel()
        test_barcode_list = [DummyModel(), DummyModel()]
        find_all_by_order_no.return_value = test_barcode_list

        return_dict = self.__call_test_target(test_context, DummyRequest())
        self.assertIsNotNone(return_dict.get('barcode_list'))
        self.assertEqual(return_dict.get('barcode_list'), test_barcode_list)
        self.assertIsInstance(return_dict.get('description'), Markup)


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
