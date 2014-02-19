# -*- coding:utf-8 -*-

import os
import unittest
from altair.app.ticketing.testing import _setup_db, _teardown_db

class TestCreateRefundZipFile(unittest.TestCase):
    def _getTarget(self):
        from ..ticket import create_refund_zip_file
        return create_refund_zip_file

    def _callFUT(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def setUp(self):
        from tempfile import mkdtemp
        self.work_dir = mkdtemp()
        self.session = _setup_db([
            'altair.app.ticketing.core.models',
            'altair.app.ticketing.sej.models',
            ])

    def _setup_fixtures(self, sent_at, prefix, num_events=3, num_tickets=5):
        from datetime import datetime, timedelta
        from altair.app.ticketing.sej.models import SejRefundEvent, SejRefundTicket
        from decimal import Decimal
        events = [
            SejRefundEvent(
                available=1,
                shop_id='00000', 
                event_code_01=('%sE1%012d' % (prefix, i)),
                event_code_02=('%sE2%012d' % (prefix, i) if i % 2 == 0 else None),
                title=('EVENT-%05d' % i),
                sub_title=('EVENT-SUBTITLE-%05d' % i),
                event_at=(datetime(2014, 1, 1, 0, 0, 0) + timedelta(days=i)),
                start_at=(datetime(2014, 2, 1, 0, 0, 0) + timedelta(days=i)),
                end_at=(datetime(2014, 3, 2, 0, 0, 0) + timedelta(days=i)),
                ticket_expire_at=(datetime(2014, 3, 1, 0, 0, 0) + timedelta(days=i)),
                event_expire_at=(datetime(2014, 3, 3, 0, 0, 0) + timedelta(days=i)),
                refund_enabled=1,
                disapproval_reason=0,
                need_stub=(i % 2),
                remarks=('REMARKS%05d' % i),
                sent_at=sent_at
                )
            for i in range(0, num_events)
            ]
        for i, event in enumerate(events):
            self.session.add(event)
            for j in range(0, num_tickets):
                uniq = '%04d%05d' % (i, j)
                sej_refund_ticket = SejRefundTicket(
                    refund_event=event,
                    available=1,
                    event_code_01=event.event_code_01,
                    event_code_02=event.event_code_02,
                    order_no=('%s0%s' % (prefix, uniq)),
                    ticket_barcode_number=('6300%s' % uniq),
                    refund_ticket_amount=Decimal(i * 10000 + j),
                    refund_other_amount=Decimal(i * 100),
                    sent_at=sent_at
                    )
                self.session.add(sej_refund_ticket)
        self.session.flush()

    def tearDown(self):
        _teardown_db()
        for parent_dir, dirs, files in os.walk(self.work_dir, topdown=False):
            for file in files:
                os.unlink(os.path.join(parent_dir, file))
        os.removedirs(self.work_dir)

    def test_no_refund_event(self):
        from datetime import datetime
        from ..zip_file import EnhZipFile
        self._callFUT(now=datetime(2014, 1, 1, 0, 0, 0), work_dir=self.work_dir)
        refund_event_file_name = '20140101_TPBKOEN.dat'
        refund_ticket_file_name = '20140101_TPBTICKET.dat'
        self.assertTrue(os.path.exists(os.path.join(self.work_dir, 'archive.txt')))
        self.assertTrue(os.path.exists(os.path.join(self.work_dir, refund_event_file_name)))
        self.assertTrue(os.path.exists(os.path.join(self.work_dir, refund_ticket_file_name)))
        zip_file_path = os.path.join(self.work_dir, '20140101.zip')
        self.assertFalse(os.path.exists(zip_file_path))

    def test_before_six(self):
        from datetime import datetime
        from ..zip_file import EnhZipFile
        self._setup_fixtures(sent_at=datetime(2014, 1, 1, 0, 0, 0), prefix='TT', num_events=3, num_tickets=5)
        self._callFUT(now=datetime(2014, 1, 1, 0, 0, 0), work_dir=self.work_dir)
        refund_event_file_name = '20140101_TPBKOEN.dat'
        refund_ticket_file_name = '20140101_TPBTICKET.dat'
        self.assertTrue(os.path.exists(os.path.join(self.work_dir, 'archive.txt')))
        self.assertTrue(os.path.exists(os.path.join(self.work_dir, refund_event_file_name)))
        self.assertTrue(os.path.exists(os.path.join(self.work_dir, refund_ticket_file_name)))
        zip_file_path = os.path.join(self.work_dir, '20140101.zip')
        self.assertTrue(os.path.exists(zip_file_path))
        z = EnhZipFile(zip_file_path, 'r')
        self.assertEqual(set(z.namelist()), {
            'archive.txt',
            refund_event_file_name,
            refund_ticket_file_name,
            })
        self.assertEqual(
            [l.rstrip() for l in z.open('archive.txt')],
            [refund_event_file_name, refund_ticket_file_name]
            )
        self.assertEqual(
            sum(1 for _ in z.open(refund_event_file_name)),
            3
            )
        self.assertEqual(
            sum(1 for _ in z.open(refund_ticket_file_name)),
            15
            )

    def test_after_six(self):
        from datetime import datetime
        from ..zip_file import EnhZipFile
        self._setup_fixtures(sent_at=datetime(2014, 1, 1, 0, 0, 0), prefix='TA', num_events=3, num_tickets=2)
        self._setup_fixtures(sent_at=datetime(2014, 1, 1, 6, 0, 0), prefix='TB', num_events=7, num_tickets=3)
        self._setup_fixtures(sent_at=datetime(2014, 1, 2, 0, 0, 0), prefix='TC', num_events=11, num_tickets=7)
        self._setup_fixtures(sent_at=datetime(2014, 1, 2, 6, 0, 0), prefix='TD', num_events=13, num_tickets=11)
        self._callFUT(now=datetime(2014, 1, 1, 6, 0, 0), work_dir=self.work_dir)
        refund_event_file_name = '20140102_TPBKOEN.dat'
        refund_ticket_file_name = '20140102_TPBTICKET.dat'
        self.assertTrue(os.path.exists(os.path.join(self.work_dir, 'archive.txt')))
        self.assertTrue(os.path.exists(os.path.join(self.work_dir, refund_event_file_name)))
        self.assertTrue(os.path.exists(os.path.join(self.work_dir, refund_ticket_file_name)))
        zip_file_path = os.path.join(self.work_dir, '20140102.zip')
        self.assertTrue(os.path.exists(zip_file_path))
        z = EnhZipFile(zip_file_path, 'r')
        self.assertEqual(set(z.namelist()), {
            'archive.txt',
            refund_event_file_name,
            refund_ticket_file_name,
            })
        self.assertEqual(
            [l.rstrip() for l in z.open('archive.txt')],
            [refund_event_file_name, refund_ticket_file_name]
            )
        self.assertEqual(
            sum(1 for _ in z.open(refund_event_file_name)),
            34
            )
        self.assertEqual(
            sum(1 for _ in z.open(refund_ticket_file_name)),
            98
            )
