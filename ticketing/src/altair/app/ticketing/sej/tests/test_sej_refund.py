# encoding: utf-8
import os
import unittest
import mock
from pyramid import testing
from altair.app.ticketing.testing import _setup_db, _teardown_db

class RefundSejOrderTest(unittest.TestCase):
    def setUp(self):
        self.session = _setup_db([
            'altair.app.ticketing.core.models',
            'altair.app.ticketing.orders.models',
            'altair.app.ticketing.lots.models',
            'altair.app.ticketing.sej.models'
            ])
        self.config = testing.setUp()
        self.request = testing.DummyRequest()
        self.config.include('altair.app.ticketing.sej')

    def tearDown(self):
        testing.tearDown()
        from ..api import remove_default_session
        remove_default_session()
        _teardown_db()

    def _getTarget(self):
        from ..api import refund_sej_order
        return refund_sej_order

    def _callFUT(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs) 

    def test_without_tickets(self):
        from ..models import ThinSejTenant, SejOrder
        from datetime import datetime
        from ..exceptions import SejError
        tenant = ThinSejTenant()
        sej_order = SejOrder(order_no='XX0000000000')
        ticket_price_getter = mock.Mock(return_value=10.)
        with self.assertRaises(SejError):
            self._callFUT(
                self.request,
                tenant=tenant,
                sej_order=sej_order,
                performance_name=u'パフォーマンス名',
                performance_code=u'000000',
                performance_start_on=datetime(2014, 3, 1, 0, 0, 0),
                per_order_fee=0.,
                per_ticket_fee=0.,
                ticket_price_getter=ticket_price_getter,
                refund_start_at=datetime(2014, 1, 1, 0, 0, 0),
                refund_end_at=datetime(2014, 2, 1, 0, 0, 0),
                need_stub=0,
                ticket_expire_at=datetime(2014, 2, 1, 0, 0, 0),
                refund_total_amount=10,
                now=datetime(2014, 1, 1, 0, 0, 0)
                )

    def test_without_applicable_tickets(self):
        from ..models import ThinSejTenant, SejOrder, SejTicket, SejRefundTicket, SejTicketType
        from datetime import datetime
        from ..exceptions import SejError
        tenant = ThinSejTenant()
        sej_order = SejOrder(
            order_no='XX0000000000',
            tickets=[SejTicket(ticket_type=SejTicketType.Ticket.v, barcode_number=None)]
            )
        ticket_price_getter = mock.Mock(return_value=10.)
        refund_event = self._callFUT(
            self.request,
            tenant=tenant,
            sej_order=sej_order,
            performance_name=u'パフォーマンス名',
            performance_code=u'000000',
            performance_start_on=datetime(2014, 3, 1, 0, 0, 0),
            per_order_fee=0.,
            per_ticket_fee=0.,
            ticket_price_getter=ticket_price_getter,
            refund_start_at=datetime(2014, 1, 1, 0, 0, 0),
            refund_end_at=datetime(2014, 2, 1, 0, 0, 0),
            need_stub=0,
            ticket_expire_at=datetime(2014, 2, 1, 0, 0, 0),
            refund_total_amount=10,
            now=datetime(2014, 1, 1, 0, 0, 0)
            )
        self.assertEqual(self.session.query(SejRefundTicket).filter_by(refund_event_id=refund_event.id).count(), 0)

    def test_with_tickets(self):
        from ..models import ThinSejTenant, SejOrder, SejTicket, SejRefundTicket, SejTicketType
        from datetime import datetime
        from ..exceptions import SejError
        tenant = ThinSejTenant()
        sej_order = SejOrder(
            order_no='XX0000000000',
            tickets=[
                SejTicket(ticket_type=SejTicketType.TicketWithBarcode.v, barcode_number=u'000000000000'),
                SejTicket(ticket_type=SejTicketType.TicketWithBarcode.v, barcode_number=u'111111111111')
                ]
            )
        ticket_price_getter = mock.Mock(return_value=10.)
        refund_event = self._callFUT(
            self.request,
            tenant=tenant,
            sej_order=sej_order,
            performance_name=u'パフォーマンス名',
            performance_code=u'000000',
            performance_start_on=datetime(2014, 3, 1, 0, 0, 0),
            per_order_fee=0.,
            per_ticket_fee=0.,
            ticket_price_getter=ticket_price_getter,
            refund_start_at=datetime(2014, 1, 1, 0, 0, 0),
            refund_end_at=datetime(2014, 2, 1, 0, 0, 0),
            need_stub=0,
            ticket_expire_at=datetime(2014, 2, 1, 0, 0, 0),
            refund_total_amount=20,
            now=datetime(2014, 1, 1, 0, 0, 0)
            )
        self.assertTrue(refund_event.id is not None)
        self.assertEqual(self.session.query(SejRefundTicket).filter_by(refund_event_id=refund_event.id).count(), 2)

    def test_with_tickets_without_barcodes(self):
        from ..models import ThinSejTenant, SejOrder, SejTicket, SejRefundTicket, SejTicketType
        from datetime import datetime
        from ..exceptions import SejError
        tenant = ThinSejTenant()
        sej_order = SejOrder(
            order_no='XX0000000000',
            tickets=[
                SejTicket(ticket_type=SejTicketType.Ticket.v, barcode_number=None),
                SejTicket(ticket_type=SejTicketType.Ticket.v, barcode_number=None),
                SejTicket(ticket_type=SejTicketType.TicketWithBarcode.v, barcode_number=u'000000000000'),
                ]
            )
        ticket_price_getter = mock.Mock(return_value=10.)
        refund_event = self._callFUT(
            self.request,
            tenant=tenant,
            sej_order=sej_order,
            performance_name=u'パフォーマンス名',
            performance_code=u'000000',
            performance_start_on=datetime(2014, 3, 1, 0, 0, 0),
            per_order_fee=0.,
            per_ticket_fee=0.,
            ticket_price_getter=ticket_price_getter,
            refund_start_at=datetime(2014, 1, 1, 0, 0, 0),
            refund_end_at=datetime(2014, 2, 1, 0, 0, 0),
            need_stub=0,
            ticket_expire_at=datetime(2014, 2, 1, 0, 0, 0),
            refund_total_amount=10,
            now=datetime(2014, 1, 1, 0, 0, 0)
            )
        self.assertTrue(refund_event.id is not None)
        self.assertEqual(self.session.query(SejRefundTicket).filter_by(refund_event_id=refund_event.id).count(), 1)

    def test_with_tickets_zero_refund(self):
        from ..models import ThinSejTenant, SejOrder, SejTicket, SejRefundTicket, SejTicketType
        from datetime import datetime
        from ..exceptions import SejError
        tenant = ThinSejTenant()
        sej_order = SejOrder(
            order_no='XX0000000000',
            tickets=[
                SejTicket(ticket_type=SejTicketType.TicketWithBarcode.v, barcode_number=u'000000000000'),
                SejTicket(ticket_type=SejTicketType.TicketWithBarcode.v, barcode_number=u'111111111111')
                ]
            )
        ticket_price_getter = mock.Mock(return_value=0.)
        refund_event = self._callFUT(
            self.request,
            tenant=tenant,
            sej_order=sej_order,
            performance_name=u'パフォーマンス名',
            performance_code=u'000000',
            performance_start_on=datetime(2014, 3, 1, 0, 0, 0),
            per_order_fee=0.,
            per_ticket_fee=0.,
            ticket_price_getter=ticket_price_getter,
            refund_start_at=datetime(2014, 1, 1, 0, 0, 0),
            refund_end_at=datetime(2014, 2, 1, 0, 0, 0),
            need_stub=0,
            ticket_expire_at=datetime(2014, 2, 1, 0, 0, 0),
            refund_total_amount=20,
            now=datetime(2014, 1, 1, 0, 0, 0)
            )
        self.assertTrue(refund_event.id is not None)
        self.assertEqual(self.session.query(SejRefundTicket).filter_by(refund_event_id=refund_event.id).count(), 0)

    def test_total_amount_over(self):
        from ..models import ThinSejTenant, SejOrder, SejTicket, SejRefundTicket, SejTicketType
        from datetime import datetime
        from ..exceptions import SejError, RefundTotalAmountOverError
        tenant = ThinSejTenant()
        sej_order = SejOrder(
            order_no='XX0000000000',
            tickets=[
                SejTicket(ticket_type=SejTicketType.TicketWithBarcode.v, barcode_number=u'000000000000'),
                SejTicket(ticket_type=SejTicketType.TicketWithBarcode.v, barcode_number=u'111111111111'),
                ]
            )
        ticket_price_getter = mock.Mock(return_value=10.)
        with self.assertRaises(RefundTotalAmountOverError):
            refund_event = self._callFUT(
                self.request,
                tenant=tenant,
                sej_order=sej_order,
                performance_name=u'パフォーマンス名',
                performance_code=u'000000',
                performance_start_on=datetime(2014, 3, 1, 0, 0, 0),
                per_order_fee=0.,
                per_ticket_fee=0.,
                ticket_price_getter=ticket_price_getter,
                refund_start_at=datetime(2014, 1, 1, 0, 0, 0),
                refund_end_at=datetime(2014, 2, 1, 0, 0, 0),
                need_stub=0,
                ticket_expire_at=datetime(2014, 2, 1, 0, 0, 0),
                refund_total_amount=10,
                now=datetime(2014, 1, 1, 0, 0, 0)
                )

