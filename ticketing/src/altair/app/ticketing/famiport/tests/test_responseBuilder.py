# -*- coding: utf-8 -*-
from altair.app.ticketing.testing import _setup_db
from sqlalchemy.ext.declarative import declarative_base
from unittest import TestCase
import sqlahelper

from ..requests import FamiPortReservationInquiryRequest, FamiPortPaymentTicketingRequest, FamiPortPaymentTicketingCompletionRequest, \
                    FamiPortPaymentTicketingCancelRequest, FamiPortInformationRequest, FamiPortCustomerInformationRequest
from ..api import get_response_builder
from ..builders import FamiPortRequestFactory
from ..utils import FamiPortRequestType, InformationResultCodeEnum
from ..models import FamiPortInformationMessage

class FamiPortResponseBuilderTest(TestCase):
    def setUp(self):
        self.session = _setup_db(modules=["altair.app.ticketing.famiport.models"])
        sqlahelper.set_base(declarative_base(self.session.bind))

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
        # famiport_information_service_unavailable_message.save()
        famiport_information_with_information_message = FamiPortInformationMessage.create(result_code=InformationResultCodeEnum.WithInformation.name , message=u'WithInformation メッセージ')
        famiport_information_with_information_message.save()

        famiport_information_request_dict = {'infoKubun':'1', 'storeCode':'000009', 'kogyoCode':'', 'kogyoSubCode':'', 'koenCode':'', 'uketsukeCode':'', 'playGuideId':'', 'authCode':'', 'reserveNumber':'4000000000001'}
        self.famiport_information_request = FamiPortRequestFactory.create_request(famiport_information_request_dict, FamiPortRequestType.Information)

        # 顧客情報取得
        famiport_customer_information_request_dict = {'storeCode':'000009', 'mmkNo':'1', 'ticketingDate':'20150331182222', 'sequenceNo':'15033100004', 'barCodeNo':'4119000000005', 'playGuideId':'', \
                                                      'orderId':'410900000005', 'totalAmount':'2200'}
        self.famiport_customer_information_request = FamiPortCustomerInformationRequest(famiport_customer_information_request_dict, FamiPortRequestType.CustomerInformation)

    def test_build_ReservationInquiryResponseBuilder(self):
        # 予約照会
        # reservation_inquiry_response_builder = get_response_builder(self.famiport_reservation_inquiry_request)
        # self.check_build_response(reservation_inquiry_response_builder, self.famiport_reservation_inquiry_request)

        # 案内
        famiport_information_response_builder = get_response_builder(self.famiport_information_request)
        self.check_build_response(famiport_information_response_builder, self.famiport_information_request)

    def check_build_response(self, response_builder, famiport_request):
        famiport_response = response_builder.build_response(famiport_request)
        print famiport_response
        self.assertTrue(famiport_response is None) # famiport_responseのprintを表示するためにAssertionErrorが起こるようにしておく