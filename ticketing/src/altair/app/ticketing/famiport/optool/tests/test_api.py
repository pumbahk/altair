# -*- coding:utf-8 -*-
from datetime import datetime, date, timedelta
from unittest import TestCase
from pyramid.testing import DummyRequest, setUp, tearDown
from altair.sqlahelper import get_global_db_session
from altair.app.ticketing.famiport.testing import _setup_db, _teardown_db
from ..helpers import RefundTicketSearchHelper
from ..api import (
    create_user,
    lookup_user_by_credentials,
    lookup_receipt_by_searchform_data,
    lookup_refund_performance_by_searchform_data,
    search_refund_ticket_by
    )
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
            FamiPortRefund,
            FamiPortRefundEntry
            )
import logging

logger = logging.getLogger(__name__)

class APITestBase(object):
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


class UserCreationTest(APITestBase, TestCase):
    def test_create_user(self):
        user_name = u'famiport_test'
        password = u'famiport'
        role = u'test'
        create_user(self.request, user_name, password, role)
        user = lookup_user_by_credentials(self.request, user_name, password)
        self.assertIsNotNone(user)


class ReceiptSearchTest(APITestBase, TestCase):

    def setUp(self):
        APITestBase.setUp(self)

        self.barcode_nos = (u'01234012340123', u'01234012340124', u'01234012340126')
        self.reserve_numbers = (u'4321043210432', u'4321043210433', u'4321043210434', u'4321043210435')
        self.management_numbers = (u'000011112222', u'000011112223', u'000011112224', u'000011112225', u'000011112226', u'000011112227', u'000011112228')
        self.barcode_numbers = (u'0000000000001', u'0000000000002', u'0000000000003', u'0000000000004', u'0000000000005', u'0000000000006')
        self.customer_phone_numbers = (u'0301234567', u'0312345678', u'0323456789')
        self.shop_codes = (u'00001', u'00002', u'00003', u'00004')
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
            discrimination_code=5,
            discrimination_code_2=4
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
            customer_phone_number=self.customer_phone_numbers[0],
            famiport_receipts=[
                FamiPortReceipt(
                    type=FamiPortReceiptType.CashOnDelivery.value,
                    barcode_no=self.barcode_nos[0],
                    famiport_order_identifier=self.famiport_client.prefix + self.management_numbers[1],
                    shop_code=self.shop_codes[0],
                    reserve_number=self.reserve_numbers[0]
                    ),
                ],
            famiport_tickets=[
                FamiPortTicket(
                    type=FamiPortTicketType.TicketWithBarcode.value,
                    barcode_number=self.barcode_numbers[0],
                    template_code=u'TTTS000001',
                    data=u'<?xml version="1.0" encoding="Shift_JIS"><TICKET></TICKET>',
                    issued_at=None
                    ),
                FamiPortTicket(
                    type=FamiPortTicketType.TicketWithBarcode.value,
                    barcode_number=self.barcode_numbers[1],
                    template_code=u'TTTS000001',
                    data=u'<?xml version="1.0" encoding="Shift_JIS"><TICKET></TICKET>',
                    issued_at=None
                    )
                ],
            customer_name_input=False,
            customer_phone_input=False,
            created_at=datetime(2015, 5, 20, 12, 34, 56)
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
            total_amount=10540,
            ticket_payment=10000,
            ticketing_fee=216,
            system_fee=324,
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
                    barcode_no=self.barcode_nos[1],
                    famiport_order_identifier=self.famiport_client.prefix + self.management_numbers[3],
                    shop_code=self.shop_codes[1],
                    reserve_number=self.reserve_numbers[1],
                    ),
                FamiPortReceipt(
                    type=FamiPortReceiptType.Ticketing.value,
                    barcode_no=u'01234012340125',
                    famiport_order_identifier=self.famiport_client.prefix + self.management_numbers[4],
                    shop_code=self.shop_codes[2],
                    reserve_number=self.reserve_numbers[2],
                    )
                ],
            famiport_tickets=[
                FamiPortTicket(
                    type=FamiPortTicketType.TicketWithBarcode.value,
                    barcode_number=self.barcode_numbers[2],
                    template_code=u'TTTS000001',
                    data=u'<?xml version="1.0" encoding="Shift_JIS"><TICKET></TICKET>',
                    issued_at=None
                    ),
                FamiPortTicket(
                    type=FamiPortTicketType.TicketWithBarcode.value,
                    barcode_number=self.barcode_numbers[3],
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
            total_amount=10540,
            ticket_payment=10000,
            ticketing_fee=216,
            system_fee=324,
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
                    barcode_no=self.barcode_nos[2],
                    shop_code=self.shop_codes[3],
                    reserve_number=self.reserve_numbers[3]
                    ),
                ],
            famiport_tickets=[
                FamiPortTicket(
                    type=FamiPortTicketType.TicketWithBarcode.value,
                    barcode_number=self.barcode_numbers[4],
                    template_code=u'TTTS000001',
                    data=u'<?xml version="1.0" encoding="Shift_JIS"><TICKET></TICKET>',
                    issued_at=None
                    ),
                FamiPortTicket(
                    type=FamiPortTicketType.TicketWithBarcode.value,
                    barcode_number=self.barcode_numbers[5],
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
        formdata = {'barcode_no': None, 'reserve_number': None, 'management_number': None, 'barcode_number': None, \
                    'customer_phone_number': None, 'shop_code': None, 'shop_name': None, 'sales_from': None, 'sales_to': None}
        # Search hits
        for barcode_no in self.barcode_nos:
            formdata['barcode_no'] = barcode_no
            receipts = lookup_receipt_by_searchform_data(self.request, formdata)
            self.assertTrue(receipts, msg='Failed to lookup receipt by barcode_no: %s' % barcode_no)
        # Search does not hit
        for barcode_no in (u'00000000000000', u'test test test', u'abcdefghijklmn'):
            formdata['barcode_no'] = barcode_no
            receipts = lookup_receipt_by_searchform_data(self.request, formdata)
            self.assertFalse(receipts, msg='Failed to lookup receipt by barcode_no: %s' % barcode_no)


    def test_search_receipt_by_reserve_number(self):
        formdata = {'barcode_no': None, 'reserve_number': None, 'management_number': None, 'barcode_number': None, \
                    'customer_phone_number': None, 'shop_code': None, 'shop_name': None, 'sales_from': None, 'sales_to': None}
        # Search hits
        for reserve_number in self.reserve_numbers:
            formdata['reserve_number'] = reserve_number
            receipts = lookup_receipt_by_searchform_data(self.request, formdata)
            self.assertTrue(receipts, msg='Failed to lookup receipt by reserve_number: %s' % reserve_number)
        # Search does not hit
        for reserve_number in (u'0000000000000', u'test test test', u'abcdefghijklmn'):
            formdata['reserve_number'] = reserve_number
            receipts = lookup_receipt_by_searchform_data(self.request, formdata)
            self.assertFalse(receipts, msg='Failed to lookup receipt by reserve_number: %s' % reserve_number)

    def test_search_receipt_by_management_number(self):
        formdata = {'barcode_no': None, 'reserve_number': None, 'management_number': None, 'barcode_number': None, \
                    'customer_phone_number': None, 'shop_code': None, 'shop_name': None, 'sales_from': None, 'sales_to': None}
        # Search hits
        for management_number in self.management_numbers:
            formdata['management_number'] = management_number
            receipts = lookup_receipt_by_searchform_data(self.request, formdata)
            self.assertTrue(receipts, msg='Failed to lookup receipt by management_number: %s' % management_number)
        # Search does not hit
        for management_number in (u'000000000', u'test test test', u'abcdefghi'):
            formdata['management_number'] = management_number
            receipts = lookup_receipt_by_searchform_data(self.request, formdata)
            self.assertFalse(receipts, msg='Failed to lookup receipt by management_number: %s' % management_number)

    def test_search_receipt_by_barcode_number(self):
        formdata = {'barcode_no': None, 'reserve_number': None, 'management_number': None, 'barcode_number': None, \
                    'customer_phone_number': None, 'shop_code': None, 'shop_name': None, 'sales_from': None, 'sales_to': None}
        # Search hits
        for barcode_number in self.barcode_numbers:
            formdata['barcode_number'] = barcode_number
            receipts = lookup_receipt_by_searchform_data(self.request, formdata)
            self.assertTrue(receipts, msg='Failed to lookup receipt by barcode_number')
        # Search does not hit
        for barcode_number in (u'0000000000000', u'test test test', u'abcdefghijklmn'):
            formdata['barcode_number'] = barcode_number
            receipts = lookup_receipt_by_searchform_data(self.request, formdata)
            self.assertFalse(receipts, msg='Failed to lookup receipt by barcode_number')

    def test_search_receipt_by_customer_phone_number(self):
        formdata = {'barcode_no': None, 'reserve_number': None, 'management_number': None, 'barcode_number': None, \
                    'customer_phone_number': None, 'shop_code': None, 'shop_name': None, 'sales_from': None, 'sales_to': None}
        # Search hits
        for customer_phone_number in self.customer_phone_numbers:
            formdata['customer_phone_number'] = customer_phone_number
            receipts = lookup_receipt_by_searchform_data(self.request, formdata)
            self.assertTrue(receipts, msg='Failed to lookup receipt by customer_phone_number: %s' % customer_phone_number)
        # Search does not hit
        for customer_phone_number in (u'1234567', u'0300000000', u'01234567'):
            formdata['customer_phone_number'] = customer_phone_number
            receipts = lookup_receipt_by_searchform_data(self.request, formdata)
            self.assertFalse(receipts, msg='Failed to lookup receipt by customer_phone_number: %s' % customer_phone_number)

    def test_search_receipt_by_shop_code(self):
        formdata = {'barcode_no': None, 'reserve_number': None, 'management_number': None, 'barcode_number': None, \
                    'customer_phone_number': None, 'shop_code': None, 'shop_name': None, 'sales_from': None, 'sales_to': None}
        # Search hits
        for shop_code in self.shop_codes:
            formdata['shop_code'] = shop_code
            receipts = lookup_receipt_by_searchform_data(self.request, formdata)
            self.assertTrue(receipts, msg='Failed to lookup receipt by shop_code: %s' % shop_code)
        # Search does not hit
        for shop_code in (u'00000', u'11111', u'abcde'):
            formdata['shop_code'] = shop_code
            receipts = lookup_receipt_by_searchform_data(self.request, formdata)
            self.assertFalse(receipts, msg='Failed to lookup receipt by shop_code: %s' % shop_code)

    def test_search_receipt_by_shop_name(self):
        formdata = {'barcode_no': None, 'reserve_number': None, 'management_number': None, 'barcode_number': None, \
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
        formdata = {'barcode_no': None, 'reserve_number': None, 'management_number': None, 'barcode_number': None, \
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
        formdata = {'barcode_no': None, 'reserve_number': None, 'management_number': None, 'barcode_number': None, \
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


class RefundTicketSearchTest(APITestBase, TestCase):
    def setUp(self):
        APITestBase.setUp(self)

        self.management_numbers = (u'000011112222', u'000011112223')
        self.barcode_numbers = (u'0000000000001', u'0000000000002', u'0000000000003', u'0000000000004', u'0000000000005')
        self.shop_codes = (u'00001', u'00002', u'00003', u'00004')
        self.event_codes = (u'000001', u'000002')
        self.event_subcodes = (u'1111', u'2222')
        self.performance_start_dates = (datetime(2015, 7, 1, 19, 0, 0), datetime(2015, 8, 1, 19, 0, 0))

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
            name=u'西五反田',
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
            name=u'下目黒',
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
            name=u'代々木',
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
            name=u'玉川',
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
            discrimination_code=5,
            discrimination_code_2=4
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
        self.famiport_event1 = FamiPortEvent(
            client=self.famiport_client,
            venue=self.famiport_venue,
            genre_1=self.famiport_genre_1,
            genre_2=self.famiport_genre_2,
            sales_channel=FamiPortSalesChannel.FamiPortAndWeb.value,
            code_1=self.event_codes[0],
            code_2=self.event_subcodes[0],
            name_1=u'テスト公演1',
            name_2=u'テスト公演副題1',
            start_at=datetime(2015, 7, 1, 19, 0, 0),
            end_at=datetime(2015, 7, 10, 23, 59, 59),
            keywords=[u'チケットスター', u'博品館', u'イベント1'],
            purchasable_prefectures=[u'%02d' % FamiPortPrefecture.Nationwide.id],
            )
        self.famiport_event2 = FamiPortEvent(
            client=self.famiport_client,
            venue=self.famiport_venue,
            genre_1=self.famiport_genre_1,
            genre_2=self.famiport_genre_2,
            sales_channel=FamiPortSalesChannel.FamiPortAndWeb.value,
            code_1=self.event_codes[1],
            code_2=self.event_subcodes[1],
            name_1=u'テスト公演2',
            name_2=u'テスト公演副題2',
            start_at=datetime(2015, 8, 1, 19, 0, 0),
            end_at=datetime(2015, 8, 10, 23, 59, 59),
            keywords=[u'Famiポート', u'博品館', u'イベント2'],
            purchasable_prefectures=[u'%02d' % FamiPortPrefecture.Nationwide.id],
            )
        self.famiport_performance1 = FamiPortPerformance(
            famiport_event=self.famiport_event1,
            code=u'001',
            name=u'7/1公演',
            type=FamiPortPerformanceType.Normal.value,
            searchable=False,
            sales_channel=FamiPortSalesChannel.FamiPortAndWeb.value,
            start_at=self.performance_start_dates[0],
            ticket_name=u''
            )
        self.famiport_performance2 = FamiPortPerformance(
            famiport_event=self.famiport_event2,
            code=u'002',
            name=u'8/1公演',
            type=FamiPortPerformanceType.Normal.value,
            searchable=False,
            sales_channel=FamiPortSalesChannel.FamiPortAndWeb.value,
            start_at=self.performance_start_dates[1],
            ticket_name=u''
            )
        self.famiport_sales_segment1 = FamiPortSalesSegment(
            famiport_performance=self.famiport_performance1,
            code=u'001',
            name=u'一般販売',
            sales_channel=FamiPortSalesChannel.FamiPortAndWeb.value,
            published_at=datetime(2015, 4, 15, 0, 0, 0),
            start_at=datetime(2015, 4, 1, 10, 0, 0),
            end_at=datetime(2015, 5, 31, 23, 59, 59),
            auth_required=False,
            auth_message=u'',
            seat_selection_start_at=datetime(2015, 5, 10, 10, 0, 0)
            )
        self.famiport_sales_segment2 = FamiPortSalesSegment(
            famiport_performance=self.famiport_performance2,
            code=u'001',
            name=u'一般販売',
            sales_channel=FamiPortSalesChannel.FamiPortAndWeb.value,
            published_at=datetime(2015, 5, 15, 0, 0, 0),
            start_at=datetime(2015, 5, 1, 10, 0, 0),
            end_at=datetime(2015, 6, 30, 23, 59, 59),
            auth_required=False,
            auth_message=u'',
            seat_selection_start_at=datetime(2015, 6, 10, 10, 0, 0)
           )
        self.famiport_order1 = FamiPortOrder(
            type=FamiPortOrderType.CashOnDelivery.value,
            order_no=u'RT0000000000',
            famiport_order_identifier=self.famiport_client.prefix + u'000011112200',
            famiport_sales_segment=self.famiport_sales_segment1,
            famiport_client=self.famiport_client,
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
            famiport_receipts=[
                FamiPortReceipt(
                    type=FamiPortReceiptType.CashOnDelivery.value,
                    barcode_no=u'01234012340123',
                    famiport_order_identifier=self.famiport_client.prefix + self.management_numbers[0],
                    shop_code=self.shop_codes[0],
                    reserve_number=u'4321043210432'
                    ),
                ],
            famiport_tickets=[
                FamiPortTicket(
                    type=FamiPortTicketType.TicketWithBarcode.value,
                    barcode_number=self.barcode_numbers[0],
                    template_code=u'TTTS000001',
                    data=u'<?xml version="1.0" encoding="Shift_JIS"><TICKET></TICKET>',
                    issued_at=None
                    ),
                FamiPortTicket(
                    type=FamiPortTicketType.TicketWithBarcode.value,
                    barcode_number=self.barcode_numbers[1],
                    template_code=u'TTTS000001',
                    data=u'<?xml version="1.0" encoding="Shift_JIS"><TICKET></TICKET>',
                    issued_at=None
                    )
                ],
            customer_name_input=False,
            customer_phone_input=False,
            created_at=datetime.now()
            )
        self.famiport_order2 = FamiPortOrder(
            type=FamiPortOrderType.Payment.value,
            order_no=u'RT0000000001',
            famiport_order_identifier=self.famiport_client.prefix + u'000011112201',
            famiport_sales_segment=self.famiport_sales_segment2,
            famiport_client=self.famiport_client,
            generation=0,
            invalidated_at=None,
            total_amount=10540,
            ticket_payment=10000,
            ticketing_fee=216,
            system_fee=324,
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
            customer_phone_number=u'0301234567',
            famiport_receipts=[
                FamiPortReceipt(
                    type=FamiPortReceiptType.Payment.value,
                    barcode_no=u'01234012340124',
                    famiport_order_identifier=self.management_numbers[1],
                    shop_code=self.shop_codes[1],
                    reserve_number=u'4321043210433',
                    ),
                FamiPortReceipt(
                    type=FamiPortReceiptType.Ticketing.value,
                    barcode_no=u'01234012340126',
                    famiport_order_identifier=self.famiport_client.prefix + u'000011112202',
                    shop_code=self.shop_codes[2],
                    reserve_number=u'4321043210434',
                    )
                ],
            famiport_tickets=[
                FamiPortTicket(
                    type=FamiPortTicketType.TicketWithBarcode.value,
                    barcode_number=self.barcode_numbers[2],
                    template_code=u'TTTS000001',
                    data=u'<?xml version="1.0" encoding="Shift_JIS"><TICKET></TICKET>',
                    issued_at=None
                    ),
                FamiPortTicket(
                    type=FamiPortTicketType.TicketWithBarcode.value,
                    barcode_number=self.barcode_numbers[3],
                    template_code=u'TTTS000001',
                    data=u'<?xml version="1.0" encoding="Shift_JIS"><TICKET></TICKET>',
                    issued_at=None
                    ),
                FamiPortTicket(
                    type=FamiPortTicketType.TicketWithBarcode.value,
                    barcode_number=self.barcode_numbers[4],
                    template_code=u'TTTS000001',
                    data=u'<?xml version="1.0" encoding="Shift_JIS"><TICKET></TICKET>',
                    issued_at=None
                    )
                ],
            customer_name_input=False,
            customer_phone_input=False,
            created_at=datetime.now()
            )
        self.session.add(self.famiport_order1)
        self.session.add(self.famiport_order2)

        self.famiport_refund1 = FamiPortRefund(
            send_back_due_at=datetime(2015, 7, 1, 0, 0, 0),
            start_at=datetime(2015, 6, 1, 0, 0, 0),
            end_at=datetime(2015, 6, 30, 23, 59, 59),
            client_code=u'00001'
        )
        self.famiport_refund2 = FamiPortRefund(
            send_back_due_at=datetime(2015, 8, 1, 0, 0, 0),
            start_at=datetime(2015, 7, 1, 0, 0, 0),
            end_at=datetime(2015, 7, 31, 23, 59, 59),
            client_code=u'00001'
        )
        self.famiport_refund3 = FamiPortRefund(
            send_back_due_at=datetime(2015, 9, 1, 0, 0, 0),
            start_at=datetime(2015, 8, 1, 0, 0, 0),
            end_at=datetime(2015, 8, 31, 23, 59, 59),
            client_code=u'00001'
        )
        self.session.add(self.famiport_refund1)
        self.session.add(self.famiport_refund2)
        self.session.add(self.famiport_refund3)

        self.famiport_refund_entry1 = FamiPortRefundEntry(
            famiport_refund=self.famiport_refund1,
            famiport_ticket=self.famiport_order1.famiport_tickets[0],
            ticket_payment=10000,
            ticketing_fee=100,
            shop_code=self.shop_codes[0],
            refunded_at=datetime(2015, 6, 10, 10, 0, 0)
        )
        self.famiport_refund_entry2 = FamiPortRefundEntry(
            famiport_refund=self.famiport_refund1,
            famiport_ticket=self.famiport_order1.famiport_tickets[1],
            ticket_payment=10000,
            ticketing_fee=100,
            shop_code=self.shop_codes[1],
            refunded_at=datetime(2015, 6, 15, 10, 0, 0)
        )
        self.famiport_refund_entry3 = FamiPortRefundEntry(
            famiport_refund=self.famiport_refund2,
            famiport_ticket=self.famiport_order2.famiport_tickets[0],
            ticket_payment=10000,
            ticketing_fee=100,
            shop_code=self.shop_codes[2],
            refunded_at=datetime(2015, 7, 10, 10, 0, 0)
        )
        self.famiport_refund_entry4 = FamiPortRefundEntry(
            famiport_refund=self.famiport_refund2,
            famiport_ticket=self.famiport_order2.famiport_tickets[1],
            ticket_payment=10000,
            ticketing_fee=100,
            shop_code=self.shop_codes[3],
            refunded_at=datetime(2015, 7, 15, 10, 0, 0)
        )
        self.famiport_refund_entry5 = FamiPortRefundEntry(
            famiport_refund=self.famiport_refund3,
            famiport_ticket=self.famiport_order2.famiport_tickets[2],
            ticket_payment=10000,
            ticketing_fee=100,
            shop_code=self.shop_codes[3],
            refunded_at=datetime(2015, 8, 15, 10, 0, 0)
        )
        self.session.add(self.famiport_refund_entry1)
        self.session.add(self.famiport_refund_entry2)
        self.session.add(self.famiport_refund_entry3)
        self.session.add(self.famiport_refund_entry4)
        self.session.add(self.famiport_refund_entry5)

        self.session.commit()

    def test_search_refund_ticket_by_refund_term(self):
        params = {'before_refund': None, 'during_refund': None, 'after_refund': None, 'management_number': None, 'barcode_number': None, \
                  'refunded_shop_code': None, 'event_code': None, 'event_subcode': None, 'performance_start_date': None, 'performance_end_date': None}
        # Search hit
        refund_term_flags = (('y', 'y', 'y'), ('y', 'y', ''), ('', 'y', 'y'), ('y', '', 'y'), ('y', '', ''), ('', 'y', ''), ('', '', 'y'), ('', '', ''))
        for refund_term_flag in refund_term_flags:
            params['before_refund'] = refund_term_flag[0]
            params['during_refund'] = refund_term_flag[1]
            params['after_refund'] = refund_term_flag[2]
            refund_ticket = search_refund_ticket_by(self.request, params, now=datetime(2015, 7, 30, 0, 0, 0))
            self.assertTrue(refund_ticket, msg='Failed to search refund ticket by refund term. %r' % params)

    def test_search_refund_ticket_by_management_number(self):
        params = {'before_refund': None, 'during_refund': None, 'after_refund': None, 'management_number': None, 'barcode_number': None, \
                  'refunded_shop_code': None, 'event_code': None, 'event_subcode': None, 'performance_start_date': None, 'performance_end_date': None}
        # Search hits
        for management_number in self.management_numbers:
            params['management_number'] = management_number
            refund_ticket = search_refund_ticket_by(self.request, params)
            self.assertTrue(refund_ticket, msg='Failed to search refund ticket by management_number: %s' % management_number)
        # Search does not hit
        for management_number in (u'000000000', u'test test test', u'abcdefghi'):
            params['management_number'] = management_number
            refund_ticket = search_refund_ticket_by(self.request, params)
            self.assertFalse(refund_ticket, msg='Failed to search refund ticket by management_number: %s' % management_number)

    def test_search_refund_ticket_by_barcode_number(self):
        params = {'before_refund': None, 'during_refund': None, 'after_refund': None, 'management_number': None, 'barcode_number': None, \
                  'refunded_shop_code': None, 'event_code': None, 'event_subcode': None, 'performance_start_date': None, 'performance_end_date': None}
        # Search hits
        for barcode_number in self.barcode_numbers:
            params['barcode_number'] = barcode_number
            refund_ticket = search_refund_ticket_by(self.request, params)
            self.assertTrue(refund_ticket, msg='Failed to search refund ticket by barcode_number: %s' % barcode_number)
        # Search does not hit
        for barcode_number in (u'0000000000000', u'test test test', u'abcdefghijklmn'):
            params['barcode_number'] = barcode_number
            refund_ticket = search_refund_ticket_by(self.request, params)
            self.assertFalse(refund_ticket, msg='Failed to search refund ticket by barcode_number: %s' % barcode_number)

    def test_search_refund_ticket_by_shop_code(self):
        params = {'before_refund': None, 'during_refund': None, 'after_refund': None, 'management_number': None, 'barcode_number': None, \
                  'refunded_shop_code': None, 'event_code': None, 'event_subcode': None, 'performance_start_date': None, 'performance_end_date': None}
        # Search hits
        for shop_code in self.shop_codes:
            params['refunded_shop_code'] = shop_code
            refund_ticket = search_refund_ticket_by(self.request, params)
            self.assertTrue(refund_ticket, msg='Failed to search refund ticket by refunded_shop_code: %s' % shop_code)
        # Search does not hit
        for shop_code in (u'00000', u'11111', u'abcde'):
            params['refunded_shop_code'] = shop_code
            refund_ticket = search_refund_ticket_by(self.request, params)
            self.assertFalse(refund_ticket, msg='Failed to search refund ticket by refunded_shop_code: %s' % shop_code)

    def test_search_refund_ticket_by_event_code(self):
        params = {'before_refund': None, 'during_refund': None, 'after_refund': None, 'management_number': None, 'barcode_number': None, \
                  'refunded_shop_code': None, 'event_code': None, 'event_subcode': None, 'performance_start_date': None, 'performance_end_date': None}
        # Search hits
        for event_code in self.event_codes:
            params['event_code'] = event_code
            refund_ticket = search_refund_ticket_by(self.request, params)
            self.assertTrue(refund_ticket, msg='Failed to search refund ticket by event_code: %s' % event_code)
        # Search does not hit
        for event_code in (u'000000', u'111111', u'abcdef'):
            params['event_code'] = event_code
            refund_ticket = search_refund_ticket_by(self.request, params)
            self.assertFalse(refund_ticket, msg='Failed to search refund ticket by event_code: %s' % event_code)

    def test_search_refund_ticket_by_event_subcode(self):
        params = {'before_refund': None, 'during_refund': None, 'after_refund': None, 'management_number': None, 'barcode_number': None, \
                  'refunded_shop_code': None, 'event_code': None, 'event_subcode': None, 'performance_start_date': None, 'performance_end_date': None}
        # Search hits
        for event_subcode in self.event_subcodes:
            params['event_subcode'] = event_subcode
            refund_ticket = search_refund_ticket_by(self.request, params)
            self.assertTrue(refund_ticket, msg='Failed to search refund ticket by event_subcode: %s' % event_subcode)
        # Search does not hit
        for event_subcode in (u'000000', u'111111', u'abcdef'):
            params['event_subcode'] = event_subcode
            refund_ticket = search_refund_ticket_by(self.request, params)
            self.assertFalse(refund_ticket, msg='Failed to search refund ticket by event_code: %s' % event_subcode)

    def test_search_refund_ticket_by_performance_start_date(self):
        params = {'before_refund': None, 'during_refund': None, 'after_refund': None, 'management_number': None, 'barcode_number': None, \
                  'refunded_shop_code': None, 'event_code': None, 'event_subcode': None, 'performance_start_date': None, 'performance_end_date': None}
        # Search hits
        for performance_start_date in self.performance_start_dates:
            str_performance_start_date = RefundTicketSearchHelper.format_date(performance_start_date - timedelta(days=10), format="%Y-%m-%d")
            params['performance_start_date'] = str_performance_start_date
            str_performance_end_date = RefundTicketSearchHelper.format_date(performance_start_date + timedelta(days=10), format="%Y-%m-%d")
            params['performance_end_date'] = str_performance_end_date
            refund_ticket = search_refund_ticket_by(self.request, params)
            self.assertTrue(refund_ticket, msg='Failed to search refund ticket by performance_start_date: %s, performance_end_date: %s' % (str_performance_start_date, str_performance_end_date))
        # Search does not hit
        for performance_start_date in self.performance_start_dates:
            str_performance_start_date = RefundTicketSearchHelper.format_date(performance_start_date + timedelta(days=10), format="%Y-%m-%d")
            params['performance_start_date'] = str_performance_start_date
            str_performance_end_date = RefundTicketSearchHelper.format_date(performance_start_date - timedelta(days=10), format="%Y-%m-%d")
            params['performance_end_date'] = str_performance_end_date
            refund_ticket = search_refund_ticket_by(self.request, params)
            self.assertFalse(refund_ticket, msg='Failed to search refund ticket by performance_start_date: %s, performance_end_date: %s' % (str_performance_start_date, str_performance_end_date))

    def test_search_refund_ticket_by_shop_code_and_event_code(self):
        params = {'before_refund': None, 'during_refund': None, 'after_refund': None, 'management_number': None, 'barcode_number': None, \
                  'refunded_shop_code': None, 'event_code': None, 'event_subcode': None, 'performance_start_date': None, 'performance_end_date': None}
        # Search hits
        params['refunded_shop_code'] = self.shop_codes[3]
        params['event_code'] = self.event_codes[1]
        refund_ticket = search_refund_ticket_by(self.request, params)
        self.assertTrue(refund_ticket, msg='Failed to search refund ticket by refunded_shop_code: %s, event_code: %s' % ( params['refunded_shop_code'], params['event_code']))
        # Search does not hit
        params['refunded_shop_code'] = self.shop_codes[3]
        params['event_code'] = self.event_codes[0]
        refund_ticket = search_refund_ticket_by(self.request, params)
        self.assertFalse(refund_ticket, msg='Failed to search refund ticket by refunded_shop_code: %s, event_code: %s' % ( params['refunded_shop_code'], params['event_code']))


class RefundPerformanceSearchTest(APITestBase, TestCase):
    def setUp(self):
        APITestBase.setUp(self)

        self.management_numbers = (u'000011112222', u'000011112223')
        self.barcode_numbers = (u'0000000000001', u'0000000000002', u'0000000000003', u'0000000000004', u'0000000000005')
        self.shop_codes = (u'00001', u'00002', u'00003', u'00004')
        self.event_codes = (u'000001', u'000002')
        self.event_subcodes = (u'1111', u'2222')
        self.performance_start_dates = (datetime.now() - timedelta(days=30), datetime.now() + timedelta(days=30)) # (datetime(2015, 7, 1, 19, 0, 0), datetime(2015, 8, 1, 19, 0, 0))

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
            name=u'西五反田',
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
            name=u'下目黒',
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
            name=u'代々木',
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
            name=u'玉川',
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
            discrimination_code=5,
            discrimination_code_2=4
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
        self.famiport_event1 = FamiPortEvent(
            client=self.famiport_client,
            venue=self.famiport_venue,
            genre_1=self.famiport_genre_1,
            genre_2=self.famiport_genre_2,
            sales_channel=FamiPortSalesChannel.FamiPortAndWeb.value,
            code_1=self.event_codes[0],
            code_2=self.event_subcodes[0],
            name_1=u'テスト公演1',
            name_2=u'テスト公演副題1',
            start_at=datetime(2015, 7, 1, 19, 0, 0),
            end_at=datetime(2015, 7, 10, 23, 59, 59),
            keywords=[u'チケットスター', u'博品館', u'イベント1'],
            purchasable_prefectures=[u'%02d' % FamiPortPrefecture.Nationwide.id],
            )
        self.famiport_event2 = FamiPortEvent(
            client=self.famiport_client,
            venue=self.famiport_venue,
            genre_1=self.famiport_genre_1,
            genre_2=self.famiport_genre_2,
            sales_channel=FamiPortSalesChannel.FamiPortAndWeb.value,
            code_1=self.event_codes[1],
            code_2=self.event_subcodes[1],
            name_1=u'テスト公演2',
            name_2=u'テスト公演副題2',
            start_at=datetime(2015, 8, 1, 19, 0, 0),
            end_at=datetime(2015, 8, 10, 23, 59, 59),
            keywords=[u'Famiポート', u'博品館', u'イベント2'],
            purchasable_prefectures=[u'%02d' % FamiPortPrefecture.Nationwide.id],
            )
        self.famiport_performance1 = FamiPortPerformance(
            famiport_event=self.famiport_event1,
            code=u'001',
            name=u'7/1公演',
            type=FamiPortPerformanceType.Normal.value,
            searchable=False,
            sales_channel=FamiPortSalesChannel.FamiPortAndWeb.value,
            start_at=self.performance_start_dates[0],
            ticket_name=u''
            )
        self.famiport_performance2 = FamiPortPerformance(
            famiport_event=self.famiport_event2,
            code=u'002',
            name=u'8/1公演',
            type=FamiPortPerformanceType.Normal.value,
            searchable=False,
            sales_channel=FamiPortSalesChannel.FamiPortAndWeb.value,
            start_at=self.performance_start_dates[1],
            ticket_name=u''
            )
        self.famiport_sales_segment1 = FamiPortSalesSegment(
            famiport_performance=self.famiport_performance1,
            code=u'001',
            name=u'先行販売',
            sales_channel=FamiPortSalesChannel.FamiPortAndWeb.value,
            published_at=datetime(2015, 4, 15, 0, 0, 0),
            start_at=datetime(2015, 4, 1, 10, 0, 0),
            end_at=datetime(2015, 5, 31, 23, 59, 59),
            auth_required=False,
            auth_message=u'',
            seat_selection_start_at=datetime(2015, 5, 10, 10, 0, 0)
            )
        self.famiport_sales_segment2 = FamiPortSalesSegment(
            famiport_performance=self.famiport_performance2,
            code=u'002',
            name=u'一般販売',
            sales_channel=FamiPortSalesChannel.FamiPortAndWeb.value,
            published_at=datetime(2015, 5, 15, 0, 0, 0),
            start_at=datetime(2015, 5, 1, 10, 0, 0),
            end_at=datetime(2015, 6, 30, 23, 59, 59),
            auth_required=False,
            auth_message=u'',
            seat_selection_start_at=datetime(2015, 6, 10, 10, 0, 0)
            )
        self.famiport_order1 = FamiPortOrder(
            type=FamiPortOrderType.CashOnDelivery.value,
            order_no=u'RT0000000000',
            famiport_order_identifier=self.famiport_client.prefix + self.management_numbers[0],
            famiport_sales_segment=self.famiport_sales_segment1,
            famiport_client=self.famiport_client,
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
            famiport_receipts=[
                FamiPortReceipt(
                    type=FamiPortReceiptType.CashOnDelivery.value,
                    barcode_no=u'01234012340123',
                    famiport_order_identifier=self.famiport_client.prefix + u'000011112200',
                    shop_code=self.shop_codes[0],
                    reserve_number=u'4321043210432'
                    ),
                ],
            famiport_tickets=[
                FamiPortTicket(
                    id = 1,
                    type=FamiPortTicketType.TicketWithBarcode.value,
                    barcode_number=self.barcode_numbers[0],
                    template_code=u'TTTS000001',
                    data=u'<?xml version="1.0" encoding="Shift_JIS"><TICKET></TICKET>',
                    issued_at=None
                    ),
                FamiPortTicket(
                    id = 2,
                    type=FamiPortTicketType.TicketWithBarcode.value,
                    barcode_number=self.barcode_numbers[1],
                    template_code=u'TTTS000001',
                    data=u'<?xml version="1.0" encoding="Shift_JIS"><TICKET></TICKET>',
                    issued_at=None
                    )
                ],
            customer_name_input=False,
            customer_phone_input=False,
            created_at=datetime.now()
            )
        self.famiport_order2 = FamiPortOrder(
            type=FamiPortOrderType.Payment.value,
            order_no=u'RT0000000001',
            famiport_order_identifier=self.famiport_client.prefix + self.management_numbers[1],
            famiport_sales_segment=self.famiport_sales_segment2,
            famiport_client=self.famiport_client,
            generation=0,
            invalidated_at=None,
            total_amount=10540,
            ticket_payment=10000,
            ticketing_fee=216,
            system_fee=324,
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
            customer_phone_number=u'0301234567',
            famiport_receipts=[
                FamiPortReceipt(
                    type=FamiPortReceiptType.Payment.value,
                    barcode_no=u'01234012340124',
                    famiport_order_identifier=self.famiport_client.prefix + u'000011112201',
                    shop_code=self.shop_codes[1],
                    reserve_number=u'4321043210433',
                    ),
                FamiPortReceipt(
                    type=FamiPortReceiptType.Ticketing.value,
                    barcode_no=u'01234012340126',
                    famiport_order_identifier=self.famiport_client.prefix + u'000011112202',
                    shop_code=self.shop_codes[2],
                    reserve_number=u'4321043210434',
                    )
                ],
            famiport_tickets=[
                FamiPortTicket(
                    id = 3,
                    type=FamiPortTicketType.TicketWithBarcode.value,
                    barcode_number=self.barcode_numbers[2],
                    template_code=u'TTTS000001',
                    data=u'<?xml version="1.0" encoding="Shift_JIS"><TICKET></TICKET>',
                    issued_at=None
                    ),
                FamiPortTicket(
                    id = 4,
                    type=FamiPortTicketType.TicketWithBarcode.value,
                    barcode_number=self.barcode_numbers[3],
                    template_code=u'TTTS000001',
                    data=u'<?xml version="1.0" encoding="Shift_JIS"><TICKET></TICKET>',
                    issued_at=None
                    ),
                FamiPortTicket(
                    id = 5,
                    type=FamiPortTicketType.TicketWithBarcode.value,
                    barcode_number=self.barcode_numbers[4],
                    template_code=u'TTTS000001',
                    data=u'<?xml version="1.0" encoding="Shift_JIS"><TICKET></TICKET>',
                    issued_at=None
                    )
                ],
            customer_name_input=False,
            customer_phone_input=False,
            created_at=datetime.now()
            )
        self.session.add(self.famiport_order1)
        self.session.add(self.famiport_order2)

        self.famiport_refund1 = FamiPortRefund(
            send_back_due_at=datetime.now() + timedelta(days=1),# datetime(2015, 7, 1, 0, 0, 0),
            start_at=datetime.now() - timedelta(days=30), # datetime(2015, 6, 1, 0, 0, 0),
            end_at=datetime.now() - timedelta(days=1),
            client_code=u'00001'
        )
        self.famiport_refund2 = FamiPortRefund(
            send_back_due_at=datetime.now() + timedelta(days=5),
            start_at=datetime.now() - timedelta(days=30),
            end_at=datetime.now() + timedelta(days=1),
            client_code=u'00001'
        )
        self.famiport_refund3 = FamiPortRefund(
            send_back_due_at=datetime.now() + timedelta(days=60),
            start_at=datetime.now() + timedelta(days=1),
            end_at=datetime.now() + timedelta(days=30),
            client_code=u'00001'
        )
        self.session.add(self.famiport_refund1)
        self.session.add(self.famiport_refund2)
        self.session.add(self.famiport_refund3)

        self.famiport_refund_entry1 = FamiPortRefundEntry(
            famiport_refund=self.famiport_refund1,
            famiport_ticket=self.famiport_order1.famiport_tickets[0],
            # ticket_payment=10000,
            # ticketing_fee=100,
            shop_code=self.shop_codes[0],
            refunded_at=datetime(2015, 6, 10, 10, 0, 0)
        )
        self.famiport_refund_entry2 = FamiPortRefundEntry(
            famiport_refund=self.famiport_refund1,
            famiport_ticket=self.famiport_order1.famiport_tickets[1],
            # ticket_payment=10000,
            # ticketing_fee=100,
            shop_code=self.shop_codes[1],
            refunded_at=datetime(2015, 6, 15, 10, 0, 0)
        )
        self.famiport_refund_entry3 = FamiPortRefundEntry(
            famiport_refund=self.famiport_refund2,
            famiport_ticket=self.famiport_order2.famiport_tickets[0],
            # ticket_payment=10000,
            # ticketing_fee=100,
            shop_code=self.shop_codes[2],
            refunded_at=datetime(2015, 7, 10, 10, 0, 0)
        )
        self.famiport_refund_entry4 = FamiPortRefundEntry(
            famiport_refund=self.famiport_refund2,
            famiport_ticket=self.famiport_order2.famiport_tickets[1],
            # ticket_payment=10000,
            # ticketing_fee=100,
            shop_code=self.shop_codes[3],
            refunded_at=datetime(2015, 7, 15, 10, 0, 0)
        )
        self.famiport_refund_entry5 = FamiPortRefundEntry(
            famiport_refund=self.famiport_refund3,
            famiport_ticket=self.famiport_order2.famiport_tickets[2],
            # ticket_payment=10000,
            # ticketing_fee=100,
            shop_code=self.shop_codes[3],
            refunded_at=datetime(2015, 8, 15, 10, 0, 0)
        )
        self.session.add(self.famiport_refund_entry1)
        self.session.add(self.famiport_refund_entry2)
        self.session.add(self.famiport_refund_entry3)
        self.session.add(self.famiport_refund_entry4)
        self.session.add(self.famiport_refund_entry5)

        self.session.commit()

    def test_search_refund_performance_by_refund_term(self):
        formdata = {'before_refund': None, 'during_refund': None, 'after_refund': None, 'performance_from': None, 'performance_to': None}
        refund_term_flags = (('y', 'y', 'y'), ('y', 'y', ''), ('', 'y', 'y'), ('y', '', 'y'), ('y', '', ''), ('', 'y', ''), ('', '', 'y'), ('', '', ''))
        for refund_term_flag in refund_term_flags:
            formdata['before_refund'] = refund_term_flag[0]
            formdata['during_refund'] = refund_term_flag[1]
            formdata['after_refund'] = refund_term_flag[2]
            refund_performance = lookup_refund_performance_by_searchform_data(self.request, formdata)
            self.assertTrue(refund_performance, msg='Failed to search refund performance by refund term. before_refund: %s, during_refund: %s, after_refund: %s' % refund_term_flag)

    def test_search_refund_performance_by_performane_date(self):
        formdata = {'before_refund': None, 'during_refund': None, 'after_refund': None, 'performance_from': None, 'performance_to': None}
        # Search hit
        for performance_start_date in self.performance_start_dates:
            str_performance_from = RefundTicketSearchHelper.format_date(performance_start_date - timedelta(days=10), format="%Y-%m-%d")
            str_performance_to = RefundTicketSearchHelper.format_date(performance_start_date + timedelta(days=10), format="%Y-%m-%d")
            formdata['performance_from'] = str_performance_from
            formdata['performance_to'] = str_performance_to
            refund_performance = lookup_refund_performance_by_searchform_data(self.request, formdata)
            self.assertTrue(refund_performance, msg='Failed to search refund performance by performance_date. performance_from: %s, performance_to: %s' % (str_performance_from, str_performance_to))
        # Search does not hit
        for performance_start_date in self.performance_start_dates:
            str_performance_from = RefundTicketSearchHelper.format_date(performance_start_date + timedelta(days=10), format="%Y-%m-%d")
            str_performance_to = RefundTicketSearchHelper.format_date(performance_start_date + timedelta(days=20), format="%Y-%m-%d")
            formdata['performance_from'] = str_performance_from
            formdata['performance_to'] = str_performance_to
            refund_performance = lookup_refund_performance_by_searchform_data(self.request, formdata)
            self.assertFalse(refund_performance, msg='Failed to search refund performance by performance_date. performance_from: %s, performance_to: %s' % (str_performance_from, str_performance_to))
