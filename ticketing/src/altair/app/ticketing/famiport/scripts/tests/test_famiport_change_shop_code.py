# -*- coding:utf-8 -*-
import os
import unittest
from datetime import datetime, date

import mock
from altair.app.ticketing.famiport.models import FamiPortReceipt
from altair.app.ticketing.famiport.scripts import famiport_change_shop_code as fcshc
from altair.app.ticketing.famiport.testing import _setup_db, _teardown_db
from altair.sqlahelper import get_global_db_session
from pyramid.testing import setUp, tearDown


dirname = os.path.dirname(__file__)
resource_path = os.path.join(dirname, 'resources')


class TestChangeShopCode(unittest.TestCase):
    def setUp(self):
        self.filename = 'ChangeStoreCodeList_TS.csv'
        self.config = setUp(
            settings={
                'altair.famiport.mdm.shop_code_change.pending_dir': resource_path,
                'altair.famiport.mdm.shop_code_change.imported_dir': resource_path,
                'altair.famiport.mdm.shop_code_change.filename': self.filename,
                'altair.famiport.mdm.shop_code_change.encoding': 'CP932'
            }
        )
        self.engine = _setup_db(self.config.registry, modules=["altair.app.ticketing.famiport.models"])
        self.session = self._get_session()

        self.famiport_order_identifier1 = u'001002287854'
        famiport_receipt1 = FamiPortReceipt(
            type=2,
            famiport_order_id=7329,
            famiport_order_identifier=self.famiport_order_identifier1,
            completed_at=datetime(2019, 2, 14, 15, 0, 0),
            rescued_at=datetime(2019, 2, 14, 15, 0, 0),
            created_at=datetime(2019, 2, 14, 12, 0, 0),
        )
        self.session.add(famiport_receipt1)
        self.session.flush()

    def _get_session(self):
        return get_global_db_session(self.config.registry, 'famiport')

    def tearDown(self):
        _teardown_db(self.config.registry)
        tearDown()

    @mock.patch('{}.date'.format(fcshc.__name__), date(2019, 2, 15))
    @mock.patch('os.rename')
    def test_success_case(self, mock_os_rename):
        famiport_order_identifier2 = u'003002287856'
        famiport_receipt2 = FamiPortReceipt(
            type=2,
            famiport_order_id=7525,
            famiport_order_identifier=famiport_order_identifier2,
            completed_at=datetime(2019, 2, 14, 9, 30, 0),
            rescued_at=datetime(2019, 2, 14, 9, 30, 0),
            created_at=datetime(2019, 2, 14, 5, 3, 0),
        )
        self.session.add(famiport_receipt2)
        self.session.flush()

        with mock.patch.object(fcshc.EnvSetup, '__call__', return_value={'registry': self.config.registry}):
            fcshc.main(['', '-C', '/famiport-batch.ini'])
            path = os.path.join(resource_path, self.filename)
            mock_os_rename.assert_called_with(path, path)

            session = self._get_session()
            exp_famiport_receipt1 = session.query(FamiPortReceipt)\
                .filter_by(famiport_order_identifier=self.famiport_order_identifier1).one()
            exp_famiport_receipt2 = session.query(FamiPortReceipt)\
                .filter_by(famiport_order_identifier=famiport_order_identifier2).one()

            self.assertEqual('70874', exp_famiport_receipt1.shop_code)
            self.assertIsNone(exp_famiport_receipt1.canceled_at)
            self.assertEqual('70876', exp_famiport_receipt2.shop_code)
            self.assertIsNotNone(exp_famiport_receipt2.canceled_at)

    @mock.patch('{}.date'.format(fcshc.__name__), date(2019, 2, 15))
    @mock.patch('os.rename')
    def test_partial_failure_case(self, mock_os_rename):
        famiport_order_identifier2 = u'003002287857'
        famiport_receipt2 = FamiPortReceipt(
            type=2,
            famiport_order_id=7525,
            famiport_order_identifier=famiport_order_identifier2,
            completed_at=datetime(2019, 2, 14, 9, 30, 0),
            rescued_at=datetime(2019, 2, 14, 9, 30, 0),
            created_at=datetime(2019, 2, 14, 5, 3, 0),
        )
        self.session.add(famiport_receipt2)
        self.session.flush()

        with mock.patch.object(fcshc.EnvSetup, '__call__', return_value={'registry': self.config.registry}):
            fcshc.main(['', '-C', '/famiport-batch.ini'])
            path = os.path.join(resource_path, self.filename)
            mock_os_rename.assert_called_with(path, path)

            session = self._get_session()
            exp_famiport_receipt1 = session.query(FamiPortReceipt) \
                .filter_by(famiport_order_identifier=self.famiport_order_identifier1).one()
            exp_famiport_receipt2 = session.query(FamiPortReceipt) \
                .filter_by(famiport_order_identifier=famiport_order_identifier2).one()

            self.assertEqual('70874', exp_famiport_receipt1.shop_code)
            self.assertIsNone(exp_famiport_receipt1.canceled_at)
            self.assertTrue(exp_famiport_receipt2.shop_code == u'')
            self.assertIsNone(exp_famiport_receipt2.canceled_at)

    def test_process_failure_case(self):
        with mock.patch.object(fcshc.EnvSetup, '__call__', return_value={'registry': self.config.registry}):
            with mock.patch('{}.open'.format(fcshc.__name__), mock.mock_open(read_data=u''), create=True) as mock_open:
                mock_open.side_effect = IOError
                self.assertRaises(IOError, fcshc.main(['', '-C', '/famiport-batch.ini']))
