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

    def test_refresh(self):
        pass

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
