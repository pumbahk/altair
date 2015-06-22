# encoding: utf-8
import unittest
from pyramid.testing import setUp, tearDown
from altair.sqlahelper import get_global_db_session
from ..testing import _setup_db, _teardown_db

class SalesReportTest(unittest.TestCase):
    def test_basic(self):
        from .sales_report import make_marshaller
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
            'shop': u'0000',
            'settlement_date': date(2015, 1, 1),
            'processed_at': datetime(2015, 1, 1, 0, 0, 0),
            'valid': True,
            'ticket_count': 1,
            'subticket_count': 2,
            })
        self.assertEqual(len(out.getvalue()), 236)


class GenRecordsFromOrderModelTest(unittest.TestCase):
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
            FamiPortEvent, FamiPortClient, FamiPortPlayguide, FamiPortVenue,
            FamiPortGenre1, FamiPortGenre2, FamiPortPerformance, FamiPortSalesSegment,
            )
        from datetime import datetime
        self.famiport_client = FamiPortClient(
            name=u'チケットスター',
            code=u'000',
            playguide=FamiPortPlayguide(discrimination_code=1),
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

    def test_cash_on_delivery_unpaid(self):
        from ..models import FamiPortOrder, FamiPortTicket, FamiPortOrderType, FamiPortReceipt, FamiPortReceiptType
        from datetime import date, datetime
        famiport_order = FamiPortOrder(
            famiport_order_identifier=u'123000000000',
            type=FamiPortOrderType.CashOnDelivery.value,
            famiport_sales_segment=self.famiport_sales_segment,
            created_at=datetime(2014, 12, 31),
            famiport_receipts=[
                FamiPortReceipt(
                    type=FamiPortReceiptType.CashOnDelivery.value,
                    shop_code=u'000000'
                    ),
                ],
            famiport_tickets=[
                FamiPortTicket(
                    barcode_number=u'0000000000000'
                    ),
                ]
            )
        from .sales_report import gen_records_from_order_model
        records = gen_records_from_order_model(famiport_order)
        self.assertEqual(len(records), 0)

    def test_cash_on_delivery_paid(self):
        from ..models import FamiPortOrder, FamiPortTicket, FamiPortOrderType, FamiPortReceipt, FamiPortReceiptType
        from datetime import date, datetime
        famiport_order = FamiPortOrder(
            famiport_order_identifier=u'123000000000',
            type=FamiPortOrderType.CashOnDelivery.value,
            famiport_sales_segment=self.famiport_sales_segment,
            created_at=datetime(2014, 12, 31),
            paid_at=datetime(2014, 12, 31),
            issued_at=datetime(2014, 12, 31),
            famiport_receipts=[
                FamiPortReceipt(
                    type=FamiPortReceiptType.CashOnDelivery.value,
                    shop_code=u'000000',
                    completed_at=datetime(2014, 12, 31)
                    ),
                ],
            famiport_tickets=[
                FamiPortTicket(
                    barcode_number=u'0000000000000'
                    ),
                ]
            )
        from .sales_report import gen_records_from_order_model
        records = gen_records_from_order_model(famiport_order)
        self.assertEqual(len(records), 1)

    def test_payment_unpaid(self):
        from ..models import FamiPortOrder, FamiPortTicket, FamiPortOrderType, FamiPortReceipt, FamiPortReceiptType
        from datetime import date, datetime
        famiport_order = FamiPortOrder(
            famiport_order_identifier=u'123000000000',
            type=FamiPortOrderType.Payment.value,
            famiport_sales_segment=self.famiport_sales_segment,
            created_at=datetime(2014, 12, 31),
            famiport_receipts=[
                FamiPortReceipt(
                    type=FamiPortReceiptType.Payment.value,
                    shop_code=u'000000',
                    completed_at=None
                    ),
                FamiPortReceipt(
                    type=FamiPortReceiptType.Ticketing.value,
                    completed_at=None
                    ),
                ],
            famiport_tickets=[
                FamiPortTicket(
                    barcode_number=u'0000000000000'
                    ),
                ]
            )
        from .sales_report import gen_records_from_order_model
        records = gen_records_from_order_model(famiport_order)
        self.assertEqual(len(records), 0)

    def test_payment_paid(self):
        from ..models import FamiPortOrder, FamiPortTicket, FamiPortOrderType, FamiPortReceipt, FamiPortReceiptType
        from datetime import date, datetime
        famiport_order = FamiPortOrder(
            famiport_order_identifier=u'123000000000',
            type=FamiPortOrderType.Payment.value,
            famiport_sales_segment=self.famiport_sales_segment,
            created_at=datetime(2014, 12, 31),
            paid_at=datetime(2014, 12, 31),
            famiport_receipts=[
                FamiPortReceipt(
                    type=FamiPortReceiptType.Payment.value,
                    shop_code=u'000000',
                    completed_at=datetime(2014, 12, 31)
                    ),
                FamiPortReceipt(
                    type=FamiPortReceiptType.Ticketing.value,
                    shop_code=u'',
                    completed_at=None
                    ),
                ],
            famiport_tickets=[
                FamiPortTicket(
                    barcode_number=u'0000000000000'
                    ),
                ]
            )
        from .sales_report import gen_records_from_order_model
        records = gen_records_from_order_model(famiport_order)
        self.assertEqual(len(records), 1)

    def test_payment_paid_and_issued(self):
        from ..models import FamiPortOrder, FamiPortTicket, FamiPortOrderType, FamiPortReceipt, FamiPortReceiptType
        from datetime import date, datetime
        famiport_order = FamiPortOrder(
            famiport_order_identifier=u'123000000000',
            type=FamiPortOrderType.Payment.value,
            famiport_sales_segment=self.famiport_sales_segment,
            created_at=datetime(2014, 12, 31),
            paid_at=datetime(2014, 12, 31),
            issued_at=datetime(2014, 12, 31),
            famiport_receipts=[
                FamiPortReceipt(
                    type=FamiPortReceiptType.Payment.value,
                    shop_code=u'000000',
                    completed_at=datetime(2014, 12, 31)
                    ),
                FamiPortReceipt(
                    type=FamiPortReceiptType.Ticketing.value,
                    shop_code=u'000000',
                    completed_at=datetime(2014, 12, 31)
                    ),
                ],
            famiport_tickets=[
                FamiPortTicket(
                    barcode_number=u'0000000000000'
                    ),
                ]
            )
        from .sales_report import gen_records_from_order_model
        records = gen_records_from_order_model(famiport_order)
        self.assertEqual(len(records), 2)
