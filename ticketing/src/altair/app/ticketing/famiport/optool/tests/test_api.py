# -*- coding:utf-8 -*-
from datetime import datetime, date, timedelta
from decimal import Decimal
from unittest import TestCase
from pyramid.testing import DummyRequest, setUp, tearDown
from altair.sqlahelper import get_global_db_session
from altair.app.ticketing.famiport.testing import _setup_db, _teardown_db
from ..helpers import RefundTicketSearchHelper
from ..api import (
    create_user,
    lookup_user_by_credentials,
    lookup_receipt_by_searchform_data,
    search_refund_ticket_by
    )

class APITestBase(object):
    def setUp(self):
        self.request = DummyRequest()
        self.config = setUp(request=self.request)
        # self.config.include('.')
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

class UserCreationTest(APITestBase, TestCase):
    def test_create_user(self):
        user_name = 'famiport_test'
        password = 'famiport'
        role = 'test'
        create_user(self.request, user_name, password, role)
        user = lookup_user_by_credentials(self.request, user_name, password)
        self.assertIsNotNone(user)



class ReceiptSearchTest(APITestBase, TestCase):

    barcode_no_cash_on_delivery = u'01234012340123'
    barcode_no_payment = u'01234012340124'
    barcode_no_payment_only = u'01234012340126'

    def setUp(self):
        APITestBase.setUp(self)
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
            FamiPortShop,
            )

        self.barcode_nos = (self.barcode_no_cash_on_delivery, self.barcode_no_payment, self.barcode_no_payment_only)
        self.exchange_numbers = ('4321043210432', '4321043210433', '4321043210434', '4321043210435')
        self.management_numbers = ('000011112222', '000011112223', '000011112224', '000011112225', '000011112226', '000011112227', '000011112228')
        self.barcode_numbers = ('0000000000001', '0000000000002', '0000000000003', '0000000000004', '0000000000005', '0000000000006')
        self.customer_phone_numbers = ('0301234567', '0312345678', '0323456789')
        self.shop_codes = ('00001', '00002', '00003', '00004')
        self.shop_names = (u'西五反田', u'下目黒', u'代々木', u'玉川')
        self.sales_from = datetime(2015, 4, 1, 10, 0, 0)

        self.famiport_shop1 = FamiPortShop(
            code=self.shop_codes[0],
            company_code=u'0001',
            company_name=u'東京ファミリーマート',
            district_code=u'01',
            district_name=u'五反田',
            district_valid_from=date(2015, 6, 1),
            branch_code=u'0001',
            branch_name=u'五反田',
            branch_valid_from=date(2015, 6, 1),
            name=self.shop_names[0],
            name_kana=u'ニシゴタンダ',
            tel=u'060012345678',
            prefecture=1,
            prefecture_name=u'東京都',
            address=u'東京都品川区西五反田',
            open_from=date(2015, 6, 1),
            zip=u'1410000',
            business_run_from=date(2015, 6, 1),
            )
        self.famiport_shop2 = FamiPortShop(
            code=self.shop_codes[1],
            company_code=u'0001',
            company_name=u'東京ファミリーマート',
            district_code=u'02',
            district_name=u'目黒',
            district_valid_from=date(2015, 5, 1),
            branch_code=u'0002',
            branch_name=u'目黒',
            branch_valid_from=date(2015, 5, 1),
            name=self.shop_names[1],
            name_kana=u'シモメグロ',
            tel=u'07012345678',
            prefecture=1,
            prefecture_name=u'東京都',
            address=u'東京都目黒区下目黒',
            open_from=date(2015, 5, 1),
            zip=u'1530064',
            business_run_from=date(2015, 5, 1),
            )
        self.famiport_shop3 = FamiPortShop(
            code=self.shop_codes[2],
            company_code=u'0001',
            company_name=u'東京ファミリーマート',
            district_code=u'03',
            district_name=u'渋谷',
            district_valid_from=date(2015, 4, 1),
            branch_code=u'0003',
            branch_name=u'渋谷',
            branch_valid_from=date(2015, 4, 1),
            name=self.shop_names[2],
            name_kana=u'ヨヨギ',
            tel=u'08001234567',
            prefecture=1,
            prefecture_name=u'東京都',
            address=u'東京都渋谷区代々木',
            open_from=date(2015, 4, 1),
            zip=u'1510053',
            business_run_from=date(2015, 4, 1),
            )
        self.famiport_shop4 = FamiPortShop(
            code=self.shop_codes[3],
            company_code=u'0001',
            company_name=u'東京ファミリーマート',
            district_code=u'04',
            district_name=u'世田谷',
            district_valid_from=date(2015, 3, 1),
            branch_code=u'0004',
            branch_name=u'世田谷',
            branch_valid_from=date(2015, 3, 1),
            name=self.shop_names[3],
            name_kana=u'タマガワ',
            tel=u'09001234567',
            prefecture=1,
            prefecture_name=u'東京都',
            address=u'東京都世田谷区玉川',
            open_from=date(2015, 3, 1),
            zip=u'1580094',
            business_run_from=date(2015, 3, 1),
            )
        self.session.add(self.famiport_shop1)
        self.session.add(self.famiport_shop2)
        self.session.add(self.famiport_shop3)
        self.session.add(self.famiport_shop4)
        self.famiport_playguide = FamiPortPlayguide(
            discrimination_code=u'5'
            )
        self.famiport_client = FamiPortClient(
            playguide=self.famiport_playguide,
            code=u'012340123401234012340123',
            name=u'チケットスター',
            prefix=u'TTT'
            )
        self.famiport_genre_1 = FamiPortGenre1(
            code=1,
            name=u'大ジャンル'
            )
        self.famiport_genre_2 = FamiPortGenre2(
            genre_1=self.famiport_genre_1,
            code=2,
            name=u'小ジャンル'
            )
        self.famiport_venue = FamiPortVenue(
            client_code=u'012340123401234012340123',
            name=u'博品館劇場',
            name_kana=u'ハクヒンカンゲキジョウ',
            prefecture=FamiPortPrefecture.Tokyo.id
            )
        self.famiport_event = FamiPortEvent(
            client=self.famiport_client,
            venue=self.famiport_venue,
            genre_1=self.famiport_genre_1,
            genre_2=self.famiport_genre_2,
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
        self.famiport_performance = FamiPortPerformance(
            famiport_event=self.famiport_event,
            code=u'001',
            name=u'7/1公演',
            type=FamiPortPerformanceType.Normal.value,
            searchable=False,
            sales_channel=FamiPortSalesChannel.FamiPortAndWeb.value,
            start_at=datetime(2015, 7, 1, 19, 0, 0),
            ticket_name=u''
            )
        self.famiport_sales_segment = FamiPortSalesSegment(
            famiport_performance=self.famiport_performance,
            code=u'001',
            name=u'一般販売',
            sales_channel=FamiPortSalesChannel.FamiPortAndWeb.value,
            published_at=datetime(2015, 4, 15, 0, 0, 0),
            start_at=self.sales_from,
            end_at=datetime(2015, 5, 31, 23, 59, 59),
            auth_required=False,
            auth_message=u'',
            seat_selection_start_at=datetime(2015, 5, 10, 10, 0, 0)
            )
        self.famiport_order_cash_on_delivery = FamiPortOrder(
            type=FamiPortOrderType.CashOnDelivery.value,
            order_no=u'RT0000000000',
            famiport_order_identifier=self.famiport_client.prefix + self.management_numbers[0],
            famiport_sales_segment=self.famiport_sales_segment,
            famiport_client=self.famiport_client,
            generation=0,
            invalidated_at=None,
            total_amount=Decimal(10540),
            ticket_payment=Decimal(10000),
            ticketing_fee=Decimal(216),
            system_fee=Decimal(324),
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
            customer_phone_number=self.customer_phone_numbers[0],
            famiport_receipts=[
                FamiPortReceipt(
                    type=FamiPortReceiptType.CashOnDelivery.value,
                    barcode_no=self.barcode_no_cash_on_delivery,
                    famiport_order_identifier=self.famiport_client.prefix + self.management_numbers[1],
                    shop_code=self.shop_codes[0],
                    reserve_number=u'4321043210432'
                    ),
                ],
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
        self.session.add(self.famiport_order_cash_on_delivery)
        self.famiport_order_payment = FamiPortOrder(
            type=FamiPortOrderType.Payment.value,
            order_no=u'RT0000000001',
            famiport_order_identifier=self.famiport_client.prefix + self.management_numbers[2],
            famiport_sales_segment=self.famiport_sales_segment,
            famiport_client=self.famiport_client,
            generation=0,
            invalidated_at=None,
            total_amount=Decimal(10540),
            ticket_payment=Decimal(10000),
            ticketing_fee=Decimal(216),
            system_fee=Decimal(324),
            paid_at=None,
            issued_at=None,
            canceled_at=None,
            ticketing_start_at=datetime(2015, 5, 22, 00, 00, 00),
            ticketing_end_at=datetime(2015, 5, 23, 23, 59, 59),
            payment_start_at=datetime(2015, 5, 20, 12, 34, 56),
            payment_due_at=datetime(2015, 5, 21, 23, 59, 59),
            customer_name=u'チケット　太郎',
            customer_address_1=u'東京都品川区西五反田7-1-9',
            customer_address_2=u'五反田HSビル9F',
            customer_phone_number=self.customer_phone_numbers[1],
            famiport_receipts=[
                FamiPortReceipt(
                    type=FamiPortReceiptType.Payment.value,
                    barcode_no=self.barcode_no_payment,
                    famiport_order_identifier=self.famiport_client.prefix + self.management_numbers[3],
                    shop_code=self.shop_codes[1],
                    reserve_number=u'4321043210433',
                    ),
                FamiPortReceipt(
                    type=FamiPortReceiptType.Ticketing.value,
                    barcode_no=u'01234012340125',
                    famiport_order_identifier=self.famiport_client.prefix + self.management_numbers[4],
                    shop_code=self.shop_codes[2],
                    reserve_number=u'4321043210434',
                    )
                ],
            famiport_tickets=[
                FamiPortTicket(
                    type=FamiPortTicketType.TicketWithBarcode.value,
                    barcode_number=u'0000000000003',
                    template_code=u'TTTS000001',
                    data=u'<?xml version="1.0" encoding="Shift_JIS"><TICKET></TICKET>',
                    issued_at=None
                    ),
                FamiPortTicket(
                    type=FamiPortTicketType.TicketWithBarcode.value,
                    barcode_number=u'0000000000004',
                    template_code=u'TTTS000001',
                    data=u'<?xml version="1.0" encoding="Shift_JIS"><TICKET></TICKET>',
                    issued_at=None
                    )
                ],
            customer_name_input=False,
            customer_phone_input=False,
            created_at=datetime.now()
            )
        self.session.add(self.famiport_order_payment)
        self.famiport_order_payment_only = FamiPortOrder(
            type=FamiPortOrderType.PaymentOnly.value,
            order_no=u'RT0000000002',
            famiport_order_identifier=self.famiport_client.prefix + self.management_numbers[5],
            famiport_sales_segment=self.famiport_sales_segment,
            famiport_client=self.famiport_client,
            generation=0,
            invalidated_at=None,
            total_amount=Decimal(10540),
            ticket_payment=Decimal(10000),
            ticketing_fee=Decimal(216),
            system_fee=Decimal(324),
            paid_at=None,
            issued_at=None,
            canceled_at=None,
            ticketing_start_at=None,
            ticketing_end_at=None,
            payment_start_at=datetime(2015, 5, 22, 12, 34, 56),
            payment_due_at=datetime(2015, 5, 23, 23, 59, 59),
            customer_name=u'チケット　太郎',
            customer_address_1=u'東京都品川区西五反田7-1-9',
            customer_address_2=u'五反田HSビル9F',
            customer_phone_number=self.customer_phone_numbers[2],
            famiport_receipts=[
                FamiPortReceipt(
                    type=FamiPortReceiptType.Payment.value,
                    famiport_order_identifier=self.famiport_client.prefix + self.management_numbers[6],
                    barcode_no=self.barcode_no_payment_only,
                    shop_code=self.shop_codes[3],
                    reserve_number=u'4321043210435'
                    ),
                ],
            famiport_tickets=[
                FamiPortTicket(
                    type=FamiPortTicketType.TicketWithBarcode.value,
                    barcode_number=u'0000000000005',
                    template_code=u'TTTS000001',
                    data=u'<?xml version="1.0" encoding="Shift_JIS"><TICKET></TICKET>',
                    issued_at=None
                    ),
                FamiPortTicket(
                    type=FamiPortTicketType.TicketWithBarcode.value,
                    barcode_number=u'0000000000006',
                    template_code=u'TTTS000001',
                    data=u'<?xml version="1.0" encoding="Shift_JIS"><TICKET></TICKET>',
                    issued_at=None
                    )
                ],
            customer_name_input=False,
            customer_phone_input=False,
            created_at=datetime.now()
            )
        self.session.add(self.famiport_order_payment_only)
        self.session.commit()

    def test_search_receipt_by_barcode_no(self):
        formdata = {'barcode_no': None, 'exchange_number': None, 'management_number': None, 'barcode_number': None, \
                    'customer_phone_number': None, 'shop_code': None, 'shop_name': None, 'sales_from': None, 'sales_to': None}
        # Search hits
        for barcode_no in self.barcode_nos:
            formdata['barcode_no'] = barcode_no
            receipts = lookup_receipt_by_searchform_data(self.request, formdata)
            self.assertTrue(receipts, msg='Failed to lookup receipt by barcode_no: %s' % barcode_no)
        # Search does not hit
        for barcode_no in ('00000000000000', 'test test test', 'abcdefghijklmn'):
            formdata['barcode_no'] = barcode_no
            receipts = lookup_receipt_by_searchform_data(self.request, formdata)
            self.assertFalse(receipts, msg='Failed to lookup receipt by barcode_no: %s' % barcode_no)


    def test_search_receipt_by_exchange_number(self):
        formdata = {'barcode_no': None, 'exchange_number': None, 'management_number': None, 'barcode_number': None, \
                    'customer_phone_number': None, 'shop_code': None, 'shop_name': None, 'sales_from': None, 'sales_to': None}
        # Search hits
        for exchange_number in self.exchange_numbers:
            formdata['exchange_number'] = exchange_number
            receipts = lookup_receipt_by_searchform_data(self.request, formdata)
            self.assertTrue(receipts, msg='Failed to lookup receipt by exchange_number: %s' % exchange_number)
        # Search does not hit
        for exchange_number in ('0000000000000', 'test test test', 'abcdefghijklmn'):
            formdata['exchange_number'] = exchange_number
            receipts = lookup_receipt_by_searchform_data(self.request, formdata)
            self.assertFalse(receipts, msg='Failed to lookup receipt by exchange_number: %s' % exchange_number)

    def test_search_receipt_by_management_number(self):
        formdata = {'barcode_no': None, 'exchange_number': None, 'management_number': None, 'barcode_number': None, \
                    'customer_phone_number': None, 'shop_code': None, 'shop_name': None, 'sales_from': None, 'sales_to': None}
        # Search hits
        for management_number in self.management_numbers:
            formdata['management_number'] = management_number
            receipts = lookup_receipt_by_searchform_data(self.request, formdata)
            self.assertTrue(receipts, msg='Failed to lookup receipt by management_number: %s' % management_number)
        # Search does not hit
        for management_number in ('000000000', 'test test test', 'abcdefghi'):
            formdata['management_number'] = management_number
            receipts = lookup_receipt_by_searchform_data(self.request, formdata)
            self.assertFalse(receipts, msg='Failed to lookup receipt by management_number: %s' % management_number)

    def test_search_receipt_by_barcode_number(self):
        formdata = {'barcode_no': None, 'exchange_number': None, 'management_number': None, 'barcode_number': None, \
                    'customer_phone_number': None, 'shop_code': None, 'shop_name': None, 'sales_from': None, 'sales_to': None}
        # Search hits
        for barcode_number in self.barcode_numbers:
            formdata['barcode_number'] = barcode_number
            receipts = lookup_receipt_by_searchform_data(self.request, formdata)
            self.assertTrue(receipts, msg='Failed to lookup receipt by barcode_number')
        # Search does not hit
        for barcode_number in ('0000000000000', 'test test test', 'abcdefghijklmn'):
            formdata['barcode_number'] = barcode_number
            receipts = lookup_receipt_by_searchform_data(self.request, formdata)
            self.assertFalse(receipts, msg='Failed to lookup receipt by barcode_number')

    def test_search_receipt_by_customer_phone_number(self):
        formdata = {'barcode_no': None, 'exchange_number': None, 'management_number': None, 'barcode_number': None, \
                    'customer_phone_number': None, 'shop_code': None, 'shop_name': None, 'sales_from': None, 'sales_to': None}
        # Search hits
        for customer_phone_number in self.customer_phone_numbers:
            formdata['customer_phone_number'] = customer_phone_number
            receipts = lookup_receipt_by_searchform_data(self.request, formdata)
            self.assertTrue(receipts, msg='Failed to lookup receipt by customer_phone_number: %s' % customer_phone_number)
        # Search does not hit
        for customer_phone_number in ('1234567', '0300000000', '01234567'):
            formdata['customer_phone_number'] = customer_phone_number
            receipts = lookup_receipt_by_searchform_data(self.request, formdata)
            self.assertFalse(receipts, msg='Failed to lookup receipt by customer_phone_number: %s' % customer_phone_number)

    def test_search_receipt_by_shop_code(self):
        formdata = {'barcode_no': None, 'exchange_number': None, 'management_number': None, 'barcode_number': None, \
                    'customer_phone_number': None, 'shop_code': None, 'shop_name': None, 'sales_from': None, 'sales_to': None}
        # Search hits
        for shop_code in self.shop_codes:
            formdata['shop_code'] = shop_code
            receipts = lookup_receipt_by_searchform_data(self.request, formdata)
            self.assertTrue(receipts, msg='Failed to lookup receipt by shop_code: %s' % shop_code)
        # Search does not hit
        for shop_code in ('00000', '11111', 'abcde'):
            formdata['shop_code'] = shop_code
            receipts = lookup_receipt_by_searchform_data(self.request, formdata)
            self.assertFalse(receipts, msg='Failed to lookup receipt by shop_code: %s' % shop_code)

    def test_search_receipt_by_shop_name(self):
        formdata = {'barcode_no': None, 'exchange_number': None, 'management_number': None, 'barcode_number': None, \
                    'customer_phone_number': None, 'shop_code': None, 'shop_name': None, 'sales_from': None, 'sales_to': None}
        # Search hits
        for shop_name in self.shop_names:
            formdata['shop_name'] = shop_name
            receipts = lookup_receipt_by_searchform_data(self.request, formdata)
            self.assertTrue(receipts, msg='Failed to lookup receipt by shop_name: %s' % shop_name)
        # Search does not hit
        for shop_name in (u'新宿', u'二子玉', u'テスト', 'test'):
            formdata['shop_name'] = shop_name
            receipts = lookup_receipt_by_searchform_data(self.request, formdata)
            self.assertFalse(receipts, msg=u'Failed to lookup receipt by shop_name: %s' % shop_name)

    def test_search_receipt_by_sales_date(self):
        formdata = {'barcode_no': None, 'exchange_number': None, 'management_number': None, 'barcode_number': None, \
                    'customer_phone_number': None, 'shop_code': None, 'shop_name': None, 'sales_from': None, 'sales_to': None}
        # Search hit
        formdata['sales_from'] = RefundTicketSearchHelper.format_date(self.sales_from - timedelta(days=10), format="%Y-%m-%d")
        receipts = lookup_receipt_by_searchform_data(self.request, formdata)
        self.assertTrue(receipts, msg='Failed to lookup receipt by sales_date: %s - %s' % (formdata['sales_from'], formdata['sales_to']))
        formdata['sales_to'] = RefundTicketSearchHelper.format_date(self.sales_from + timedelta(days=10), format="%Y-%m-%d")
        receipts = lookup_receipt_by_searchform_data(self.request, formdata)
        self.assertTrue(receipts, msg='Failed to lookup receipt by sales_date: %s - %s' % (formdata['sales_from'], formdata['sales_to']))
        # Search does not hit
        formdata['sales_from'] = RefundTicketSearchHelper.format_date(self.sales_from + timedelta(days=10), format="%Y-%m-%d")
        receipts = lookup_receipt_by_searchform_data(self.request, formdata)
        self.assertFalse(receipts, msg='Failed to lookup receipt by sales_date: %s - %s' % (formdata['sales_from'], formdata['sales_to']))
        formdata['sales_to'] = RefundTicketSearchHelper.format_date(self.sales_from + timedelta(days=10), format="%Y-%m-%d")
        receipts = lookup_receipt_by_searchform_data(self.request, formdata)
        self.assertFalse(receipts, msg='Failed to lookup receipt by sales_date: %s - %s' % (formdata['sales_from'], formdata['sales_to']))

    def test_search_receipt_by_customer_phone_number_and_shop_code(self):
        formdata = {'barcode_no': None, 'exchange_number': None, 'management_number': None, 'barcode_number': None, \
                    'customer_phone_number': None, 'shop_code': None, 'shop_name': None, 'sales_from': None, 'sales_to': None}
        # Search hit
        formdata['customer_phone_number'] = self.customer_phone_numbers[0]
        formdata['shop_code'] = self.shop_codes[0]
        receipts = lookup_receipt_by_searchform_data(self.request, formdata)
        self.assertTrue(receipts, msg='Failed to lookup receipt by customer_phone_numbers: %s and shop_code: %s' % (formdata['customer_phone_number'], formdata['shop_code']))
        # Search does not hit
        formdata['customer_phone_number'] = self.customer_phone_numbers[0]
        formdata['shop_code'] = self.shop_codes[2]
        receipts = lookup_receipt_by_searchform_data(self.request, formdata)
        self.assertFalse(receipts, msg='Failed to lookup receipt by customer_phone_numbers: %s and shop_code: %s' % (formdata['customer_phone_number'], formdata['shop_code']))
