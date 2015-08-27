# encoding: utf-8
import unittest
from altair.sqlahelper import get_global_db_session
from pyramid.testing import setUp, tearDown
from ..testing import _setup_db, _teardown_db

class RefundReportMarshallerTest(unittest.TestCase):
    def test_basic(self):
        from .refund_report import make_marshaller
        from io import BytesIO
        from datetime import datetime, date
        from decimal import Decimal
        out = BytesIO()
        target = make_marshaller(out, encoding='CP932', eor='\n')
        target({
            'unique_key': u'0',
            'type': 0,
            'management_number': u'0',
            'event_code': u'0',
            'event_code_sub': u'0',
            'sales_segment_code': u'0',
            'performance_code': u'0',
            'event_name': u'イベント名',
            'performance_date': datetime(2015, 1, 1, 0, 0, 0),
            'ticket_payment': Decimal(1000),
            'ticketing_fee': Decimal(50),
            'other_fees': Decimal(100),
            'start_at': datetime(2015, 1, 1, 0, 0, 0),
            'end_at': datetime(2015, 1, 10, 0, 0, 0),
            'processed_at': datetime(2015, 1, 5, 0, 0),
            'shop': u'0000',
            'shop_of_issue': u'0001',
            'issued_at': datetime(2015, 1, 1, 0, 0, 0),
            'valid': True,
            'barcode_number': u'000000000000',
            'send_back_due_at': date(2015, 1, 20),
            })
        self.assertEqual(len(out.getvalue()), 287)

    def test_halfwidth(self):
        from .refund_report import make_marshaller
        from io import BytesIO
        from datetime import datetime, date
        from decimal import Decimal
        out = BytesIO()
        target = make_marshaller(out, encoding='CP932', eor='\n')
        target({
            'unique_key': u'0',
            'type': 0,
            'management_number': u'0',
            'event_code': u'0',
            'event_code_sub': u'0',
            'sales_segment_code': u'0',
            'performance_code': u'0',
            'event_name': u'イベント123',
            'performance_date': datetime(2015, 1, 1, 0, 0, 0),
            'ticket_payment': Decimal(1000),
            'ticketing_fee': Decimal(50),
            'other_fees': Decimal(100),
            'start_at': datetime(2015, 1, 1, 0, 0, 0),
            'end_at': datetime(2015, 1, 10, 0, 0, 0),
            'processed_at': datetime(2015, 1, 5, 0, 0),
            'shop': u'0000',
            'shop_of_issue': u'0001',
            'issued_at': datetime(2015, 1, 1, 0, 0, 0),
            'valid': True,
            'barcode_number': u'000000000000',
            'send_back_due_at': date(2015, 1, 20),
            })
        result = out.getvalue()
        self.assertEqual(len(result), 287)
        self.assertTrue(u'イベント１２３'.encode('CP932') in result)


class RefundReportGenRecordTest(unittest.TestCase):
    def setUp(self):
        self.config = setUp()
        self.engine = _setup_db(
            self.config.registry,
            [
                'altair.app.ticketing.famiport.models',
                ]
            )
        self.session = get_global_db_session(self.config.registry, 'famiport')
        from ..models import (
            FamiPortEvent, FamiPortClient, FamiPortPlayguide,
            FamiPortVenue, FamiPortGenre1, FamiPortGenre2,
            FamiPortPerformance, FamiPortSalesSegment,
            )
        from datetime import datetime
        self.famiport_client = FamiPortClient(
            name=u'チケットスター',
            code=u'000',
            playguide=FamiPortPlayguide(discrimination_code=1, discrimination_code_2=1),
            prefix=u'XXX'
            )
        self.famiport_event = FamiPortEvent(
            code_1=u'000000',
            code_2=u'0000',
            name_1=u'name_1',
            name_2=u'name_2',
            client=self.famiport_client,
            venue=FamiPortVenue(name=u'venue', name_kana=u'ヴェニュー', client_code=u'00000000000000000000123'),
            genre_1=FamiPortGenre1(code=1, name=u'genre1'),
            genre_2=FamiPortGenre2(genre_1_code=1, code=2, name=u'genre2'),
            keywords=[u'a', u'b', u'c'],
            search_code=u'search'
            )
        self.famiport_performance = FamiPortPerformance(
            famiport_event=self.famiport_event,
            code=u'000',
            name=u'performance',
            )
        self.famiport_sales_segment = FamiPortSalesSegment(
            code=u'000',
            famiport_performance=self.famiport_performance,
            name=u'name',
            start_at=datetime(2015, 1, 1),
            end_at=datetime(2015, 1, 7),
            )
        self.session.add(self.famiport_sales_segment)
        self.session.flush()

    def tearDown(self):
        _teardown_db(self.config.registry)
        tearDown()

    def test_gen(self):
        from datetime import datetime
        from decimal import Decimal
        from .refund_report import gen_record_from_refund_model
        from ..models import (
            FamiPortRefundType,
            FamiPortRefund,
            FamiPortRefundEntry,
            FamiPortOrder,
            FamiPortReceipt,
            FamiPortTicket,
            FamiPortOrderType,
            FamiPortReceiptType,
            )
        refund = FamiPortRefund(
            type=FamiPortRefundType.Type1.value,
            start_at=datetime(2015, 1, 1, 10, 0, 0),
            end_at=datetime(2015, 1, 7, 23, 59, 59),
            send_back_due_at=datetime(2015, 2, 1),
            client_code='00001',
            last_serial=0
            )
        refund_entry = FamiPortRefundEntry(
            famiport_refund=refund,
            serial=refund.last_serial + 1,
            ticket_payment=Decimal(100),
            ticketing_fee=Decimal(10),
            other_fees=Decimal(20),
            shop_code=u'0000000',
            famiport_ticket=FamiPortTicket(
                template_code=u'TTXX000000',
                barcode_number=u'0000000000000',
                data=u'',
                famiport_order=FamiPortOrder(
                    type=FamiPortOrderType.CashOnDelivery.value,
                    order_no=u'XX0000000000',
                    client_code=u'0',
                    famiport_order_identifier=u'123000000000',
                    total_amount=Decimal(130),
                    ticket_payment=Decimal(100),
                    ticketing_fee=Decimal(10),
                    system_fee=Decimal(20),
                    customer_name=u'',
                    customer_phone_number=u'',
                    famiport_sales_segment=self.famiport_sales_segment,
                    famiport_performance=self.famiport_performance,
                    famiport_receipts=[
                        FamiPortReceipt(
                            type=FamiPortReceiptType.CashOnDelivery.value,
                            famiport_order_identifier=u'123000000001',
                            shop_code=u'0000000',
                            barcode_no=u'0000000000001'
                            )
                        ]
                    )
                )
            )
        self.session.add(refund_entry)
        self.session.flush()
        gen_record_from_refund_model(refund_entry)


