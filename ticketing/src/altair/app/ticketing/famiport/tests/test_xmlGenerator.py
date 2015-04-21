# -*- coding: utf-8 -*-

from unittest import TestCase

from ..api import get_xmlResponse_generator
from ..responses import FamiPortReservationInquiryResponse, FamiPortPaymentTicketingResponse, FamiPortPaymentTicketingCompletionResponse, FamiPortPaymentTicketingCancelResponse, FamiPortInformationResponse, FamiPortCustomerInformationResponse, FamiPortTicket
from ..utils import prettify


class XmlFamiPortResponseGeneratorTest(TestCase):
    def setUp(self):
        # 予約照会
        self.famiport_reservation_inquiry_response = FamiPortReservationInquiryResponse(resultCode='00', replyClass='1', replyCode='00', barCodeNo='4110000000006', totalAmount='00000670', ticketPayment='00000000', systemFee='00000500', ticketingFee='00000170', ticketCountTotal='1', ticketCount='1', kogyoName='test_kogyoNames', koenDate='201505011000', name='test_name', nameInput='0', phoneInput='0')

        # 入金発券
        tickets = [FamiPortTicket(barCodeNo='1234567890019', ticketClass='1', templateCode='TTEVEN0001', ticketData='test_ticketData1'), \
                   FamiPortTicket(barCodeNo='1234567890026', ticketClass='1', templateCode='TTEVEN0001', ticketData='test_ticketData2'), \
                   FamiPortTicket(barCodeNo='1234567890033', ticketClass='1', templateCode='TTEVEN0001', ticketData='test_ticketData3'), \
                   FamiPortTicket(barCodeNo='1234567890040', ticketClass='1', templateCode='TTEVEN0001', ticketData='test_ticketData4'), \
                   FamiPortTicket(barCodeNo='1234567890057', ticketClass='1', templateCode='TTEVEN0001', ticketData='test_ticketData5')]
        self.famiport_payment_ticketing_response = FamiPortPaymentTicketingResponse(resultCode='00', storeCode='099999', sequenceNo='12345678901', barCodeNo='4310000000002', orderId='430000000002', replyClass='3', replyCode='00', playGuideId='00001', playGuideName='test_playGuideName', orderTicketNo='', exchangeTicketNo='4310000000002', ticketingStart='', ticketingEnd='', totalAmount='00000200', ticketPayment='00000000', systemFee='00000000', ticketingFee='00000200', ticketCountTotal='5', ticketCount='5', kogyoName='test_kogyoNames', koenDate='999999999999', ticket=tickets)

        # 発券完了
        self.famiport_payment_ticketing_completion_response = FamiPortPaymentTicketingCompletionResponse(resultCode='00', storeCode='099999', sequenceNo='12345678901', barCodeNo='6010000000000', orderId='123456789012', replyCode='00')

        # 入金発券取消
        self.famiport_payment_ticketing_cancel_response = FamiPortPaymentTicketingCancelResponse(resultCode='00', storeCode='099999', sequenceNo='12345678901', barCodeNo='3300000000000', orderId='123456789012', replyCode='00')

        # 案内
        self.famiport_information_response = FamiPortInformationResponse(resultCode='00', infoKubun='0', infoMessage='test_infoMessage')

        # 顧客情報取得
        self.famiport_customer_information_response = FamiPortCustomerInformationResponse(resultCode='00', replyCode='00', name='test_name', memberId='test_memberId', address1='test_address1', address2='test_address2', identifyNo='1234567890123456')

    def test_generate_xmlFamiPortReservationInquiryResponse(self):
        self.check_generate_xmlFamiPortResponse(self.famiport_reservation_inquiry_response)

    def test_generate_xmlFamiPortPaymentTicketingCompletionResponse(self):
        self.check_generate_xmlFamiPortResponse(self.famiport_payment_ticketing_completion_response)

    def test_generate_xmlFamiPortPaymentTicketingCancelResponse(self):
        self.check_generate_xmlFamiPortResponse(self.famiport_payment_ticketing_cancel_response)

    def test_generate_xmlFamiPortInformationResponse(self):
        self.check_generate_xmlFamiPortResponse(self.famiport_information_response)

    def test_generate_xmlFamiPortCustomerInformationResponse(self):
        self.check_generate_xmlFamiPortResponse(self.famiport_customer_information_response)

    def check_generate_xmlFamiPortResponse(self, famiport_response):
         xml_response_generator = get_xmlResponse_generator(famiport_response)
         result = xml_response_generator.generate_xmlResponse(famiport_response)
         print result
         # print prettify(result)
         self.assertTrue(result is None) # resultのprintを表示するためにAssertionErrorが起こるようにしておく