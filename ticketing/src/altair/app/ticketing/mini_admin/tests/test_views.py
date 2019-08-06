# -*- coding:utf-8 -*-
import mock
import unittest
from pyramid.testing import DummyResource, DummyModel
from altair.app.ticketing.testing import DummyRequest


class MiniAdminLotViewTest(unittest.TestCase):
    @staticmethod
    def __make_test_target(*args, **kwargs):
        from altair.app.ticketing.mini_admin.views import MiniAdminLotView
        return MiniAdminLotView(*args, **kwargs)

    @mock.patch('altair.app.ticketing.mini_admin.views.get_lot_entry_status')
    def test_show_lot_report(self, get_lot_entry_status):
        """
        show_lot_report 正常系のテスト
        """
        test_lot = DummyModel()
        test_context = DummyResource(lot=test_lot)
        test_request = DummyRequest()
        test_lot_entry_status = DummyModel()
        get_lot_entry_status.return_value = test_lot_entry_status

        view_data = self.__make_test_target(test_context, test_request).show_lot_report()
        self.assertEqual(view_data.get('lot'), test_lot)
        self.assertEqual(view_data.get('lot_status'), test_lot_entry_status)
        self.assertTrue(get_lot_entry_status.called)

    def test_show_lot_report_not_found(self):
        """
        show_lot_report 異常系のテスト 存在しない抽選
        """
        from pyramid.httpexceptions import HTTPNotFound
        test_context = DummyResource(lot=None)
        test_request = DummyRequest()

        with self.assertRaises(HTTPNotFound):
            self.__make_test_target(test_context, test_request).show_lot_report()
