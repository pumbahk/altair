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

        def mock_exist_operator_event():
            return True

        test_context = DummyResource(lot=test_lot, exist_operator_event=mock_exist_operator_event)
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

    def test_show_lot_invalid_event_of_lot(self):
        """
        show_lot_report 異常系のテスト 許可されていないイベントの抽選
        """
        from pyramid.httpexceptions import HTTPNotFound
        test_lot = DummyModel()

        def mock_exist_operator_event():
            return False

        test_context = DummyResource(lot=test_lot, exist_operator_event=mock_exist_operator_event)
        test_request = DummyRequest()

        with self.assertRaises(HTTPNotFound):
            self.__make_test_target(test_context, test_request).show_lot_report()

    @mock.patch('altair.app.ticketing.mini_admin.views.CSVExporter')
    @mock.patch('altair.app.ticketing.mini_admin.views.get_db_session')
    def test_export_entries(self, get_db_session, csv_exporter):
        """
        export_entriesの正常系のテスト
        """
        test_lot = DummyModel(id=123)

        def mock_exist_operator_event():
            return True

        def mock_all():
            return 1, 2, 3

        def mock_iter():
            return MockIterator()

        class MockIterator:
            def __init__(self):
                self.count = 0

            def __iter__(self):
                return self

            def next(self):
                if self.count == 6:
                    raise StopIteration()

                self.count += 1
                return self.count

        test_context = DummyResource(lot=test_lot, exist_operator_event=mock_exist_operator_event)
        test_request = DummyRequest()
        get_db_session.return_value = DummyModel()
        csv_exporter.return_value = DummyModel(all=mock_all, __iter__=mock_iter)

        view_data = self.__make_test_target(test_context, test_request).export_entries()
        self.assertIsNotNone(view_data)
        self.assertEqual(view_data.get('filename'), 'lot-{0.id}.csv'.format(test_lot))

    def test_export_entries_not_found(self):
        """
        export_entriesの異常系のテスト 存在しない抽選
        """
        from pyramid.httpexceptions import HTTPNotFound
        test_context = DummyResource(lot=None)
        test_request = DummyRequest()

        with self.assertRaises(HTTPNotFound):
            self.__make_test_target(test_context, test_request).export_entries()

    def test_export_entries_invalid_event_of_lot(self):
        """
        export_entriesの異常系のテスト 許可されていないイベントの抽選
        """
        from pyramid.httpexceptions import HTTPNotFound
        test_lot = DummyModel()

        def mock_exist_operator_event():
            return False

        test_context = DummyResource(lot=test_lot, exist_operator_event=mock_exist_operator_event)
        test_request = DummyRequest()

        with self.assertRaises(HTTPNotFound):
            self.__make_test_target(test_context, test_request).export_entries()

    @mock.patch('altair.app.ticketing.mini_admin.views.CSVExporter')
    @mock.patch('altair.app.ticketing.mini_admin.views.get_db_session')
    def test_no_export_entries(self, get_db_session, csv_exporter):
        """
        export_entriesの正常系のテスト エクスポートするLotEntryが0件
        """
        from pyramid.httpexceptions import HTTPFound
        test_lot = DummyModel(id=123)

        def mock_exist_operator_event():
            return True

        def mock_all():
            return [None]

        def mock_route_url(route_name, lot_id=None):
            return 'http://example.com'

        test_context = DummyResource(lot=test_lot, exist_operator_event=mock_exist_operator_event)
        test_request = DummyRequest(route_url=mock_route_url)
        get_db_session.return_value = DummyModel()
        csv_exporter.return_value = DummyModel(all=mock_all)

        view_data = self.__make_test_target(test_context, test_request).export_entries()
        self.assertIsInstance(view_data, HTTPFound)
