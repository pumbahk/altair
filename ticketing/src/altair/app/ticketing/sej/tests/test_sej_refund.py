# encoding: utf-8
import unittest
from pyramid import testing
import mock
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
                now=datetime(2014, 1, 1, 0, 0, 0)
                )

    def test_with_tickets(self):
        from ..models import ThinSejTenant, SejOrder, SejTicket, SejRefundTicket, SejTicketType
        from datetime import datetime
        from ..exceptions import SejError
        tenant = ThinSejTenant()
        sej_order = SejOrder(
            order_no='XX0000000000',
            tickets=[SejTicket(ticket_type=SejTicketType.TicketWithBarcode.v, barcode_number=u'000000000000')]
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
            now=datetime(2014, 1, 1, 0, 0, 0)
            )
        self.assertTrue(refund_event.id is not None)
        self.assertEqual(self.session.query(SejRefundTicket).filter_by(refund_event_id=refund_event.id).count(), 1)

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
            now=datetime(2014, 1, 1, 0, 0, 0)
            )
        self.assertTrue(refund_event.id is not None)
        self.assertEqual(self.session.query(SejRefundTicket).filter_by(refund_event_id=refund_event.id).count(), 1)
