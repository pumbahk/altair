# -*- coding: utf-8 -*-
from sqlalchemy.ext.declarative import declarative_base
from unittest import TestCase
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

class FamiPortResponseBuilderTest(TestCase):
    def setUp(self):
        self.config = setUp()
        self.config.include('.')
        self.engine = _setup_db(
            self.config.registry,
            [
                'altair.app.ticketing.famiport.models',
                'altair.app.ticketing.famiport.communication.models',
                ]
            )
        self.session = get_global_db_session(self.config.registry, 'famiport')

        # 予約照会
        # self.famiport_reservation_inquiry_request = FamiPortReservationInquiryRequest(storeCode='000009', ticketingDate='20150325151159', reserveNumber='5300000000001', authNumber='')

        # 入金発券
        # self.famiport_payment_ticketing_request = FamiPortPaymentTicketingRequest(storeCode='000009', mmkNo='1', ticketingDate='20150331172554', sequenceNo='15033100002', playGuideId='', barCodeNo='1000000000000',\
        #                                                                          customerName='pT6fj7ULQklIfOWBKGyQ6g%3d%3d', phoneNumber='rfanmRgUZFRRephCwOsgbg%3d%3d')

        # 発券完了
        # self.famiport_payment_ticketing_completion_request = FamiPortPaymentTicketingCompletionRequest(storeCode='000009', mmkNo='1', ticketingDate='20150331184114', sequenceNo='15033100010', requestClass='', \
        #                                                                                               barCodeNo='1000000000000', playGuideId='', orderId='123456789012', totalAmount='1000')

        # 入金発券取消
        # self.famiport_payment_ticketing_cancel_request = FamiPortPaymentTicketingCancelRequest(storeCode='000009', mmkNo='1', ticketingDate='20150401101950', sequenceNo='15040100009', barCodeNo='1000000000000', \
        #                                                                                       playGuideId='', orderId='123456789012', cancelCode='10')

        # 案内
        # famiport_information_service_unavailable_message = FamiPortInformationMessage.create(result_code=InformationResultCodeEnum.ServiceUnavailable.name , message=u'ServiceUnavailable メッセージ')
        famiport_information_with_information_message = FamiPortInformationMessage.create(result_code=InformationResultCodeEnum.WithInformation.name , message=u'WithInformation メッセージ')

        famiport_information_request_dict = {'infoKubun':'1', 'storeCode':'000009', 'kogyoCode':'', 'kogyoSubCode':'', 'koenCode':'', 'uketsukeCode':'', 'playGuideId':'', 'authCode':'', 'reserveNumber':'4000000000001'}
        self.famiport_information_request = FamiPortRequestFactory.create_request(famiport_information_request_dict, FamiPortRequestType.Information)

        # 顧客情報取得
        self.famiport_customer_information_request = FamiPortCustomerInformationRequest(
            storeCode=u'000009',
            mmkNo=u'1',
            ticketingDate=u'20150331182222',
            sequenceNo=u'15033100004',
            barCodeNo=u'4119000000005',
            playGuideId=u'',
            orderId=u'410900000005',
            totalAmount=u'2200'
            )

    def tearDown(self):
        _teardown_db(self.config.registry)
        tearDown()

    def test_build_ReservationInquiryResponseBuilder(self):
        # 予約照会
        # reservation_inquiry_response_builder = get_response_builder(self.famiport_reservation_inquiry_request)
        # self.check_build_response(reservation_inquiry_response_builder, self.famiport_reservation_inquiry_request)

        # 案内
        request = DummyRequest()
        famiport_information_response_builder = get_response_builder(request, self.famiport_information_request)
        self.check_build_response(famiport_information_response_builder, self.famiport_information_request)

    def check_build_response(self, response_builder, famiport_request):
        famiport_response = response_builder.build_response(famiport_request, self.session)
        self.assertIsNotNone(famiport_response)
