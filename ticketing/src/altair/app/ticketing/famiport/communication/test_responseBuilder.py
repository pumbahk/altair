# -*- coding: utf-8 -*-
import unittest
from datetime import datetime
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
            FamiPortOrderType,
            FamiPortTicketType,
            FamiPortTicket,
            )
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
            barcode_no=u'01234012340123',
            reserve_number=u'4321043210432',
            exchange_number=u'',
            customer_name=u'チケット　太郎',
            customer_address_1=u'東京都品川区西五反田7-1-9',
            customer_address_2=u'五反田HSビル9F',
            customer_phone_number=u'0123456789',
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
            barcode_no=u'01234012340124',
            reserve_number=u'4321043210433',
            exchange_number=u'',
            customer_name=u'チケット　太郎',
            customer_address_1=u'東京都品川区西五反田7-1-9',
            customer_address_2=u'五反田HSビル9F',
            customer_phone_number=u'0123456789',
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
            barcode_no=u'01234012340125',
            reserve_number=u'4321043210434',
            exchange_number=u'',
            customer_name=u'チケット　太郎',
            customer_address_1=u'東京都品川区西五反田7-1-9',
            customer_address_2=u'五反田HSビル9F',
            customer_phone_number=u'0123456789',
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

    def test_ok(self):
        from .models import ResultCodeEnum, ReplyCodeEnum
        f_request = FamiPortCustomerInformationRequest(
            storeCode=u'000009',
            mmkNo=u'1',
            ticketingDate=u'20150521134001',
            sequenceNo=u'15052100001',
            barCodeNo=u'01234012340123',
            playGuideId=self.famiport_client.code,
            orderId=u'000011112222',
            totalAmount=u'10540'
            )
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
        self.assertEqual(result.barCodeNo, u'01234012340123')
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


class FamiPortPaymentTicketingResponseBuilderTest(unittest.TestCase, FamiPortResponseBuilderTestBase):
    # 入金発券
    def setUp(self):
        FamiPortResponseBuilderTestBase.setUp(self)

    def tearDown(self):
        FamiPortResponseBuilderTestBase.tearDown(self)

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

