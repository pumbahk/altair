# -*- coding:utf-8 -*-

import unittest
from pyramid.testing import DummyResource, DummyModel
from altair.app.ticketing.testing import DummyRequest
import mock


class QRTicketViewTest(unittest.TestCase):
    @staticmethod
    def __make_test_target(*args, **kwargs):
        from altair.app.ticketing.orderreview.views import QRTicketView
        return QRTicketView(*args, **kwargs)

    @mock.patch('altair.app.ticketing.orderreview.resources.SkidataBarcode.find_by_id')
    @mock.patch('altair.app.ticketing.orderreview.resources.get_db_session')
    def test_show_qr_not_owner(self, get_db_session, find_by_id):
        import hashlib
        from altair.app.ticketing.orderreview.resources import QRTicketViewResource
        test_barcode_id = '1'
        test_barcode_data = 'test'
        test_hash = hashlib.sha256(test_barcode_data).hexdigest()

        def test_route_path(*args, **kwargs):
            return u'http://example.com'

        test_request = DummyRequest(
            matchdict=dict(barcode_id=test_barcode_id, hash=test_hash),
            route_path=test_route_path
        )
        test_opi_token = DummyModel(
            seat=DummyModel(),
            item=DummyModel(
                product_item=DummyModel(),
                ordered_product=DummyModel(
                    order=DummyModel(
                        performance=DummyModel()
                    ),
                    product=DummyModel(
                        seat_stock_type=DummyModel()
                    )
                )
            )
        )
        test_skidata_barcode = DummyModel(
            id=test_barcode_id,
            data=test_barcode_data,
            ordered_product_item_token=test_opi_token
        )
        get_db_session.return_value = DummyModel()
        find_by_id.return_value = test_skidata_barcode

        test_view = self.__make_test_target(QRTicketViewResource(test_request), test_request)
        return_dict = test_view.show_qr_ticket_not_owner()
        self.assertIsNotNone(return_dict)
        self.assertIsNotNone(return_dict.get(u'performance'))
        self.assertIsNotNone(return_dict.get(u'order'))
        self.assertIsNotNone(return_dict.get(u'product_item'))
        self.assertIsNotNone(return_dict.get(u'seat'))
        self.assertIsNotNone(return_dict.get(u'stock_type'))
        self.assertIsNotNone(return_dict.get(u'qr_url'))

    @mock.patch('altair.app.ticketing.orderreview.resources.SkidataBarcode.find_by_id')
    @mock.patch('altair.app.ticketing.orderreview.resources.get_db_session')
    def test_show_qr_not_owner_no_barcode(self, get_db_session, find_by_id):
        import hashlib
        from altair.app.ticketing.orderreview.resources import QRTicketViewResource
        from pyramid.httpexceptions import HTTPNotFound
        test_barcode_id = '1'
        test_barcode_data = 'test'
        test_hash = hashlib.sha256(test_barcode_data).hexdigest()

        test_request = DummyRequest(matchdict=dict(barcode_id=test_barcode_id, hash=test_hash))
        get_db_session.return_value = DummyModel()
        find_by_id.return_value = None

        test_view = self.__make_test_target(QRTicketViewResource(test_request), test_request)
        with self.assertRaises(HTTPNotFound):
            test_view.show_qr_ticket_not_owner()

    @mock.patch('altair.app.ticketing.orderreview.resources.SkidataBarcode.find_by_id')
    @mock.patch('altair.app.ticketing.orderreview.resources.get_db_session')
    def test_show_qr_not_owner_mismatch_hash(self, get_db_session, find_by_id):
        import hashlib
        from altair.app.ticketing.orderreview.resources import QRTicketViewResource
        from pyramid.httpexceptions import HTTPNotFound
        test_barcode_id = '1'
        test_barcode_data = 'test'
        test_hash = hashlib.sha256('invalid_value').hexdigest()

        test_request = DummyRequest(matchdict=dict(barcode_id=test_barcode_id, hash=test_hash))
        test_skidata_barcode = DummyModel(
            id=test_barcode_id,
            data=test_barcode_data
        )
        get_db_session.return_value = DummyModel()
        find_by_id.return_value = test_skidata_barcode

        test_view = self.__make_test_target(QRTicketViewResource(test_request), test_request)
        with self.assertRaises(HTTPNotFound):
            test_view.show_qr_ticket_not_owner()

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