class TestCreateRefundZipFile(unittest.TestCase):
    def _getTarget(self):
        from ..refund import create_refund_zip_files
        return create_refund_zip_files

    def _callFUT(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def setUp(self):
        from tempfile import mkdtemp
        self.work_dir_base = mkdtemp()
        self.session = _setup_db([
            'altair.app.ticketing.core.models',
            'altair.app.ticketing.orders.models',
            'altair.app.ticketing.lots.models',
            'altair.app.ticketing.sej.models',
            ])
        self.per_nwts_info_dir_list = set()

    def _setup_fixtures(self, sent_at, prefix, num_events=3, num_tickets=5):
        from datetime import datetime, timedelta
        from altair.app.ticketing.sej.models import SejRefundEvent, SejRefundTicket
        from decimal import Decimal
        for i in range(0, 4):
            nwts_endpoint_url = 'http://www.example.com/sdmt%d' % i
            nwts_terminal_id = '60022'
            nwts_password = '60022X'
            per_nwts_info_dir = 'www.example.com--sdmt%d-60022-60022X' % i
            self.per_nwts_info_dir_list.add(per_nwts_info_dir)
            events = [
                SejRefundEvent(
                    available=1,
                    shop_id='00000',
                    nwts_endpoint_url=nwts_endpoint_url,
                    nwts_terminal_id=nwts_terminal_id,
                    nwts_password=nwts_password,
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
        for parent_dir, dirs, files in os.walk(self.work_dir_base, topdown=False):
            for file in files:
                os.unlink(os.path.join(parent_dir, file))
            for dir in dirs:
                os.rmdir(os.path.join(parent_dir, dir))
        os.rmdir(self.work_dir_base)

    def test_no_refund_event(self):
        from datetime import datetime
        from ..zip_file import EnhZipFile
        self._callFUT(session=self.session, now=datetime(2014, 1, 1, 0, 0, 0), work_dir_base=self.work_dir_base)
        refund_event_file_name = '20140101_TPBKOEN.dat'
        refund_ticket_file_name = '20140101_TPBTICKET.dat'
        self.assertEqual(len(os.listdir(self.work_dir_base)), 0)

    def test_before_six(self):
        from datetime import datetime
        from ..zip_file import EnhZipFile
        self._setup_fixtures(sent_at=datetime(2014, 1, 1, 0, 0, 0), prefix='TT', num_events=3, num_tickets=5)
        self._callFUT(session=self.session, now=datetime(2014, 1, 1, 0, 0, 0), work_dir_base=self.work_dir_base)
        refund_event_file_name = '20140101_TPBKOEN.dat'
        refund_ticket_file_name = '20140101_TPBTICKET.dat'
        for per_nwts_info_dir in self.per_nwts_info_dir_list:
            work_dir = os.path.join(self.work_dir_base, per_nwts_info_dir)
            self.assertTrue(os.path.exists(os.path.join(work_dir, 'archive.txt')))
            self.assertTrue(os.path.exists(os.path.join(work_dir, refund_event_file_name)))
            self.assertTrue(os.path.exists(os.path.join(work_dir, refund_ticket_file_name)))
            zip_file_path = os.path.join(work_dir, '20140101.zip')
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
        self._callFUT(session=self.session, now=datetime(2014, 1, 1, 6, 0, 0), work_dir_base=self.work_dir_base)
        refund_event_file_name = '20140102_TPBKOEN.dat'
        refund_ticket_file_name = '20140102_TPBTICKET.dat'
        for per_nwts_info_dir in self.per_nwts_info_dir_list:
            work_dir = os.path.join(self.work_dir_base, per_nwts_info_dir)
            self.assertTrue(os.path.exists(os.path.join(work_dir, 'archive.txt')))
            self.assertTrue(os.path.exists(os.path.join(work_dir, refund_event_file_name)))
            self.assertTrue(os.path.exists(os.path.join(work_dir, refund_ticket_file_name)))
            zip_file_path = os.path.join(work_dir, '20140102.zip')
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

