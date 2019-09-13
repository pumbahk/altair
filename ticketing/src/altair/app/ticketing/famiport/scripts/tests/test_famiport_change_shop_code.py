# -*- coding:utf-8 -*-
import mock
import os
import unittest

from datetime import datetime, date
from pyramid.testing import setUp, tearDown

from altair.app.ticketing.famiport.models import FamiPortReceipt
from altair.app.ticketing.famiport.scripts import famiport_change_shop_code as fcshc
from altair.app.ticketing.famiport.testing import _setup_db, _teardown_db
from altair.sqlahelper import get_global_db_session

dirname = os.path.dirname(__file__)
resource_path = os.path.join(dirname, 'resources')


class ChangeShopCodeTest(unittest.TestCase):
    def setUp(self):
        self.filename = 'ChangeStoreCodeList_TS.csv'
        self.err_filename = 'ChangeStoreCodeList_TS_{date:%Y%m%d}_err.csv'
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

        self.default_famiport_order_identifier = u'001002287854'
        default_famiport_receipt = FamiPortReceipt(
            type=2,
            famiport_order_id=7329,
            famiport_order_identifier=self.default_famiport_order_identifier,
            completed_at=datetime(2019, 2, 14, 15, 0, 0),
            rescued_at=datetime(2019, 2, 14, 15, 0, 0),
            created_at=datetime(2019, 2, 14, 12, 0, 0),
        )
        self.session.add(default_famiport_receipt)
        self.session.flush()

    def _get_session(self):
        return get_global_db_session(self.config.registry, 'famiport')

    def _get_famiport_receipts(self, famiport_order_identifiers, session=None):
        if not session:
            session = self._get_session()
        return session.query(FamiPortReceipt)\
            .filter(FamiPortReceipt.famiport_order_identifier.in_(famiport_order_identifiers))

    def tearDown(self):
        _teardown_db(self.config.registry)
        tearDown()

    @mock.patch('os.rename')
    def test_success_case(self, mock_os_rename):
        canceled_famiport_order_identifier = u'003002287856'
        self.session.add(FamiPortReceipt(
            type=2,
            famiport_order_id=7525,
            famiport_order_identifier=canceled_famiport_order_identifier,
            completed_at=datetime(2019, 2, 14, 9, 30, 0),
            rescued_at=datetime(2019, 2, 14, 9, 30, 0),
            created_at=datetime(2019, 2, 14, 5, 3, 0),
        ))
        self.session.flush()

        with mock.patch.object(fcshc, 'date', return_value=mock.Mock(wraps=date)) as mock_date:
            with mock.patch.object(fcshc.EnvSetup, '__call__', return_value={'registry': self.config.registry}):
                mock_date.today.return_value = date(2019, 2, 15)
                fcshc.main(['', '-C', '/famiport-batch.ini'])
                path = os.path.join(resource_path, self.filename)
                mock_os_rename.assert_called_with(path, path)

                default_famiport_receipt, canceled_famiport_receipt = \
                    self._get_famiport_receipts([self.default_famiport_order_identifier,
                                                 canceled_famiport_order_identifier])

                # assert that two receipts' shop_code has been changed
                # second receipt is expected to be canceled
                self.assertEqual('70874', default_famiport_receipt.shop_code)
                self.assertEqual(datetime(2019, 2, 15, 4, 30), default_famiport_receipt.completed_at)
                self.assertEqual('70876', canceled_famiport_receipt.shop_code)
                self.assertEqual(datetime(2019, 2, 15, 4, 30), canceled_famiport_receipt.completed_at)

    @mock.patch('os.rename')
    def test_partial_failure_case(self, mock_os_rename):
        unprocessed_famiport_order_identifier = u'003002287856'
        self.session.add(FamiPortReceipt(
            type=2,
            famiport_order_id=7525,
            famiport_order_identifier=unprocessed_famiport_order_identifier,
            completed_at=datetime(2019, 2, 14, 9, 30, 0),
            rescued_at=datetime(2019, 2, 14, 9, 30, 0),
            created_at=datetime(2019, 2, 14, 5, 3, 0),
        ))
        self.session.add(FamiPortReceipt(
            type=2,
            famiport_order_id=7526,
            famiport_order_identifier=unprocessed_famiport_order_identifier.replace('003', '001'),
            completed_at=datetime(2019, 2, 14, 9, 30, 0),
            rescued_at=datetime(2019, 2, 14, 9, 30, 0),
            created_at=datetime(2019, 2, 14, 5, 3, 0),
        ))
        self.session.flush()

        with mock.patch.object(fcshc, 'date', return_value=mock.Mock(wraps=date)) as mock_date:
            with mock.patch.object(fcshc.EnvSetup, '__call__', return_value={'registry': self.config.registry}):
                mock_date.today.return_value = date(2019, 2, 15)
                fcshc.main(['', '-C', '/famiport-batch.ini'])
                path = os.path.join(resource_path, self.filename)
                err_path = os.path.join(resource_path, self.err_filename.format(date=mock_date.today()))
                mock_os_rename.assert_called_with(path, err_path)

                default_famiport_receipt, unprocessed_famiport_order = \
                    self._get_famiport_receipts([self.default_famiport_order_identifier,
                                                 unprocessed_famiport_order_identifier])

                # assert that first receipt's shop_code has been changed
                # second receipt is expected to be unprocessed due to duplicated management number
                self.assertEqual('70874', default_famiport_receipt.shop_code)
                self.assertEqual(datetime(2019, 2, 15, 4, 30), default_famiport_receipt.completed_at)
                self.assertNotEqual('70876', unprocessed_famiport_order.shop_code)
                self.assertNotEqual(datetime(2019, 2, 15, 4, 30), unprocessed_famiport_order.completed_at)

    def test_process_failure_case(self):
        with mock.patch.object(fcshc.EnvSetup, '__call__', return_value={'registry': self.config.registry}):
            with mock.patch('{}.open'.format(fcshc.__name__), mock.mock_open(read_data=u''), create=True) as mock_open:
                mock_open.side_effect = IOError
                # assert that process ends with exception raised
                self.assertRaises(IOError, fcshc.main(['', '-C', '/famiport-batch.ini']))
