# -*- coding: utf-8 -*-
import unittest
from datetime import (
    date,
    datetime,
    timedelta,
    )
from decimal import Decimal
from pyramid.testing import DummyRequest, setUp, tearDown
from altair.sqlahelper import get_global_db_session

from ..api import get_response_builder
from .builders import FamiPortRequestFactory
from .models import (
    FamiPortRequestType,
    InformationResultCodeEnum,
    FamiPortReservationInquiryRequest,
    FamiPortPaymentTicketingRequest,
    FamiPortPaymentTicketingCompletionRequest,
    FamiPortPaymentTicketingCancelRequest,
    FamiPortInformationRequest,
    FamiPortCustomerInformationRequest,
    )
from ..models import FamiPortInformationMessage
from ..testing import _setup_db, _teardown_db


class FamiPortResponseBuilderTestBase(object):
    barcode_no_cash_on_delivery = u'01234012340123'
    barcode_no_payment = u'01234012340124'
    barcode_no_payment_only = u'01234012340125'

    def setUp(self):
        self.request = DummyRequest()
        self.config = setUp(request=self.request)
        self.config.include('.')
        self.engine = _setup_db(
            self.config.registry,
            [
                'altair.app.ticketing.famiport.models',
                'altair.app.ticketing.famiport.communication.models',
                ]
            )
        self.session = get_global_db_session(self.config.registry, 'famiport')
        from ..models import (
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
            FamiPortInformationMessage,
            FamiPortPrefecture,
            FamiPortOrder,
            FamiPortReceipt,
            FamiPortOrderType,
            FamiPortTicketType,
            FamiPortTicket,
            FamiPortShop,
            )
        self.famiport_shop = FamiPortShop(
            code=u'000009',
            company_code=u'TEST',
            company_name=u'TEST',
            district_code=u'TEST',
            district_name=u'TEST',
            district_valid_from=date(2015, 6, 1),
            branch_code=u'TEST',
            branch_name=u'TEST',
            branch_valid_from=date(2015, 6, 1),
            name=u'TEST',
            name_kana=u'TEST',
            tel=u'070111122222',
            prefecture=1,
            prefecture_name=u'東京都',
            address=u'東京都品川区西五反田',
            open_from=date(2015, 6, 1),
            zip=u'1410000',
            business_run_from=date(2015, 6, 1),
            )
        self.session.add(self.famiport_shop)
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
            code=u'00000000000000000000111',
            name=u'大ジャンル'
            )
        self.famiport_genre_2 = FamiPortGenre2(
            code=u'00000000000000000000000000000022222',
            name=u'小ジャンル'
            )
        self.famiport_venue = FamiPortVenue(
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
            start_at=datetime(2015, 5, 1, 10, 0, 0),
            end_at=datetime(2015, 5, 31, 23, 59, 59),
            auth_required=False,
            auth_message=u'',
            seat_selection_start_at=datetime(2015, 5, 10, 10, 0, 0)
            )
        self.famiport_order_cash_on_delivery = FamiPortOrder(
            type=FamiPortOrderType.CashOnDelivery.value,
            order_no=u'RT0000000000',
            famiport_order_identifier=u'000011112222',
            shop_code=u'00001',
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
            cancel_reason=None,
            ticketing_start_at=datetime(2015, 5, 20, 12, 34, 56),
            ticketing_end_at=datetime(2015, 5, 23, 23, 59, 59),
            payment_start_at=datetime(2015, 5, 20, 12, 34, 56),
            payment_due_at=datetime(2015, 5, 23, 23, 59, 59),
            reserve_number=u'4321043210432',
            customer_name=u'チケット　太郎',
            customer_address_1=u'東京都品川区西五反田7-1-9',
            customer_address_2=u'五反田HSビル9F',
            customer_phone_number=u'0123456789',
            famiport_receipts=[
                FamiPortReceipt(
                    exchange_number=u'',
                    barcode_no=self.barcode_no_cash_on_delivery,
                    famiport_shop=self.famiport_shop,
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
            created_at=datetime(2015, 5, 20, 12, 34, 56)
            )
        self.session.add(self.famiport_order_cash_on_delivery)
        self.famiport_order_payment = FamiPortOrder(
            type=FamiPortOrderType.Payment.value,
            order_no=u'RT0000000001',
            famiport_order_identifier=u'000011112223',
            shop_code=u'00001',
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
            cancel_reason=None,
            ticketing_start_at=datetime(2015, 5, 22, 00, 00, 00),
            ticketing_end_at=datetime(2015, 5, 23, 23, 59, 59),
            payment_start_at=datetime(2015, 5, 20, 12, 34, 56),
            payment_due_at=datetime(2015, 5, 21, 23, 59, 59),
            reserve_number=u'4321043210433',
            customer_name=u'チケット　太郎',
            customer_address_1=u'東京都品川区西五反田7-1-9',
            customer_address_2=u'五反田HSビル9F',
            customer_phone_number=u'0123456789',
            famiport_receipts=[
                FamiPortReceipt(
                    exchange_number=u'',
                    barcode_no=self.barcode_no_payment,
                    famiport_shop=self.famiport_shop,
                    ),
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
            created_at=datetime(2015, 5, 20, 12, 34, 56)
            )
        self.session.add(self.famiport_order_payment)
        self.famiport_order_payment_only = FamiPortOrder(
            type=FamiPortOrderType.PaymentOnly.value,
            order_no=u'RT0000000001',
            famiport_order_identifier=u'000011112224',
            shop_code=u'00001',
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
            cancel_reason=None,
            ticketing_start_at=None,
            ticketing_end_at=None,
            payment_start_at=datetime(2015, 5, 22, 12, 34, 56),
            payment_due_at=datetime(2015, 5, 23, 23, 59, 59),
            reserve_number=u'4321043210434',
            customer_name=u'チケット　太郎',
            customer_address_1=u'東京都品川区西五反田7-1-9',
            customer_address_2=u'五反田HSビル9F',
            customer_phone_number=u'0123456789',
            famiport_receipts=[
                FamiPortReceipt(
                    exchange_number=u'',
                    barcode_no=self.barcode_no_payment_only,
                    famiport_shop=self.famiport_shop,
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
            created_at=datetime(2015, 5, 22, 12, 34, 56)
            )
        self.session.add(self.famiport_order_payment_only)
        self.session.commit()
        self.now = datetime(2015, 5, 21, 10, 0, 0)

    def tearDown(self):
        _teardown_db(self.config.registry)
        tearDown()


class FamiPortInformationMessageResponseBuilderTest(unittest.TestCase, FamiPortResponseBuilderTestBase):
    def setUp(self):
        FamiPortResponseBuilderTestBase.setUp(self)

    def tearDown(self):
        FamiPortResponseBuilderTestBase.tearDown(self)

    # 案内
    def test_with_information(self):
        famiport_information_with_information_message = FamiPortInformationMessage(
            result_code=InformationResultCodeEnum.WithInformation.name,
            message=u'WithInformation メッセージ',
            )
        self.session.add(famiport_information_with_information_message)
        self.session.commit()
        from .models import ResultCodeEnum, ReplyCodeEnum
        f_request = FamiPortRequestFactory.create_request(
            {
                'infoKubun':     u'1',
                'storeCode':     u'000009',
                'kogyoCode':     u'',
                'kogyoSubCode':  u'',
                'koenCode':      u'',
                'uketsukeCode':  u'',
                'playGuideId':   u'',
                'authCode':      u'',
                'reserveNumber': u'4000000000001',
                },
            FamiPortRequestType.Information
            )

        builder = get_response_builder(self.request, f_request)
        result = builder.build_response(f_request, self.session, self.now)
        self.assertEqual(result.resultCode, InformationResultCodeEnum.WithInformation.value)
        self.assertEqual(result.infoKubun, u'1')
        self.assertEqual(result.infoMessage, u'WithInformation メッセージ')

    # 案内
    def test_service_unavail(self):
        famiport_information_service_unavailable_message = FamiPortInformationMessage(
            result_code=InformationResultCodeEnum.ServiceUnavailable.name,
            message=u'Service Unavailableメッセージ',
            )
        self.session.add(famiport_information_service_unavailable_message)
        self.session.commit()
        from .models import ResultCodeEnum, ReplyCodeEnum
        f_request = FamiPortRequestFactory.create_request(
            {
                'infoKubun':     u'1',
                'storeCode':     u'000009',
                'kogyoCode':     u'',
                'kogyoSubCode':  u'',
                'koenCode':      u'',
                'uketsukeCode':  u'',
                'playGuideId':   u'',
                'authCode':      u'',
                'reserveNumber': u'4000000000001',
                },
            FamiPortRequestType.Information
            )

        builder = get_response_builder(self.request, f_request)
        result = builder.build_response(f_request, self.session, self.now)
        self.assertEqual(result.resultCode, InformationResultCodeEnum.ServiceUnavailable.value)
        self.assertEqual(result.infoKubun, u'1')
        self.assertEqual(result.infoMessage, u'Service Unavailableメッセージ')


class FamiPortCustomerInformationResponseBuilderTest(unittest.TestCase, FamiPortResponseBuilderTestBase):
    # 顧客情報照会
    def setUp(self):
        FamiPortResponseBuilderTestBase.setUp(self)

    def tearDown(self):
        FamiPortResponseBuilderTestBase.tearDown(self)

    def _payment_receipt(self, barcode_no, minutes=15):
        from ..models import FamiPortReceipt
        receipt = self.session \
                      .query(FamiPortReceipt) \
                      .filter_by(barcode_no=barcode_no) \
                      .one()
        time_point = datetime.now() - timedelta(minutes=minutes)
        receipt.inquired_at = time_point
        receipt.payment_request_received_at = time_point
        receipt._at = time_point
        self.session.add(receipt)
        self.session.commit()

    def test_ok(self):
        from .models import ResultCodeEnum, ReplyCodeEnum
        f_request = FamiPortCustomerInformationRequest(
            storeCode=u'000009',
            mmkNo=u'1',
            ticketingDate=u'20150521134001',
            sequenceNo=u'15052100001',
            barCodeNo=self.barcode_no_cash_on_delivery,
            playGuideId=self.famiport_client.code,
            orderId=u'000011112222',
            totalAmount=u'10540'
            )
        self._payment_receipt(self.barcode_no_cash_on_delivery)
        builder = get_response_builder(self.request, f_request)
        result = builder.build_response(f_request, self.session, self.now)
        self.assertEqual(result.resultCode, ResultCodeEnum.Normal.value)
        self.assertEqual(result.replyCode, ReplyCodeEnum.Normal.value)
        self.assertEqual(result.name, u'チケット　太郎')
        self.assertEqual(result.memberId, u'')
        self.assertEqual(result.address1, u'東京都品川区西五反田7-1-9')
        self.assertEqual(result.address2, u'五反田HSビル9F')
        self.assertEqual(result.identifyNo, u'')

    def test_not_found(self):
        from .models import ResultCodeEnum, ReplyCodeEnum
        f_request = FamiPortCustomerInformationRequest(
            storeCode=u'000009',
            mmkNo=u'1',
            ticketingDate=u'20150521134001',
            sequenceNo=u'15052100001',
            barCodeNo=u'0123401234012X',
            playGuideId=self.famiport_client.code,
            orderId=u'00001111222X',
            totalAmount=u'10540'
            )
        builder = get_response_builder(self.request, f_request)
        result = builder.build_response(f_request, self.session, self.now)
        self.assertEqual(result.resultCode, ResultCodeEnum.OtherError.value)
        self.assertEqual(result.replyCode, ReplyCodeEnum.CustomerNamePrintInformationError.value)
        self.assertEqual(result.name, None)
        self.assertEqual(result.memberId, None)
        self.assertEqual(result.address1, None)
        self.assertEqual(result.address2, None)
        self.assertEqual(result.identifyNo, None)


class FamiPortReservationInquiryResponseBuilderTest(unittest.TestCase, FamiPortResponseBuilderTestBase):
    # 予約照会
    def setUp(self):
        FamiPortResponseBuilderTestBase.setUp(self)

    def tearDown(self):
        FamiPortResponseBuilderTestBase.tearDown(self)

    def test_ok(self):

        from .models import ResultCodeEnum, ReplyClassEnum, ReplyCodeEnum
        f_request = FamiPortReservationInquiryRequest(
            storeCode=u'000009',
            ticketingDate=u'20150521134001',
            reserveNumber=u'4321043210432',
            authNumber=u''
            )
        builder = get_response_builder(self.request, f_request)
        result = builder.build_response(f_request, self.session, self.now)
        self.assertEqual(result.resultCode, ResultCodeEnum.Normal.value)
        self.assertEqual(result.replyClass, ReplyClassEnum.CashOnDelivery.value)
        self.assertEqual(result.replyCode, ReplyCodeEnum.Normal.value)
        self.assertEqual(result.playGuideId, u'012340123401234012340123')
        self.assertTrue(result.barCodeNo)
        self.assertEqual(result.totalAmount, u'00010540')
        self.assertEqual(result.ticketPayment, u'00010000')
        self.assertEqual(result.systemFee, u'00000324')
        self.assertEqual(result.ticketingFee, u'00000216')
        self.assertEqual(result.ticketCountTotal, u'2')
        self.assertEqual(result.ticketCount, u'2')
        self.assertEqual(result.kogyoName, u'7/1公演') # 興行名なので、「テスト公演」であるべきでは? 確認
        self.assertEqual(result.koenDate, u'201507011900')
        self.assertEqual(result.name, u'チケット　太郎')
        self.assertEqual(result.nameInput, u'0')
        self.assertEqual(result.phoneInput, u'0')

    def test_too_early(self):
        from .models import ResultCodeEnum, ReplyClassEnum, ReplyCodeEnum
        f_request = FamiPortReservationInquiryRequest(
            storeCode=u'000009',
            ticketingDate=u'20150520000000',
            reserveNumber=u'4321043210432',
            authNumber=u''
            )
        builder = get_response_builder(self.request, f_request)
        result = builder.build_response(f_request, self.session, self.now)
        self.assertEqual(result.resultCode, ResultCodeEnum.OtherError.value)
        self.assertEqual(result.replyCode, ReplyCodeEnum.SearchKeyError.value)
        self.assertEqual(result.playGuideId, u'')
        self.assertEqual(result.barCodeNo, u'')
        self.assertEqual(result.totalAmount, u'')
        self.assertEqual(result.ticketPayment, u'')
        self.assertEqual(result.systemFee, u'')
        self.assertEqual(result.ticketingFee, u'')
        self.assertEqual(result.ticketCountTotal, u'')
        self.assertEqual(result.ticketCount, u'')
        self.assertEqual(result.kogyoName, u'')
        self.assertEqual(result.koenDate, u'')
        self.assertEqual(result.name, u'')
        self.assertEqual(result.nameInput, u'0')
        self.assertEqual(result.phoneInput, u'0')

    def test_invalid_ticket_date(self):
        from .models import ResultCodeEnum, ReplyClassEnum, ReplyCodeEnum
        f_request = FamiPortReservationInquiryRequest(
            storeCode=u'000009',
            ticketingDate=u'20XX0521134001',
            reserveNumber=u'4321043210432',
            authNumber=u''
            )
        builder = get_response_builder(self.request, f_request)
        result = builder.build_response(f_request, self.session, self.now)
        self.assertEqual(result.resultCode, ResultCodeEnum.OtherError.value)
        self.assertEqual(result.replyClass, None)
        self.assertEqual(result.replyCode, ReplyCodeEnum.OtherError.value)
        self.assertEqual(result.barCodeNo, None)
        self.assertEqual(result.totalAmount, None)
        self.assertEqual(result.ticketPayment, None)
        self.assertEqual(result.systemFee, None)
        self.assertEqual(result.ticketingFee, None)
        self.assertEqual(result.ticketCountTotal, None)
        self.assertEqual(result.ticketCount, None)
        self.assertEqual(result.kogyoName, None)
        self.assertEqual(result.koenDate, None)
        self.assertEqual(result.name, None)
        self.assertEqual(result.nameInput, None)
        self.assertEqual(result.phoneInput, None)

    def test_not_found(self):
        from .models import ResultCodeEnum, ReplyClassEnum, ReplyCodeEnum
        f_request = FamiPortReservationInquiryRequest(
            storeCode=u'000009',
            ticketingDate=u'20150521134001',
            reserveNumber=u'432104321043X',
            authNumber=u''
            )
        builder = get_response_builder(self.request, f_request)
        result = builder.build_response(f_request, self.session, self.now)
        self.assertEqual(result.resultCode, ResultCodeEnum.OtherError.value)
        self.assertEqual(result.replyClass, None)
        self.assertEqual(result.replyCode, ReplyCodeEnum.SearchKeyError.value)
        self.assertEqual(result.barCodeNo, u'')
        self.assertEqual(result.totalAmount, u'')
        self.assertEqual(result.ticketPayment, u'')
        self.assertEqual(result.systemFee, u'')
        self.assertEqual(result.ticketingFee, u'')
        self.assertEqual(result.ticketCountTotal, u'')
        self.assertEqual(result.ticketCount, u'')
        self.assertEqual(result.kogyoName, u'')
        self.assertEqual(result.koenDate, u'')
        self.assertEqual(result.name, u'')
        self.assertEqual(result.nameInput, u'0')
        self.assertEqual(result.phoneInput, u'0')


class FamiPortCancelResponseBuilderTest(unittest.TestCase, FamiPortResponseBuilderTestBase):
    # 30分VOID処理

    def setUp(self):
        FamiPortResponseBuilderTestBase.setUp(self)

    def tearDown(self):
        FamiPortResponseBuilderTestBase.tearDown(self)

    def _get_target_class(self):
        from .builders import FamiPortPaymentTicketingCancelResponseBuilder as klass
        return klass

    def _get_target(self, *args, **kwds):
        klass = self._get_target_class()
        return klass(*args, **kwds)

    def _callFUT(self, *args, **kwds):
        target = self._get_target()
        return target.build_response(*args, **kwds)

    def _create_famiport_request(self, *args, **kwds):
        from .models import FamiPortPaymentTicketingCancelRequest as klass
        return klass(*args, **kwds)

    def test_ok(self):
        now = datetime.now()
        famiport_request = self._create_famiport_request(storeCode=u'099999')
        famiport_response = self._callFUT(famiport_request, self.session, now)

    def test_illigal(self):
        now = datetime.now()
        famiport_request = self._create_famiport_request(storeCode=u'099999')
        famiport_response = self._callFUT(famiport_request, self.session, now)

    def test_already_payment(self):
        from .models import ResultCodeEnum, ReplyCodeEnum
        now = datetime.now()
        famiport_request = self._create_famiport_request(storeCode=u'099999')
        famiport_response = self._callFUT(famiport_request, self.session, now)
        self.assertEqual(famiport_response.storeCode, famiport_request.storeCode)
        self.assertEqual(famiport_response.sequenceNo, famiport_request.sequenceNo)
        self.assertEqual(famiport_response.resultCode, ResultCodeEnum.OtherError.value)
        self.assertEqual(famiport_response.replyCode, ReplyCodeEnum.OtherError.value)

    def test_already_issued(self):
        from .models import ResultCodeEnum, ReplyCodeEnum
        now = datetime.now()
        famiport_request = self._create_famiport_request(storeCode=u'099999')
        famiport_response = self._callFUT(famiport_request, self.session, now)
        self.assertEqual(famiport_response.storeCode, famiport_request.storeCode)
        self.assertEqual(famiport_response.sequenceNo, famiport_request.sequenceNo)
        self.assertEqual(famiport_response.resultCode, ResultCodeEnum.OtherError.value)
        self.assertEqual(famiport_response.replyCode, ReplyCodeEnum.OtherError.value)

    def test_cannot_cancel(self):
        from .models import ResultCodeEnum, ReplyCodeEnum
        now = datetime.now()
        famiport_request = self._create_famiport_request(storeCode=u'099999')
        famiport_response = self._callFUT(famiport_request, self.session, now)
        self.assertEqual(famiport_response.storeCode, famiport_request.storeCode)
        self.assertEqual(famiport_response.sequenceNo, famiport_request.sequenceNo)
        self.assertEqual(famiport_response.resultCode, ResultCodeEnum.OtherError.value)
        self.assertEqual(famiport_response.replyCode, ReplyCodeEnum.OtherError.value)

    def test_no_receipt(self):
        from .models import ResultCodeEnum, ReplyCodeEnum
        now = datetime.now()
        famiport_request = self._create_famiport_request(storeCode=u'099999')
        famiport_response = self._callFUT(famiport_request, self.session, now)
        self.assertEqual(famiport_response.storeCode, famiport_request.storeCode)
        self.assertEqual(famiport_response.sequenceNo, famiport_request.sequenceNo)
        self.assertEqual(famiport_response.resultCode, ResultCodeEnum.OtherError.value)
        self.assertEqual(famiport_response.replyCode, ReplyCodeEnum.OtherError.value)

    def test_no_famport_order(self):
        from .models import ResultCodeEnum, ReplyCodeEnum
        now = datetime.now()
        famiport_request = self._create_famiport_request(storeCode=u'099999')
        famiport_response = self._callFUT(famiport_request, self.session, now)
        self.assertEqual(famiport_response.storeCode, famiport_request.storeCode)
        self.assertEqual(famiport_response.sequenceNo, famiport_request.sequenceNo)
        self.assertEqual(famiport_response.resultCode, ResultCodeEnum.OtherError.value)
        self.assertEqual(famiport_response.replyCode, ReplyCodeEnum.OtherError.value)


class FamiPortPaymentTicketingResponseBuilderTest(unittest.TestCase, FamiPortResponseBuilderTestBase):
    # 入金発券
    def setUp(self):
        FamiPortResponseBuilderTestBase.setUp(self)

    def tearDown(self):
        FamiPortResponseBuilderTestBase.tearDown(self)

    def _inquiry_receipt(self, barcode_no, minutes=15):
        from ..models import FamiPortReceipt
        receipt = self.session \
                      .query(FamiPortReceipt) \
                      .filter_by(barcode_no=barcode_no) \
                      .one()

        receipt.inquired_at = datetime.now() - timedelta(minutes=minutes)
        self.session.add(receipt)
        self.session.commit()

    def test_cash_on_delivery(self):
        # 代引
        from .models import ResultCodeEnum, ReplyClassEnum, ReplyCodeEnum
        f_request = FamiPortPaymentTicketingRequest(
            storeCode=u'000009',
            mmkNo=u'1',
            ticketingDate=u'20150521134001',
            sequenceNo=u'15052100002',
            playGuideId=u'012340123401234012340123',
            barCodeNo=u'01234012340123',
            customerName=u'カスタマ　太郎',
            phoneNumber=u'0123456789'
            )
        self._inquiry_receipt(u'01234012340123')
        builder = get_response_builder(self.request, f_request)
        result = builder.build_response(f_request, self.session, self.now)
        self.assertEqual(result.resultCode, ResultCodeEnum.Normal.value)
        self.assertEqual(result.replyClass, ReplyClassEnum.CashOnDelivery.value)
        self.assertEqual(result.replyCode, ReplyCodeEnum.Normal.value)
        self.assertEqual(result.storeCode, u'000009')
        self.assertEqual(result.sequenceNo, u'15052100002')
        self.assertEqual(result.barCodeNo, u'01234012340123')
        self.assertEqual(result.orderId, u'000011112222')
        self.assertEqual(result.playGuideId, u'012340123401234012340123')
        self.assertEqual(result.playGuideName, u'チケットスター')
        self.assertEqual(result.orderTicketNo, u'01234012340123')
        self.assertEqual(result.exchangeTicketNo, u'')
        self.assertEqual(result.ticketingStart, u'')
        self.assertEqual(result.ticketingEnd, u'')
        self.assertEqual(result.totalAmount, u'00010540')
        self.assertEqual(result.ticketPayment, u'00010000')
        self.assertEqual(result.systemFee, u'00000324')
        self.assertEqual(result.ticketingFee, u'00000216')
        self.assertEqual(result.ticketCountTotal, u'2')
        self.assertEqual(result.ticketCount, u'2')
        self.assertEqual(result.kogyoName, u'7/1公演')
        self.assertEqual(result.koenDate, u'201507011900')

    def test_payment_valid_date(self):
        # 前払後日
        from .models import ResultCodeEnum, ReplyClassEnum, ReplyCodeEnum
        f_request = FamiPortPaymentTicketingRequest(
            storeCode=u'000009',
            mmkNo=u'1',
            ticketingDate=u'20150521134001',
            sequenceNo=u'15052100003',
            playGuideId=u'012340123401234012340123',
            barCodeNo=u'01234012340124',
            customerName=u'カスタマ　太郎',
            phoneNumber=u'0123456789'
            )
        self._inquiry_receipt(u'01234012340124')
        builder = get_response_builder(self.request, f_request)
        result = builder.build_response(f_request, self.session, self.now)
        self.assertEqual(result.resultCode, ResultCodeEnum.Normal.value)
        self.assertEqual(result.replyClass, ReplyClassEnum.Prepayment.value)
        self.assertEqual(result.replyCode, ReplyCodeEnum.Normal.value)
        self.assertEqual(result.storeCode, u'000009')
        self.assertEqual(result.sequenceNo, u'15052100003')
        self.assertEqual(result.barCodeNo, u'01234012340124')
        self.assertEqual(result.orderId, u'000011112223')
        self.assertEqual(result.playGuideId, u'012340123401234012340123')
        self.assertEqual(result.playGuideName, u'チケットスター')
        self.assertEqual(result.orderTicketNo, u'01234012340124')
        self.assertEqual(result.exchangeTicketNo, u'')
        self.assertEqual(result.ticketingStart, u'20150522000000')
        self.assertEqual(result.ticketingEnd, u'20150523235959')
        self.assertEqual(result.totalAmount, u'00010540')
        self.assertEqual(result.ticketPayment, u'00010000')
        self.assertEqual(result.systemFee, u'00000324')
        self.assertEqual(result.ticketingFee, u'00000216')
        self.assertEqual(result.ticketCountTotal, u'2')
        self.assertEqual(result.ticketCount, u'2')
        self.assertEqual(result.kogyoName, u'7/1公演')
        self.assertEqual(result.koenDate, u'201507011900')

    def test_payment_earlier_date(self):
        # 前払後日
        from .models import ResultCodeEnum, ReplyClassEnum, ReplyCodeEnum
        f_request = FamiPortPaymentTicketingRequest(
            storeCode=u'000009',
            mmkNo=u'1',
            ticketingDate=u'20150520100000',
            sequenceNo=u'15052100003',
            playGuideId=u'012340123401234012340123',
            barCodeNo=u'01234012340124',
            customerName=u'カスタマ　太郎',
            phoneNumber=u'0123456789'
            )
        self._inquiry_receipt(u'01234012340124')
        builder = get_response_builder(self.request, f_request)
        result = builder.build_response(f_request, self.session, self.now)
        self.assertEqual(result.resultCode, ResultCodeEnum.OtherError.value)
        self.assertEqual(result.replyClass, u'')
        self.assertEqual(result.replyCode, ReplyCodeEnum.SearchKeyError.value)

    def test_payment_later_date(self):
        # 前払後日
        from .models import ResultCodeEnum, ReplyClassEnum, ReplyCodeEnum
        f_request = FamiPortPaymentTicketingRequest(
            storeCode=u'000009',
            mmkNo=u'1',
            ticketingDate=u'20150522003000',
            sequenceNo=u'15052100003',
            playGuideId=u'012340123401234012340123',
            barCodeNo=u'01234012340124',
            customerName=u'カスタマ　太郎',
            phoneNumber=u'0123456789'
            )
        self._inquiry_receipt(u'01234012340124')
        builder = get_response_builder(self.request, f_request)
        result = builder.build_response(f_request, self.session, self.now)
        self.assertEqual(result.resultCode, ResultCodeEnum.OtherError.value)
        self.assertEqual(result.replyClass, u'')
        self.assertEqual(result.replyCode, ReplyCodeEnum.PaymentDueError.value)

    def test_payment_later_date_but_within_moratorium(self):
        # 前払後日
        from .models import ResultCodeEnum, ReplyClassEnum, ReplyCodeEnum
        f_request = FamiPortPaymentTicketingRequest(
            storeCode=u'000009',
            mmkNo=u'1',
            ticketingDate=u'20150522000000',
            sequenceNo=u'15052100003',
            playGuideId=u'012340123401234012340123',
            barCodeNo=u'01234012340124',
            customerName=u'カスタマ　太郎',
            phoneNumber=u'0123456789'
            )
        self._inquiry_receipt(u'01234012340124')
        builder = get_response_builder(self.request, f_request)
        result = builder.build_response(f_request, self.session, self.now)
        self.assertEqual(result.resultCode, ResultCodeEnum.Normal.value)
        self.assertEqual(result.replyClass, ReplyClassEnum.Prepayment.value)
        self.assertEqual(result.replyCode, ReplyCodeEnum.Normal.value)
        self.assertEqual(result.storeCode, u'000009')
        self.assertEqual(result.sequenceNo, u'15052100003')
        self.assertEqual(result.barCodeNo, u'01234012340124')
        self.assertEqual(result.orderId, u'000011112223')
        self.assertEqual(result.playGuideId, u'012340123401234012340123')
        self.assertEqual(result.playGuideName, u'チケットスター')
        self.assertEqual(result.orderTicketNo, u'01234012340124')
        self.assertEqual(result.exchangeTicketNo, u'')
        self.assertEqual(result.ticketingStart, u'20150522000000')
        self.assertEqual(result.ticketingEnd, u'20150523235959')
        self.assertEqual(result.totalAmount, u'00010540')
        self.assertEqual(result.ticketPayment, u'00010000')
        self.assertEqual(result.systemFee, u'00000324')
        self.assertEqual(result.ticketingFee, u'00000216')
        self.assertEqual(result.ticketCountTotal, u'2')
        self.assertEqual(result.ticketCount, u'2')
        self.assertEqual(result.kogyoName, u'7/1公演')
        self.assertEqual(result.koenDate, u'201507011900')

    def test_ticketing_for_paid_order(self):
        # 前払後日の発券
        from .models import ResultCodeEnum, ReplyClassEnum, ReplyCodeEnum
        self.famiport_order_payment.paid_at = datetime(2015, 5, 21, 13, 40, 1)
        f_request = FamiPortPaymentTicketingRequest(
            storeCode=u'000009',
            mmkNo=u'1',
            ticketingDate=u'20150522211234',
            sequenceNo=u'15052100003',
            playGuideId=u'012340123401234012340123',
            barCodeNo=u'01234012340124',
            customerName=u'カスタマ　太郎',
            phoneNumber=u'0123456789'
            )
        self._inquiry_receipt(u'01234012340124')
        builder = get_response_builder(self.request, f_request)
        result = builder.build_response(f_request, self.session, self.now)
        self.assertEqual(result.resultCode, ResultCodeEnum.Normal.value)
        self.assertEqual(result.replyClass, ReplyClassEnum.Paid.value)
        self.assertEqual(result.replyCode, ReplyCodeEnum.Normal.value)
        self.assertEqual(result.storeCode, u'000009')
        self.assertEqual(result.sequenceNo, u'15052100003')
        self.assertEqual(result.barCodeNo, u'01234012340124')
        self.assertEqual(result.orderId, u'000011112223')
        self.assertEqual(result.playGuideId, u'012340123401234012340123')
        self.assertEqual(result.playGuideName, u'チケットスター')
        self.assertEqual(result.orderTicketNo, u'01234012340124')
        self.assertEqual(result.exchangeTicketNo, u'')
        self.assertEqual(result.ticketingStart, u'20150522000000')
        self.assertEqual(result.ticketingEnd, u'20150523235959')
        self.assertEqual(result.totalAmount, u'00010540')
        self.assertEqual(result.ticketPayment, u'00010000')
        self.assertEqual(result.systemFee, u'00000324')
        self.assertEqual(result.ticketingFee, u'00000216')
        self.assertEqual(result.ticketCountTotal, u'2')
        self.assertEqual(result.ticketCount, u'2')
        self.assertEqual(result.kogyoName, u'7/1公演')
        self.assertEqual(result.koenDate, u'201507011900')

    def test_ticketing_for_paid_order_earlier(self):
        # 前払後日の発券
        from .models import ResultCodeEnum, ReplyClassEnum, ReplyCodeEnum

        self.famiport_order_payment.paid_at = datetime(2015, 5, 21, 13, 40, 1)
        f_request = FamiPortPaymentTicketingRequest(
            storeCode=u'000009',
            mmkNo=u'1',
            ticketingDate=u'20150521135001',
            sequenceNo=u'15052100003',
            playGuideId=u'012340123401234012340123',
            barCodeNo=u'01234012340124',
            customerName=u'カスタマ　太郎',
            phoneNumber=u'0123456789'
            )
        self._inquiry_receipt(u'01234012340124')
        builder = get_response_builder(self.request, f_request)
        result = builder.build_response(f_request, self.session, self.now)
        self.assertEqual(result.resultCode, ResultCodeEnum.OtherError.value)
        self.assertEqual(result.replyClass, u'')
        self.assertEqual(result.replyCode, ReplyCodeEnum.TicketingBeforeStartError.value)
        self.assertEqual(result.storeCode, u'000009')
        self.assertEqual(result.sequenceNo, u'15052100003')
        self.assertEqual(result.barCodeNo, u'01234012340124')
        self.assertEqual(result.orderId, u'000011112223')
        self.assertEqual(result.playGuideId, u'')
        self.assertEqual(result.playGuideName, u'')
        self.assertEqual(result.orderTicketNo, None)
        self.assertEqual(result.exchangeTicketNo, None)
        self.assertEqual(result.ticketingStart, None)
        self.assertEqual(result.ticketingEnd, None)
        self.assertEqual(result.totalAmount, None)
        self.assertEqual(result.ticketPayment, None)
        self.assertEqual(result.systemFee, None)
        self.assertEqual(result.ticketingFee, None)
        self.assertEqual(result.ticketCountTotal, None)
        self.assertEqual(result.ticketCount, None)
        self.assertEqual(result.kogyoName, None)
        self.assertEqual(result.koenDate, None)

    def test_payment_only(self):
        # 前払いのみ
        from .models import ResultCodeEnum, ReplyClassEnum, ReplyCodeEnum
        f_request = FamiPortPaymentTicketingRequest(
            storeCode=u'000009',
            mmkNo=u'1',
            ticketingDate=u'20150522134001',
            sequenceNo=u'15052100004',
            playGuideId=u'012340123401234012340123',
            barCodeNo=u'01234012340125',
            customerName=u'カスタマ　太郎',
            phoneNumber=u'0123456789'
            )
        self._inquiry_receipt(u'01234012340125')
        builder = get_response_builder(self.request, f_request)
        result = builder.build_response(f_request, self.session, self.now)
        self.assertEqual(result.resultCode, ResultCodeEnum.Normal.value)
        self.assertEqual(result.replyClass, ReplyClassEnum.PrepaymentOnly.value)
        self.assertEqual(result.replyCode, ReplyCodeEnum.Normal.value)
        self.assertEqual(result.storeCode, u'000009')
        self.assertEqual(result.sequenceNo, u'15052100004')
        self.assertEqual(result.barCodeNo, u'01234012340125')
        self.assertEqual(result.orderId, u'000011112224')
        self.assertEqual(result.playGuideId, u'012340123401234012340123')
        self.assertEqual(result.playGuideName, u'チケットスター')
        self.assertEqual(result.orderTicketNo, u'01234012340125')
        self.assertEqual(result.exchangeTicketNo, u'')
        self.assertEqual(result.ticketingStart, u'')
        self.assertEqual(result.ticketingEnd, u'')
        self.assertEqual(result.totalAmount, u'00010540')
        self.assertEqual(result.ticketPayment, u'00010000')
        self.assertEqual(result.systemFee, u'00000324')
        self.assertEqual(result.ticketingFee, u'00000216')
        self.assertEqual(result.ticketCountTotal, u'2')
        self.assertEqual(result.ticketCount, u'2')
        self.assertEqual(result.kogyoName, u'7/1公演')
        self.assertEqual(result.koenDate, u'201507011900')


class FamiPortPaymentTicketingCompletionBuilderTest(unittest.TestCase, FamiPortResponseBuilderTestBase):
    # 発券完了
    pass
        # self.famiport_payment_ticketing_completion_request = FamiPortPaymentTicketingCompletionRequest(storeCode='000009', mmkNo='1', ticketingDate='20150331184114', sequenceNo='15033100010', requestClass='', \
        #                                                                                               barCodeNo='1000000000000', playGuideId='', orderId='123456789012', totalAmount='1000')

        # 入金発券取消
        # self.famiport_payment_ticketing_cancel_request = FamiPortPaymentTicketingCancelRequest(storeCode='000009', mmkNo='1', ticketingDate='20150401101950', sequenceNo='15040100009', barCodeNo='1000000000000', \
        #                                                                                       playGuideId='', orderId='123456789012', cancelCode='10')

        # 案内
        # famiport_information_service_unavailable_message = FamiPortInformationMessage.create(result_code=InformationResultCodeEnum.ServiceUnavailable.name , message=u'ServiceUnavailable メッセージ')

        # 顧客情報取得