class BuildRefundReportFileTest(unittest.TestCase):
    def setUp(self):
        self.config = setUp()
        self.engine = _setup_db(
            self.config.registry,
            [
                'altair.app.ticketing.famiport.models',
                ]
            )
        self.session = get_global_db_session(self.config.registry, 'famiport')
        from ..models import (
            FamiPortEvent, FamiPortClient, FamiPortPlayguide,
            FamiPortVenue, FamiPortGenre1, FamiPortGenre2, FamiPortPerformance,
            FamiPortSalesSegment,
            )
        from datetime import datetime
        self.famiport_client = FamiPortClient(
            name=u'チケットスター',
            code=u'000',
            playguide=FamiPortPlayguide(discrimination_code=1, discrimination_code_2=1),
            prefix=u'XXX'
            )
        self.famiport_event = FamiPortEvent(
            code_1=u'000000',
            code_2=u'0000',
            name_1=u'イベント',
            name_2=u'イベント副題',
            client=self.famiport_client,
            venue=FamiPortVenue(name=u'venue', name_kana=u'ヴェニュー', client_code=u'00000000000000000000123'),
            genre_1=FamiPortGenre1(code=1, name=u'genre1'),
            genre_2=FamiPortGenre2(genre_1_code=1, code=2, name=u'genre2'),
            keywords=[u'a', u'b', u'c'],
            search_code=u'search'
            )
        self.famiport_performance = FamiPortPerformance(
            famiport_event=self.famiport_event,
            code=u'000',
            name=u'performance',
            start_at=datetime(2015, 2, 2)
            )
        self.famiport_sales_segment = FamiPortSalesSegment(
            code=u'000',
            famiport_performance=self.famiport_performance,
            name=u'name',
            start_at=datetime(2015, 1, 1),
            end_at=datetime(2015, 1, 7),
            )
        self.session.add(self.famiport_sales_segment)
        self.session.flush()

    def tearDown(self):
        _teardown_db(self.config.registry)
        tearDown()

    def test_it(self):
        from datetime import datetime, date
        from io import BytesIO
        from decimal import Decimal
        from .refund_report import build_refund_file
        from ..models import (
            FamiPortRefundType,
            FamiPortRefund,
            FamiPortRefundEntry,
            FamiPortOrder,
            FamiPortReceipt,
            FamiPortTicket,
            FamiPortOrderType,
            FamiPortReceiptType,
            )
        refunds = [
            FamiPortRefund(
                type=FamiPortRefundType.Type1.value,
                start_at=datetime(2015, 1, 1, 10, 0, 0),
                end_at=datetime(2015, 1, 7, 23, 59, 59),
                send_back_due_at=date(2015, 2, 1),
                client_code='00001',
                last_serial=0
                )
            for _ in range(0, 10)
            ]
        refund_entries = [
            FamiPortRefundEntry(
                famiport_refund=refund,
                serial=refund.last_serial + i,
                ticket_payment=Decimal(100),
                ticketing_fee=Decimal(10),
                other_fees=Decimal(20),
                shop_code=u'0000000',
                refunded_at=datetime(2015, 1, 3, 0, 0, 0),
                famiport_ticket=FamiPortTicket(
                    template_code=u'TTXX000000',
                    barcode_number=u'0000000000000',
                    data=u'',
                    issued_at=datetime(2014, 12, 31),
                    famiport_order=FamiPortOrder(
                        type=FamiPortOrderType.CashOnDelivery.value,
                        order_no=u'XX0000000000',
                        client_code=u'0',
                        famiport_order_identifier=u'123%09d' % (j * 10 + i),
                        famiport_sales_segment=self.famiport_sales_segment,
                        famiport_performance=self.famiport_performance,
                        total_amount=Decimal(130),
                        ticket_payment=Decimal(100),
                        ticketing_fee=Decimal(10),
                        system_fee=Decimal(20),
                        customer_name=u'',
                        customer_phone_number=u'',
                        created_at=datetime(2014, 12, 31),
                        famiport_receipts=[
                            FamiPortReceipt(
                                type=FamiPortReceiptType.CashOnDelivery.value,
                                famiport_order_identifier=u'124%09d' % (j * 10 + i),
                                shop_code=u'000000',
                                barcode_no=u'1%012d' % (j * 10 + i)
                                )
                            ],
                        )
                    )
                )
            for j, refund in enumerate(refunds)
            for i in range(0, 10)
            ]
        self.session.add_all(refund_entries)
        self.session.flush()
        f = BytesIO()
        eor = '\n'
        build_refund_file(f, refund_entries, eor=eor)
        self.assertEqual(f.getvalue().count(eor), 100)
