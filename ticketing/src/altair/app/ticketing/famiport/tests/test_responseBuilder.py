# -*- coding: utf-8 -*-

from unittest import TestCase

from ..requests import FamiPortReservationInquiryRequest, FamiPortPaymentTicketingRequest, FamiPortPaymentTicketingCompletionRequest, \
                    FamiPortPaymentTicketingCancelRequest, FamiPortInformationRequest, FamiPortCustomerInformationRequest

from ..api import get_response_builder

class FamiPortResponseBuilderTest(TestCase):
    def setUp(self):
        # 予約照会
        self.famiport_reservation_inquiry_request = FamiPortReservationInquiryRequest(storeCode='000009', ticketingDate='20150325151159', reserveNumber='5300000000001', authNumber='')

        # 入金発券
        self.famiport_payment_ticketing_request = FamiPortPaymentTicketingRequest(storeCode='000009', mmkNo='1', ticketingDate='20150331172554', sequenceNo='15033100002', playGuideId='', barCodeNo='1000000000000',\
                                                                                  customerName='pT6fj7ULQklIfOWBKGyQ6g%3d%3d', phoneNumber='rfanmRgUZFRRephCwOsgbg%3d%3d')

        # 発券完了
        self.famiport_payment_ticketing_completion_request = FamiPortPaymentTicketingCompletionRequest(storeCode='000009', mmkNo='1', ticketingDate='20150331184114', sequenceNo='15033100010', requestClass='', \
                                                                                                       barCodeNo='1000000000000', playGuideId='', orderId='123456789012', totalAmount='1000')

        # 入金発券取消
        self.famiport_payment_ticketing_cancel_request = FamiPortPaymentTicketingCancelRequest(storeCode='000009', mmkNo='1', ticketingDate='20150401101950', sequenceNo='15040100009', barCodeNo='1000000000000', \
                                                                                               playGuideId='', orderId='123456789012', cancelCode='10')

        # 案内
        self.famiport_information_request = FamiPortInformationRequest(infoKubun='Reserve', storeCode='000009', kogyoCode='', kogyoSubCode='', koenCode='', uketsukeCode='', playGuideId='', authCode='', \
                                                                       reserveNumber='4000000000001')

        # 顧客情報取得
        self.famiport_customer_information_request = FamiPortCustomerInformationRequest(storeCode='000009', mmkNo='1', ticketingDate='20150331182222', sequenceNo='15033100004', barCodeNo='4119000000005', \
                                                                                        playGuideId='', orderId='410900000005', totalAmount='2200')

    def test_build_ReservationInquiryResponseBuilder(self):
        reservation_inquiry_response_builder = get_response_builder(self.famiport_reservation_inquiry_request)
        # famiport_reservation_inquiry_response = reservation_inquiry_response_builder.build_response(self.famiport_reservation_inquiry_request)
        self.check_build_response(reservation_inquiry_response_builder, self.famiport_reservation_inquiry_request)


    def check_build_response(self, response_builder, famiport_request):
        famiport_response = response_builder.build_response(famiport_request)
        self.assertTrue(famiport_response)