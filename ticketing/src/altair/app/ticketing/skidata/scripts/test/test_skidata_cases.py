#! /usr/bin/env python
# encoding:utf-8
import mock
from altair.app.ticketing.skidata.scripts.test.base_skidata_order_test import BaseSkidataOrderTest
from altair.app.ticketing.skidata.scripts import send_white_list_data_to_skidata as target_batch
from altair.app.ticketing.skidata.models import SkidataBarcode

RESOURCE_PATH = 'test_helper/resources'
BATCH_INI = '/altair.ticketing.batch.ini'


@mock.patch.object(target_batch, 'transaction')
@mock.patch.object(target_batch, 'bootstrap')
@mock.patch.object(target_batch, '_prepare_barcode_data')
@mock.patch.object(target_batch, '_send_qr_objs_to_hsh')
@mock.patch.object(target_batch, 'get_global_db_session')
@mock.patch.object(target_batch, 'DBSession')
@mock.patch.object(target_batch, 'sqlahelper')
class SkidataOrderTest(BaseSkidataOrderTest):
    def setUp(self):
        super(SkidataOrderTest, self).setUp()
        self.except_keys = ('hide_voucher', 'fee_type')
        self.importer_tables_with_file(RESOURCE_PATH+'/common_sbdata_property.csv')

    @classmethod
    def _send_to_batch(cls, params):
        target_batch.send_white_list_data_to_skidata(params)

    def _assert_equal(self, except_count):
        barcode_objs = self.session.query(SkidataBarcode).filter(SkidataBarcode.sent_at.isnot(None)).all()
        self.assertEqual(len(barcode_objs), except_count)

    def test_case_01_1line(self, sqlahelper, db_session, get_global_db_session, send_qr_objs_to_hsh,
                           prepare_barcode_data, bootstrap, transaction):
        self.mock_objects(sqlahelper, db_session, get_global_db_session, send_qr_objs_to_hsh,
                          prepare_barcode_data, bootstrap, transaction)
        self.importer_tables_with_file(RESOURCE_PATH+'/test_data_01_1line.csv', self.except_keys)

        self._send_to_batch(['', '-C', BATCH_INI, '--offset', '0', '--days', '1001'])
        self._assert_equal(1)

    def test_case_02_3line(self, sqlahelper, db_session, get_global_db_session, send_qr_objs_to_hsh,
                           prepare_barcode_data, bootstrap, transaction):
        self.mock_objects(sqlahelper, db_session, get_global_db_session, send_qr_objs_to_hsh,
                          prepare_barcode_data, bootstrap, transaction)
        self.importer_tables_with_file(RESOURCE_PATH+'/test_data_02_3line.csv', self.except_keys)

        self._send_to_batch(['', '-C', BATCH_INI, '--offset', '0', '--days', '1001'])
        self._assert_equal(3)

    def test_case_03_5line(self, sqlahelper, db_session, get_global_db_session, send_qr_objs_to_hsh,
                           prepare_barcode_data, bootstrap, transaction):
        self.mock_objects(sqlahelper, db_session, get_global_db_session, send_qr_objs_to_hsh,
                          prepare_barcode_data, bootstrap, transaction)
        self.importer_tables_with_file(RESOURCE_PATH+'/test_data_03_5line.csv', self.except_keys)

        self._send_to_batch(['', '-C', BATCH_INI, '--offset', '0', '--days', '1001'])
        self._assert_equal(5)

    def test_case_04_0line(self, sqlahelper, db_session, get_global_db_session, send_qr_objs_to_hsh,
                           prepare_barcode_data, bootstrap, transaction):
        self.mock_objects(sqlahelper, db_session, get_global_db_session, send_qr_objs_to_hsh,
                          prepare_barcode_data, bootstrap, transaction)
        self.importer_tables_with_file(RESOURCE_PATH+'/test_data_04_0line.csv', self.except_keys)

        self._send_to_batch(['', '-C', BATCH_INI, '--offset', '0', '--days', '1001'])
        self._assert_equal(0)

    def test_case_not_send_by_time(self, sqlahelper, db_session, get_global_db_session, send_qr_objs_to_hsh,
                                   prepare_barcode_data, bootstrap, transaction):
        self.mock_objects(sqlahelper, db_session, get_global_db_session, send_qr_objs_to_hsh,
                          prepare_barcode_data, bootstrap, transaction)
        self.importer_tables_with_file(RESOURCE_PATH+'/test_data_not_send_by_time.csv', self.except_keys)

        self._send_to_batch(['', '-C', BATCH_INI, '--offset', '0', '--days', '0'])
        self._assert_equal(0)
