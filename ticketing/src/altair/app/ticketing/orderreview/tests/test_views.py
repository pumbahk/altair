# -*- coding:utf-8 -*-

import unittest
from pyramid.testing import DummyResource, DummyModel
from altair.app.ticketing.testing import DummyRequest
import mock


class QRGateViewTest(unittest.TestCase):
    @staticmethod
    def __make_test_target(*args, **kwargs):
        from altair.app.ticketing.orderreview.views import QRGateView
        return QRGateView(*args, **kwargs)

    @mock.patch('altair.app.ticketing.orderreview.views.SkidataBarcode.find_by_id')
    @mock.patch('altair.app.ticketing.orderreview.views.get_db_session')
    def test_qr_draw_success(self, get_db_session, find_by_id):
        import hashlib
        test_barcode_id = '1'
        test_barcode_data = 'test'
        test_hash = hashlib.sha256(test_barcode_data).hexdigest()
        test_request = DummyRequest(matchdict=dict(barcode_id=test_barcode_id, hash=test_hash))
        test_skidata_barcode = DummyModel(data=test_barcode_data)
        get_db_session.return_value = DummyModel()
        find_by_id.return_value = test_skidata_barcode

        test_view = self.__make_test_target(DummyResource(), test_request)
        response = test_view.qr_draw()
        self.assertIsNotNone(response)

    @mock.patch('altair.app.ticketing.orderreview.views.SkidataBarcode.find_by_id')
    @mock.patch('altair.app.ticketing.orderreview.views.get_db_session')
    def test_qr_draw_no_barcode(self, get_db_session, find_by_id):
        import hashlib
        from pyramid.httpexceptions import HTTPNotFound
        test_barcode_id = '1'
        test_barcode_data = 'test'
        test_hash = hashlib.sha256(test_barcode_data).hexdigest()
        test_request = DummyRequest(matchdict=dict(barcode_id=test_barcode_id, hash=test_hash))
        get_db_session.return_value = DummyModel()
        find_by_id.return_value = None

        test_view = self.__make_test_target(DummyResource(), test_request)
        with self.assertRaises(HTTPNotFound):
            test_view.qr_draw()

    @mock.patch('altair.app.ticketing.orderreview.views.SkidataBarcode.find_by_id')
    @mock.patch('altair.app.ticketing.orderreview.views.get_db_session')
    def test_qr_draw_mismatch_hash(self, get_db_session, find_by_id):
        import hashlib
        from pyramid.httpexceptions import HTTPNotFound
        test_barcode_id = '1'
        test_barcode_data = 'test'
        test_hash = hashlib.sha256('invalid_value').hexdigest()
        test_request = DummyRequest(matchdict=dict(barcode_id=test_barcode_id, hash=test_hash))
        test_skidata_barcode = DummyModel(data=test_barcode_data)
        get_db_session.return_value = DummyModel()
        find_by_id.return_value = test_skidata_barcode

        test_view = self.__make_test_target(DummyResource(), test_request)
        with self.assertRaises(HTTPNotFound):
            test_view.qr_draw()
