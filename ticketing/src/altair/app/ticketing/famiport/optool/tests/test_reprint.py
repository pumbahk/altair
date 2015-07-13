# -*- coding:utf-8 -*-

from unittest import TestCase
from pyramid.testing import DummyRequest, setUp, tearDown
from altair.app.ticketing.famiport.testing import _setup_db, _teardown_db
from altair.sqlahelper import get_global_db_session
from altair.app.ticketing.famiport.models import (
            FamiPortPrefecture,
            FamiPortPlayguide,
            FamiPortClient,
            FamiPortVenue,
            FamiPortGenre1,
            FamiPortGenre2,
            FamiPortSalesChannel,
            FamiPortPerformanceType,
            FamiPortEvent,
            FamiPortPerformance,
            FamiPortSalesSegment,
            FamiPortOrder,
            FamiPortReceipt,
            FamiPortOrderType,
            FamiPortReceiptType,
            FamiPortTicketType,
            FamiPortTicket,
            )
from ..utils import ValidateUtils
from datetime import datetime, timedelta

class ReprintTest(TestCase):
    def setUp(self):
        self.request = DummyRequest()
        self.config = setUp(request=self.request)
        self.engine = _setup_db(
            self.config.registry,
            [
                'altair.app.ticketing.famiport.models',
                'altair.app.ticketing.famiport.optool.models',
                ]
            )
        self.session = get_global_db_session(self.config.registry, 'famiport')

    def tearDown(self):
        _teardown_db(self.config.registry)
        tearDown()

    def test_canceled_receipt(self):
        canceled_payment_receipt = FamiPortReceipt(
                    type=FamiPortReceiptType.Payment.value,
                    famiport_order_identifier=u'RT0000000000',
                    barcode_no=u'01234012340123',
                    shop_code=u'00000',
                    reserve_number=u'4321043210430',
                    payment_request_received_at=datetime.now() -  timedelta(days=1),
                    canceled_at=datetime.now() - timedelta(minutes=10)
                )

        canceled_ticketing_receipt = FamiPortReceipt(
                    type=FamiPortReceiptType.Ticketing.value,
                    famiport_order_identifier=u'RT0000000001',
                    barcode_no=u'01234012340124',
                    shop_code=u'00000',
                    reserve_number=u'4321043210431',
                    payment_request_received_at=datetime.now() -  timedelta(days=1),
                    canceled_at=datetime.now() - timedelta(minutes=10)
                )

        famiport_playguide = FamiPortPlayguide(
            discrimination_code=5
            )
        famiport_client = FamiPortClient(
            playguide=famiport_playguide,
            code=u'012340123401234012340123',
            name=u'チケットスター',
            prefix=u'TTT'
            )
        famiport_genre_1 = FamiPortGenre1(
            code=1,
            name=u'大ジャンル'
            )
        famiport_genre_2 = FamiPortGenre2(
            genre_1=famiport_genre_1,
            code=2,
            name=u'小ジャンル'
            )
        famiport_venue = FamiPortVenue(
            client_code=u'012340123401234012340123',
            name=u'博品館劇場',
            name_kana=u'ハクヒンカンゲキジョウ',
            prefecture=FamiPortPrefecture.Tokyo.id
            )
        famiport_event = FamiPortEvent(
            client=famiport_client,
            venue=famiport_venue,
            genre_1=famiport_genre_1,
            genre_2=famiport_genre_2,
            sales_channel=FamiPortSalesChannel.FamiPortAndWeb.value,
            code_1=u'000000',
            code_2=u'1111',
            name_1=u'テスト公演',
            name_2=u'テスト公演副題',
            start_at=datetime(2015, 7, 1, 19, 0, 0),
            end_at=datetime(2015, 7, 10, 23, 59, 59),
            keywords=[u'チケットスター', u'博品館', u'イベント'],
            purchasable_prefectures=[u'%02d' % FamiPortPrefecture.Nationwide.id],
            )
        famiport_performance = FamiPortPerformance(
            famiport_event=famiport_event,
            code=u'001',
            name=u'7/1公演',
            type=FamiPortPerformanceType.Normal.value,
            searchable=False,
            sales_channel=FamiPortSalesChannel.FamiPortAndWeb.value,
            start_at=datetime(2015, 7, 1, 19, 0, 0),
            ticket_name=u''
            )
        famiport_sales_segment = FamiPortSalesSegment(
            famiport_performance=famiport_performance,
            code=u'001',
            name=u'一般販売',
            sales_channel=FamiPortSalesChannel.FamiPortAndWeb.value,
            published_at=datetime(2015, 4, 15, 0, 0, 0),
            start_at=datetime(2015, 5, 1, 23, 59, 59),
            end_at=datetime(2015, 5, 31, 23, 59, 59),
            auth_required=False,
            auth_message=u'',
            seat_selection_start_at=datetime(2015, 5, 10, 10, 0, 0)
            )

        famiport_order_payment = FamiPortOrder(
            type=FamiPortOrderType.Payment.value,
            order_no=u'RT0000000001',
            famiport_order_identifier=u'RT0000000001',
            famiport_sales_segment=famiport_sales_segment,
            famiport_client=famiport_client,
            generation=0,
            invalidated_at=None,
            total_amount=10540,
            ticket_payment=10000,
            ticketing_fee=216,
            system_fee=324,
            paid_at=None,
            issued_at=None,
            canceled_at=None,
            ticketing_start_at=datetime.now() - timedelta(days=1),
            ticketing_end_at=datetime.now() + timedelta(days=5),
            payment_start_at=datetime.now() - timedelta(days=1),
            payment_due_at=datetime.now() + timedelta(days=5),
            customer_name=u'チケット　太郎',
            customer_address_1=u'東京都品川区西五反田7-1-9',
            customer_address_2=u'五反田HSビル9F',
            customer_phone_number=u'0301234567',
            famiport_receipts=[canceled_payment_receipt, canceled_ticketing_receipt],
            famiport_tickets=[
                FamiPortTicket(
                    type=FamiPortTicketType.TicketWithBarcode.value,
                    barcode_number=u'0000000000001',
                    template_code=u'TTTS000001',
                    data=u'<?xml version="1.0" encoding="Shift_JIS"><TICKET></TICKET>',
                    issued_at=None
                    ),
                FamiPortTicket(
                    type=FamiPortTicketType.TicketWithBarcode.value,
                    barcode_number=u'0000000000002',
                    template_code=u'TTTS000001',
                    data=u'<?xml version="1.0" encoding="Shift_JIS"><TICKET></TICKET>',
                    issued_at=None
                    )
                ],
            customer_name_input=False,
            customer_phone_input=False,
            created_at=datetime.now()
            )

        self.session.add(famiport_order_payment)

        canceled_cash_on_delivery_receipt = FamiPortReceipt(
                    type=FamiPortReceiptType.CashOnDelivery.value,
                    famiport_order_identifier=u'RT0000000002',
                    barcode_no=u'01234012340125',
                    shop_code=u'00009',
                    reserve_number=u'4321043210432',
                    payment_request_received_at=datetime.now() -  timedelta(days=1),
                    canceled_at=datetime.now() - timedelta(minutes=10)
                )

        famiport_order_cash_on_delivery = FamiPortOrder(
            type=FamiPortOrderType.CashOnDelivery.value,
            order_no=u'RT0000000002',
            famiport_order_identifier=u'RT0000000002',
            famiport_sales_segment=famiport_sales_segment,
            famiport_client=famiport_client,
            generation=0,
            invalidated_at=None,
            total_amount=10540,
            ticket_payment=10000,
            ticketing_fee=216,
            system_fee=324,
            paid_at=None,
            issued_at=None,
            canceled_at=None,
            ticketing_start_at=datetime(2015, 5, 20, 12, 34, 56),
            ticketing_end_at=datetime(2015, 5, 23, 23, 59, 59),
            payment_start_at=datetime(2015, 5, 20, 12, 34, 56),
            payment_due_at=datetime(2015, 5, 23, 23, 59, 59),
            customer_name=u'チケット　太郎',
            customer_address_1=u'東京都品川区西五反田7-1-9',
            customer_address_2=u'五反田HSビル9F',
            customer_phone_number=u'0301234567',
            famiport_receipts=[canceled_cash_on_delivery_receipt],
            famiport_tickets=[
                FamiPortTicket(
                    type=FamiPortTicketType.TicketWithBarcode.value,
                    barcode_number=u'0000000000003',
                    template_code=u'TTTS000003',
                    data=u'<?xml version="1.0" encoding="Shift_JIS"><TICKET></TICKET>',
                    issued_at=None
                    ),
                ],
            customer_name_input=False,
            customer_phone_input=False,
            created_at=datetime(2015, 5, 20, 12, 34, 56)
            )
        self.session.add(famiport_order_cash_on_delivery)

        self.session.commit()

        canceled_payment_receipt_errors = ValidateUtils.validate_reprint_cond(canceled_payment_receipt, datetime.now())
        canceled_ticketing_receipt_errors = ValidateUtils.validate_reprint_cond(canceled_ticketing_receipt, datetime.now())
        canceled_cash_on_delivery_receipt_errors = ValidateUtils.validate_reprint_cond(canceled_cash_on_delivery_receipt, datetime.now())

        self.assertTrue(canceled_payment_receipt_errors, msg='Canceled payment receipt should not be reprintable.')
        self.assertTrue(canceled_ticketing_receipt_errors, msg='Canceled ticketing receipt should not be reprintable.')
        self.assertTrue(canceled_cash_on_delivery_receipt_errors, msg='Canceled cache on delivery receipt should not be reprintable.')

    def test_voided_receipt(self):
        voided_payment_receipt = FamiPortReceipt(
                    type=FamiPortReceiptType.Payment.value,
                    famiport_order_identifier=u'RT0000000000',
                    barcode_no=u'01234012340123',
                    shop_code=u'00000',
                    reserve_number=u'4321043210430',
                    payment_request_received_at=datetime.now() -  timedelta(days=1),
                    void_at=datetime.now() - timedelta(minutes=10)
                )

        voided_ticketing_receipt = FamiPortReceipt(
                    type=FamiPortReceiptType.Ticketing.value,
                    famiport_order_identifier=u'RT0000000001',
                    barcode_no=u'01234012340124',
                    shop_code=u'00000',
                    reserve_number=u'4321043210431',
                    payment_request_received_at=datetime.now() -  timedelta(days=1),
                    void_at=datetime.now() - timedelta(minutes=10)
                )

        famiport_playguide = FamiPortPlayguide(
            discrimination_code=5
            )
        famiport_client = FamiPortClient(
            playguide=famiport_playguide,
            code=u'012340123401234012340123',
            name=u'チケットスター',
            prefix=u'TTT'
            )
        famiport_genre_1 = FamiPortGenre1(
            code=1,
            name=u'大ジャンル'
            )
        famiport_genre_2 = FamiPortGenre2(
            genre_1=famiport_genre_1,
            code=2,
            name=u'小ジャンル'
            )
        famiport_venue = FamiPortVenue(
            client_code=u'012340123401234012340123',
            name=u'博品館劇場',
            name_kana=u'ハクヒンカンゲキジョウ',
            prefecture=FamiPortPrefecture.Tokyo.id
            )
        famiport_event = FamiPortEvent(
            client=famiport_client,
            venue=famiport_venue,
            genre_1=famiport_genre_1,
            genre_2=famiport_genre_2,
            sales_channel=FamiPortSalesChannel.FamiPortAndWeb.value,
            code_1=u'000000',
            code_2=u'1111',
            name_1=u'テスト公演',
            name_2=u'テスト公演副題',
            start_at=datetime(2015, 7, 1, 19, 0, 0),
            end_at=datetime(2015, 7, 10, 23, 59, 59),
            keywords=[u'チケットスター', u'博品館', u'イベント'],
            purchasable_prefectures=[u'%02d' % FamiPortPrefecture.Nationwide.id],
            )
        famiport_performance = FamiPortPerformance(
            famiport_event=famiport_event,
            code=u'001',
            name=u'7/1公演',
            type=FamiPortPerformanceType.Normal.value,
            searchable=False,
            sales_channel=FamiPortSalesChannel.FamiPortAndWeb.value,
            start_at=datetime(2015, 7, 1, 19, 0, 0),
            ticket_name=u''
            )
        famiport_sales_segment = FamiPortSalesSegment(
            famiport_performance=famiport_performance,
            code=u'001',
            name=u'一般販売',
            sales_channel=FamiPortSalesChannel.FamiPortAndWeb.value,
            published_at=datetime(2015, 4, 15, 0, 0, 0),
            start_at=datetime(2015, 5, 1, 23, 59, 59),
            end_at=datetime(2015, 5, 31, 23, 59, 59),
            auth_required=False,
            auth_message=u'',
            seat_selection_start_at=datetime(2015, 5, 10, 10, 0, 0)
            )

        famiport_order_payment = FamiPortOrder(
            type=FamiPortOrderType.Payment.value,
            order_no=u'RT0000000001',
            famiport_order_identifier=u'RT0000000010',
            famiport_sales_segment=famiport_sales_segment,
            famiport_client=famiport_client,
            generation=0,
            invalidated_at=None,
            total_amount=10540,
            ticket_payment=10000,
            ticketing_fee=216,
            system_fee=324,
            paid_at=None,
            issued_at=None,
            canceled_at=None,
            ticketing_start_at=datetime.now() - timedelta(days=1),
            ticketing_end_at=datetime.now() + timedelta(days=5),
            payment_start_at=datetime.now() - timedelta(days=1),
            payment_due_at=datetime.now() + timedelta(days=5),
            customer_name=u'チケット　太郎',
            customer_address_1=u'東京都品川区西五反田7-1-9',
            customer_address_2=u'五反田HSビル9F',
            customer_phone_number=u'0301234567',
            famiport_receipts=[voided_payment_receipt, voided_ticketing_receipt],
            famiport_tickets=[
                FamiPortTicket(
                    type=FamiPortTicketType.TicketWithBarcode.value,
                    barcode_number=u'0000000000001',
                    template_code=u'TTTS000001',
                    data=u'<?xml version="1.0" encoding="Shift_JIS"><TICKET></TICKET>',
                    issued_at=None
                    ),
                FamiPortTicket(
                    type=FamiPortTicketType.TicketWithBarcode.value,
                    barcode_number=u'0000000000002',
                    template_code=u'TTTS000001',
                    data=u'<?xml version="1.0" encoding="Shift_JIS"><TICKET></TICKET>',
                    issued_at=None
                    )
                ],
            customer_name_input=False,
            customer_phone_input=False,
            created_at=datetime.now()
            )

        self.session.add(famiport_order_payment)

        voided_cash_on_delivery_receipt = FamiPortReceipt(
                    type=FamiPortReceiptType.CashOnDelivery.value,
                    famiport_order_identifier=u'RT0000000003',
                    barcode_no=u'01234012340125',
                    shop_code=u'00009',
                    reserve_number=u'4321043210432',
                    payment_request_received_at=datetime.now() -  timedelta(days=1),
                    void_at=datetime.now() - timedelta(minutes=10)
                )

        famiport_order_cash_on_delivery = FamiPortOrder(
            type=FamiPortOrderType.CashOnDelivery.value,
            order_no=u'RT0000000002',
            famiport_order_identifier=u'RT0000000012',
            famiport_sales_segment=famiport_sales_segment,
            famiport_client=famiport_client,
            generation=0,
            invalidated_at=None,
            total_amount=10540,
            ticket_payment=10000,
            ticketing_fee=216,
            system_fee=324,
            paid_at=None,
            issued_at=None,
            canceled_at=None,
            ticketing_start_at=datetime(2015, 5, 20, 12, 34, 56),
            ticketing_end_at=datetime(2015, 5, 23, 23, 59, 59),
            payment_start_at=datetime(2015, 5, 20, 12, 34, 56),
            payment_due_at=datetime(2015, 5, 23, 23, 59, 59),
            customer_name=u'チケット　太郎',
            customer_address_1=u'東京都品川区西五反田7-1-9',
            customer_address_2=u'五反田HSビル9F',
            customer_phone_number=u'0301234567',
            famiport_receipts=[voided_cash_on_delivery_receipt],
            famiport_tickets=[
                FamiPortTicket(
                    type=FamiPortTicketType.TicketWithBarcode.value,
                    barcode_number=u'0000000000003',
                    template_code=u'TTTS000003',
                    data=u'<?xml version="1.0" encoding="Shift_JIS"><TICKET></TICKET>',
                    issued_at=None
                    ),
                ],
            customer_name_input=False,
            customer_phone_input=False,
            created_at=datetime(2015, 5, 20, 12, 34, 56)
            )

        self.session.add(famiport_order_cash_on_delivery)

        self.session.commit()

        voided_payment_receipt_errors = ValidateUtils.validate_reprint_cond(voided_payment_receipt, datetime.now())
        voided_ticketing_receipt_errors = ValidateUtils.validate_reprint_cond(voided_ticketing_receipt, datetime.now())
        voided_cash_on_delivery_receipt_errors = ValidateUtils.validate_reprint_cond(voided_cash_on_delivery_receipt, datetime.now())

        self.assertTrue(voided_payment_receipt_errors, msg='Canceled payment receipt should not be reprintable.')
        self.assertTrue(voided_ticketing_receipt_errors, msg='Canceled ticketing receipt should not be reprintable.')
        self.assertTrue(voided_cash_on_delivery_receipt_errors, msg='Canceled cache on delivery receipt should not be reprintable.')

    def test_unpaid_receipt(self):
        unpaid_payment_receipt = FamiPortReceipt(
                    type=FamiPortReceiptType.Payment.value,
                    famiport_order_identifier=u'RT0000000000',
                    barcode_no=u'01234012340123',
                    shop_code=u'00000',
                    reserve_number=u'4321043210430'
                )

        unissued_ticketing_receipt = FamiPortReceipt(
                    type=FamiPortReceiptType.Ticketing.value,
                    famiport_order_identifier=u'RT0000000001',
                    barcode_no=u'01234012340124',
                    shop_code=u'00000',
                    reserve_number=u'4321043210431',
                )

        famiport_playguide = FamiPortPlayguide(
            discrimination_code=5
            )
        famiport_client = FamiPortClient(
            playguide=famiport_playguide,
            code=u'012340123401234012340123',
            name=u'チケットスター',
            prefix=u'TTT'
            )
        famiport_genre_1 = FamiPortGenre1(
            code=1,
            name=u'大ジャンル'
            )
        famiport_genre_2 = FamiPortGenre2(
            genre_1=famiport_genre_1,
            code=2,
            name=u'小ジャンル'
            )
        famiport_venue = FamiPortVenue(
            client_code=u'012340123401234012340123',
            name=u'博品館劇場',
            name_kana=u'ハクヒンカンゲキジョウ',
            prefecture=FamiPortPrefecture.Tokyo.id
            )
        famiport_event = FamiPortEvent(
            client=famiport_client,
            venue=famiport_venue,
            genre_1=famiport_genre_1,
            genre_2=famiport_genre_2,
            sales_channel=FamiPortSalesChannel.FamiPortAndWeb.value,
            code_1=u'000000',
            code_2=u'1111',
            name_1=u'テスト公演',
            name_2=u'テスト公演副題',
            start_at=datetime(2015, 7, 1, 19, 0, 0),
            end_at=datetime(2015, 7, 10, 23, 59, 59),
            keywords=[u'チケットスター', u'博品館', u'イベント'],
            purchasable_prefectures=[u'%02d' % FamiPortPrefecture.Nationwide.id],
            )
        famiport_performance = FamiPortPerformance(
            famiport_event=famiport_event,
            code=u'001',
            name=u'7/1公演',
            type=FamiPortPerformanceType.Normal.value,
            searchable=False,
            sales_channel=FamiPortSalesChannel.FamiPortAndWeb.value,
            start_at=datetime(2015, 7, 1, 19, 0, 0),
            ticket_name=u''
            )
        famiport_sales_segment = FamiPortSalesSegment(
            famiport_performance=famiport_performance,
            code=u'001',
            name=u'一般販売',
            sales_channel=FamiPortSalesChannel.FamiPortAndWeb.value,
            published_at=datetime(2015, 4, 15, 0, 0, 0),
            start_at=datetime(2015, 5, 1, 23, 59, 59),
            end_at=datetime(2015, 5, 31, 23, 59, 59),
            auth_required=False,
            auth_message=u'',
            seat_selection_start_at=datetime(2015, 5, 10, 10, 0, 0)
            )

        famiport_order_payment = FamiPortOrder(
            type=FamiPortOrderType.Payment.value,
            order_no=u'RT0000000001',
            famiport_order_identifier=u'RT0000000010',
            famiport_sales_segment=famiport_sales_segment,
            famiport_client=famiport_client,
            generation=0,
            invalidated_at=None,
            total_amount=10540,
            ticket_payment=10000,
            ticketing_fee=216,
            system_fee=324,
            paid_at=None,
            issued_at=None,
            canceled_at=None,
            ticketing_start_at=datetime.now() - timedelta(days=1),
            ticketing_end_at=datetime.now() + timedelta(days=5),
            payment_start_at=datetime.now() - timedelta(days=1),
            payment_due_at=datetime.now() + timedelta(days=5),
            customer_name=u'チケット　太郎',
            customer_address_1=u'東京都品川区西五反田7-1-9',
            customer_address_2=u'五反田HSビル9F',
            customer_phone_number=u'0301234567',
            famiport_receipts=[unpaid_payment_receipt, unissued_ticketing_receipt],
            famiport_tickets=[
                FamiPortTicket(
                    type=FamiPortTicketType.TicketWithBarcode.value,
                    barcode_number=u'0000000000001',
                    template_code=u'TTTS000001',
                    data=u'<?xml version="1.0" encoding="Shift_JIS"><TICKET></TICKET>',
                    issued_at=None
                    ),
                FamiPortTicket(
                    type=FamiPortTicketType.TicketWithBarcode.value,
                    barcode_number=u'0000000000002',
                    template_code=u'TTTS000001',
                    data=u'<?xml version="1.0" encoding="Shift_JIS"><TICKET></TICKET>',
                    issued_at=None
                    )
                ],
            customer_name_input=False,
            customer_phone_input=False,
            created_at=datetime.now()
            )

        self.session.add(famiport_order_payment)

        unpaid_cash_on_delivery_receipt = FamiPortReceipt(
                    type=FamiPortReceiptType.CashOnDelivery.value,
                    famiport_order_identifier=u'RT0000000002',
                    barcode_no=u'01234012340125',
                    shop_code=u'00009',
                    reserve_number=u'4321043210432',
                )

        famiport_order_cash_on_delivery = FamiPortOrder(
            type=FamiPortOrderType.CashOnDelivery.value,
            order_no=u'RT0000000002',
            famiport_order_identifier=u'RT0000000012',
            famiport_sales_segment=famiport_sales_segment,
            famiport_client=famiport_client,
            generation=0,
            invalidated_at=None,
            total_amount=10540,
            ticket_payment=10000,
            ticketing_fee=216,
            system_fee=324,
            paid_at=None,
            issued_at=None,
            canceled_at=None,
            ticketing_start_at=datetime(2015, 5, 20, 12, 34, 56),
            ticketing_end_at=datetime(2015, 5, 23, 23, 59, 59),
            payment_start_at=datetime(2015, 5, 20, 12, 34, 56),
            payment_due_at=datetime(2015, 5, 23, 23, 59, 59),
            customer_name=u'チケット　太郎',
            customer_address_1=u'東京都品川区西五反田7-1-9',
            customer_address_2=u'五反田HSビル9F',
            customer_phone_number=u'0301234567',
            famiport_receipts=[unpaid_cash_on_delivery_receipt],
            famiport_tickets=[
                FamiPortTicket(
                    type=FamiPortTicketType.TicketWithBarcode.value,
                    barcode_number=u'0000000000003',
                    template_code=u'TTTS000003',
                    data=u'<?xml version="1.0" encoding="Shift_JIS"><TICKET></TICKET>',
                    issued_at=None
                    ),
                ],
            customer_name_input=False,
            customer_phone_input=False,
            created_at=datetime(2015, 5, 20, 12, 34, 56)
            )

        self.session.add(famiport_order_cash_on_delivery)
        self.session.commit()

        unpaid_payment_receipt_errors = ValidateUtils.validate_reprint_cond(unpaid_payment_receipt, datetime.now())
        unissued_ticketing_receipt_errors = ValidateUtils.validate_reprint_cond(unissued_ticketing_receipt, datetime.now())
        unpaid_cash_on_delivery_receipt_errors = ValidateUtils.validate_reprint_cond(unpaid_cash_on_delivery_receipt, datetime.now())

        self.assertTrue(unpaid_payment_receipt_errors, msg='Unpaid payment receipt should not be reprintable.')
        self.assertTrue(unissued_ticketing_receipt_errors, msg='Unissued ticketing receipt should not be reprintable.')
        self.assertTrue(unpaid_cash_on_delivery_receipt_errors, msg='Unpaid cache on delivery receipt should not be reprintable.')

    def test_incomplete_receipt(self):
        incomplete_payment_receipt = FamiPortReceipt(
                    type=FamiPortReceiptType.Payment.value,
                    famiport_order_identifier=u'RT0000000000',
                    barcode_no=u'01234012340123',
                    shop_code=u'00000',
                    reserve_number=u'4321043210430',
                    payment_request_received_at=datetime.now() -  timedelta(minutes=1)
                )

        incomplete_ticketing_receipt = FamiPortReceipt(
                    type=FamiPortReceiptType.Ticketing.value,
                    famiport_order_identifier=u'RT0000000001',
                    barcode_no=u'01234012340124',
                    shop_code=u'00000',
                    reserve_number=u'4321043210431',
                    payment_request_received_at=datetime.now() -  timedelta(minutes=1)
                )

        famiport_playguide = FamiPortPlayguide(
            discrimination_code=5
            )
        famiport_client = FamiPortClient(
            playguide=famiport_playguide,
            code=u'012340123401234012340123',
            name=u'チケットスター',
            prefix=u'TTT'
            )
        famiport_genre_1 = FamiPortGenre1(
            code=1,
            name=u'大ジャンル'
            )
        famiport_genre_2 = FamiPortGenre2(
            genre_1=famiport_genre_1,
            code=2,
            name=u'小ジャンル'
            )
        famiport_venue = FamiPortVenue(
            client_code=u'012340123401234012340123',
            name=u'博品館劇場',
            name_kana=u'ハクヒンカンゲキジョウ',
            prefecture=FamiPortPrefecture.Tokyo.id
            )
        famiport_event = FamiPortEvent(
            client=famiport_client,
            venue=famiport_venue,
            genre_1=famiport_genre_1,
            genre_2=famiport_genre_2,
            sales_channel=FamiPortSalesChannel.FamiPortAndWeb.value,
            code_1=u'000000',
            code_2=u'1111',
            name_1=u'テスト公演',
            name_2=u'テスト公演副題',
            start_at=datetime(2015, 7, 1, 19, 0, 0),
            end_at=datetime(2015, 7, 10, 23, 59, 59),
            keywords=[u'チケットスター', u'博品館', u'イベント'],
            purchasable_prefectures=[u'%02d' % FamiPortPrefecture.Nationwide.id],
            )
        famiport_performance = FamiPortPerformance(
            famiport_event=famiport_event,
            code=u'001',
            name=u'7/1公演',
            type=FamiPortPerformanceType.Normal.value,
            searchable=False,
            sales_channel=FamiPortSalesChannel.FamiPortAndWeb.value,
            start_at=datetime(2015, 7, 1, 19, 0, 0),
            ticket_name=u''
            )
        famiport_sales_segment = FamiPortSalesSegment(
            famiport_performance=famiport_performance,
            code=u'001',
            name=u'一般販売',
            sales_channel=FamiPortSalesChannel.FamiPortAndWeb.value,
            published_at=datetime(2015, 4, 15, 0, 0, 0),
            start_at=datetime(2015, 5, 1, 23, 59, 59),
            end_at=datetime(2015, 5, 31, 23, 59, 59),
            auth_required=False,
            auth_message=u'',
            seat_selection_start_at=datetime(2015, 5, 10, 10, 0, 0)
            )

        famiport_order_payment = FamiPortOrder(
            type=FamiPortOrderType.Payment.value,
            order_no=u'RT0000000001',
            famiport_order_identifier=u'RT0000000010',
            famiport_sales_segment=famiport_sales_segment,
            famiport_client=famiport_client,
            generation=0,
            invalidated_at=None,
            total_amount=10540,
            ticket_payment=10000,
            ticketing_fee=216,
            system_fee=324,
            paid_at=None,
            issued_at=None,
            canceled_at=None,
            ticketing_start_at=datetime.now() - timedelta(days=1),
            ticketing_end_at=datetime.now() + timedelta(days=5),
            payment_start_at=datetime.now() - timedelta(days=1),
            payment_due_at=datetime.now() + timedelta(days=5),
            customer_name=u'チケット　太郎',
            customer_address_1=u'東京都品川区西五反田7-1-9',
            customer_address_2=u'五反田HSビル9F',
            customer_phone_number=u'0301234567',
            famiport_receipts=[incomplete_payment_receipt, incomplete_ticketing_receipt],
            famiport_tickets=[
                FamiPortTicket(
                    type=FamiPortTicketType.TicketWithBarcode.value,
                    barcode_number=u'0000000000001',
                    template_code=u'TTTS000001',
                    data=u'<?xml version="1.0" encoding="Shift_JIS"><TICKET></TICKET>',
                    issued_at=None
                    ),
                FamiPortTicket(
                    type=FamiPortTicketType.TicketWithBarcode.value,
                    barcode_number=u'0000000000002',
                    template_code=u'TTTS000001',
                    data=u'<?xml version="1.0" encoding="Shift_JIS"><TICKET></TICKET>',
                    issued_at=None
                    )
                ],
            customer_name_input=False,
            customer_phone_input=False,
            created_at=datetime.now()
            )

        self.session.add(famiport_order_payment)

        incomplete_cash_on_delivery_receipt = FamiPortReceipt(
                    type=FamiPortReceiptType.CashOnDelivery.value,
                    famiport_order_identifier=u'RT0000000002',
                    barcode_no=u'01234012340125',
                    shop_code=u'00009',
                    reserve_number=u'4321043210432',
                    payment_request_received_at=datetime.now() -  timedelta(minutes=1)
                )

        famiport_order_cash_on_delivery = FamiPortOrder(
            type=FamiPortOrderType.CashOnDelivery.value,
            order_no=u'RT0000000002',
            famiport_order_identifier=u'RT0000000012',
            famiport_sales_segment=famiport_sales_segment,
            famiport_client=famiport_client,
            generation=0,
            invalidated_at=None,
            total_amount=10540,
            ticket_payment=10000,
            ticketing_fee=216,
            system_fee=324,
            paid_at=None,
            issued_at=None,
            canceled_at=None,
            ticketing_start_at=datetime.now() - timedelta(days=1),
            ticketing_end_at=datetime.now() + timedelta(days=5),
            payment_start_at=datetime.now() - timedelta(days=1),
            payment_due_at=datetime.now() + timedelta(days=5),
            customer_name=u'チケット　太郎',
            customer_address_1=u'東京都品川区西五反田7-1-9',
            customer_address_2=u'五反田HSビル9F',
            customer_phone_number=u'0301234567',
            famiport_receipts=[incomplete_cash_on_delivery_receipt],
            famiport_tickets=[
                FamiPortTicket(
                    type=FamiPortTicketType.TicketWithBarcode.value,
                    barcode_number=u'0000000000003',
                    template_code=u'TTTS000003',
                    data=u'<?xml version="1.0" encoding="Shift_JIS"><TICKET></TICKET>',
                    issued_at=None
                    ),
                ],
            customer_name_input=False,
            customer_phone_input=False,
            created_at=datetime(2015, 5, 20, 12, 34, 56)
            )

        self.session.add(famiport_order_cash_on_delivery)
        self.session.commit()

        incomplete_payment_receipt_errors = ValidateUtils.validate_reprint_cond(incomplete_payment_receipt, datetime.now())
        incomplete_ticketing_receipt_errors = ValidateUtils.validate_reprint_cond(incomplete_ticketing_receipt, datetime.now())
        incomplete_cash_on_delivery_receipt_errors = ValidateUtils.validate_reprint_cond(incomplete_cash_on_delivery_receipt, datetime.now())

        self.assertTrue(incomplete_payment_receipt_errors, msg='Incomplete payment receipt should not be reprintable.')
        self.assertFalse(incomplete_ticketing_receipt_errors, msg='Incomplete ticketing receipt should be reprintable.')
        self.assertFalse(incomplete_cash_on_delivery_receipt_errors, msg='Incomplete cash on delivery receipt should be reprintable.')

    def test_complete_receipt(self):
        complete_payment_receipt = FamiPortReceipt(
                    type=FamiPortReceiptType.Payment.value,
                    famiport_order_identifier=u'RT0000000000',
                    barcode_no=u'01234012340123',
                    shop_code=u'00000',
                    reserve_number=u'4321043210430',
                    payment_request_received_at=datetime.now() -  timedelta(minutes=1)
                )

        complete_ticketing_receipt = FamiPortReceipt(
                    type=FamiPortReceiptType.Ticketing.value,
                    famiport_order_identifier=u'RT0000000001',
                    barcode_no=u'01234012340124',
                    shop_code=u'00000',
                    reserve_number=u'4321043210431',
                    payment_request_received_at=datetime.now() -  timedelta(minutes=1)
                )

        famiport_playguide = FamiPortPlayguide(
            discrimination_code=5
            )
        famiport_client = FamiPortClient(
            playguide=famiport_playguide,
            code=u'012340123401234012340123',
            name=u'チケットスター',
            prefix=u'TTT'
            )
        famiport_genre_1 = FamiPortGenre1(
            code=1,
            name=u'大ジャンル'
            )
        famiport_genre_2 = FamiPortGenre2(
            genre_1=famiport_genre_1,
            code=2,
            name=u'小ジャンル'
            )
        famiport_venue = FamiPortVenue(
            client_code=u'012340123401234012340123',
            name=u'博品館劇場',
            name_kana=u'ハクヒンカンゲキジョウ',
            prefecture=FamiPortPrefecture.Tokyo.id
            )
        famiport_event = FamiPortEvent(
            client=famiport_client,
            venue=famiport_venue,
            genre_1=famiport_genre_1,
            genre_2=famiport_genre_2,
            sales_channel=FamiPortSalesChannel.FamiPortAndWeb.value,
            code_1=u'000000',
            code_2=u'1111',
            name_1=u'テスト公演',
            name_2=u'テスト公演副題',
            start_at=datetime(2015, 7, 1, 19, 0, 0),
            end_at=datetime(2015, 7, 10, 23, 59, 59),
            keywords=[u'チケットスター', u'博品館', u'イベント'],
            purchasable_prefectures=[u'%02d' % FamiPortPrefecture.Nationwide.id],
            )
        famiport_performance = FamiPortPerformance(
            famiport_event=famiport_event,
            code=u'001',
            name=u'7/1公演',
            type=FamiPortPerformanceType.Normal.value,
            searchable=False,
            sales_channel=FamiPortSalesChannel.FamiPortAndWeb.value,
            start_at=datetime(2015, 7, 1, 19, 0, 0),
            ticket_name=u''
            )
        famiport_sales_segment = FamiPortSalesSegment(
            famiport_performance=famiport_performance,
            code=u'001',
            name=u'一般販売',
            sales_channel=FamiPortSalesChannel.FamiPortAndWeb.value,
            published_at=datetime(2015, 4, 15, 0, 0, 0),
            start_at=datetime(2015, 5, 1, 23, 59, 59),
            end_at=datetime(2015, 5, 31, 23, 59, 59),
            auth_required=False,
            auth_message=u'',
            seat_selection_start_at=datetime(2015, 5, 10, 10, 0, 0)
            )

        famiport_order_payment = FamiPortOrder(
            type=FamiPortOrderType.Payment.value,
            order_no=u'RT0000000001',
            famiport_order_identifier=u'RT0000000010',
            famiport_sales_segment=famiport_sales_segment,
            famiport_client=famiport_client,
            generation=0,
            invalidated_at=None,
            total_amount=10540,
            ticket_payment=10000,
            ticketing_fee=216,
            system_fee=324,
            paid_at=None,
            issued_at=None,
            canceled_at=None,
            ticketing_start_at=datetime.now() - timedelta(days=1),
            ticketing_end_at=datetime.now() + timedelta(days=5),
            payment_start_at=datetime.now() - timedelta(days=1),
            payment_due_at=datetime.now() + timedelta(days=5),
            customer_name=u'チケット　太郎',
            customer_address_1=u'東京都品川区西五反田7-1-9',
            customer_address_2=u'五反田HSビル9F',
            customer_phone_number=u'0301234567',
            famiport_receipts=[complete_payment_receipt, complete_ticketing_receipt],
            famiport_tickets=[
                FamiPortTicket(
                    type=FamiPortTicketType.TicketWithBarcode.value,
                    barcode_number=u'0000000000001',
                    template_code=u'TTTS000001',
                    data=u'<?xml version="1.0" encoding="Shift_JIS"><TICKET></TICKET>',
                    issued_at=None
                    ),
                FamiPortTicket(
                    type=FamiPortTicketType.TicketWithBarcode.value,
                    barcode_number=u'0000000000002',
                    template_code=u'TTTS000001',
                    data=u'<?xml version="1.0" encoding="Shift_JIS"><TICKET></TICKET>',
                    issued_at=None
                    )
                ],
            customer_name_input=False,
            customer_phone_input=False,
            created_at=datetime.now()
            )

        self.session.add(famiport_order_payment)

        complete_cash_on_delivery_receipt = FamiPortReceipt(
                    type=FamiPortReceiptType.CashOnDelivery.value,
                    famiport_order_identifier=u'RT0000000002',
                    barcode_no=u'01234012340125',
                    shop_code=u'00009',
                    reserve_number=u'4321043210432',
                    payment_request_received_at=datetime.now() -  timedelta(minutes=1)
                )

        famiport_order_cash_on_delivery = FamiPortOrder(
            type=FamiPortOrderType.CashOnDelivery.value,
            order_no=u'RT0000000002',
            famiport_order_identifier=u'RT0000000012',
            famiport_sales_segment=famiport_sales_segment,
            famiport_client=famiport_client,
            generation=0,
            invalidated_at=None,
            total_amount=10540,
            ticket_payment=10000,
            ticketing_fee=216,
            system_fee=324,
            paid_at=None,
            issued_at=None,
            canceled_at=None,
            ticketing_start_at=datetime.now() - timedelta(days=1),
            ticketing_end_at=datetime.now() + timedelta(days=5),
            payment_start_at=datetime.now() - timedelta(days=1),
            payment_due_at=datetime.now() + timedelta(days=5),
            customer_name=u'チケット　太郎',
            customer_address_1=u'東京都品川区西五反田7-1-9',
            customer_address_2=u'五反田HSビル9F',
            customer_phone_number=u'0301234567',
            famiport_receipts=[complete_cash_on_delivery_receipt],
            famiport_tickets=[
                FamiPortTicket(
                    type=FamiPortTicketType.TicketWithBarcode.value,
                    barcode_number=u'0000000000003',
                    template_code=u'TTTS000003',
                    data=u'<?xml version="1.0" encoding="Shift_JIS"><TICKET></TICKET>',
                    issued_at=None
                    ),
                ],
            customer_name_input=False,
            customer_phone_input=False,
            created_at=datetime(2015, 5, 20, 12, 34, 56)
            )

        self.session.add(famiport_order_cash_on_delivery)
        self.session.commit()

        complete_payment_receipt_errors = ValidateUtils.validate_reprint_cond(complete_payment_receipt, datetime.now())
        complete_ticketing_receipt_errors = ValidateUtils.validate_reprint_cond(complete_ticketing_receipt, datetime.now())
        complete_cash_on_delivery_receipt_errors = ValidateUtils.validate_reprint_cond(complete_cash_on_delivery_receipt, datetime.now())

        self.assertTrue(complete_payment_receipt_errors, msg='Complete payment receipt should be reprintable.')
        self.assertFalse(complete_ticketing_receipt_errors, msg='Complete ticketing receipt should be reprintable.')
        self.assertFalse(complete_cash_on_delivery_receipt_errors, msg='Complete cash on delivery receipt should be reprintable.')