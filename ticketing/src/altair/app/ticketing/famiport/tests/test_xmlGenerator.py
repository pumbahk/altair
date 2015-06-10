# -*- coding: utf-8 -*-

from unittest import TestCase
from lxml import etree
from altair.app.ticketing.testing import _setup_db, _teardown_db
from ..api import get_xmlResponse_generator


class XmlFamiPortResponseGeneratorTest(TestCase):
    def setUp(self):
        self.session = _setup_db([
            'altair.app.ticketing.famiport.models',
            'altair.app.ticketing.famiport.communication',
            ])
        from ..communication import (
            FamiPortReservationInquiryResponse,
            FamiPortPaymentTicketingResponse,
            FamiPortPaymentTicketingCompletionResponse,
            FamiPortPaymentTicketingCancelResponse,
            FamiPortInformationResponse,
            FamiPortCustomerInformationResponse,
            FamiPortTicketResponse,
            )

        # 予約照会
        # problematic_kogyoName=u'土吉サンプル興行♥♠♦♣⓪㉑㊿♫♬♩'
        regular_kogyoName = u'サンプル興行'
        self.famiport_reservation_inquiry_response = FamiPortReservationInquiryResponse(
            resultCode=u'00',
            replyClass=u'1',
            replyCode=u'00',
            playGuideId=u'00001',
            barCodeNo=u'4110000000006',
            totalAmount=u'00000670',
            ticketPayment=u'00000000',
            systemFee=u'00000500',
            ticketingFee=u'00000170',
            ticketCountTotal=u'1',
            ticketCount=u'1',
            kogyoName=regular_kogyoName,
            koenDate=u'201505011000',
            name=u'test_name',
            nameInput=u'0',
            phoneInput=u'0'
            )
        # 入金発券
        self.famiport_payment_ticketing_response = FamiPortPaymentTicketingResponse(
            resultCode=u'00',
            storeCode=u'099999',
            sequenceNo=u'12345678901',
            barCodeNo=u'4310000000002',
            orderId=u'430000000002',
            replyClass=u'3',
            replyCode=u'00',
            playGuideId=u'00001',
            playGuideName=u'テストプレイガイド名',
            orderTicketNo=u'',
            exchangeTicketNo=u'4310000000002',
            ticketingStart=u'',
            ticketingEnd=u'',
            totalAmount=u'00000200',
            ticketPayment=u'00000000',
            systemFee=u'00000000',
            ticketingFee=u'00000200',
            ticketCountTotal=u'5',
            ticketCount=u'5',
            kogyoName=u'サンプル興行',
            koenDate=u'999999999999',
            tickets=[
                FamiPortTicketResponse(
                    barCodeNo=u'1234567890019',
                    ticketClass=u'1',
                    templateCode=u'TTEVEN0001',
                    ticketData=u'test_ticketData1'
                    ),
                FamiPortTicketResponse(
                    barCodeNo=u'1234567890026',
                    ticketClass=u'1',
                    templateCode=u'TTEVEN0001',
                    ticketData=u'test_ticketData2'
                    ),
                FamiPortTicketResponse(
                    barCodeNo=u'1234567890033',
                    ticketClass=u'1',
                    templateCode=u'TTEVEN0001',
                    ticketData=u'test_ticketData3'
                    ),
                FamiPortTicketResponse(
                    barCodeNo=u'1234567890040',
                    ticketClass=u'1',
                    templateCode=u'TTEVEN0001',
                    ticketData=u'test_ticketData4'
                    ),
                FamiPortTicketResponse(
                    barCodeNo=u'1234567890057',
                    ticketClass=u'1',
                    templateCode=u'TTEVEN0001',
                    ticketData=u'test_ticketData5'
                    ),
                ]
            )
        # tickets = getattr(self.famiport_payment_ticketing_response, "ticket")
        # print "isinstance(tickets, (list, tuple)): ", isinstance(tickets, (list, tuple))

        # 発券完了
        self.famiport_payment_ticketing_completion_response = FamiPortPaymentTicketingCompletionResponse(
            resultCode=u'00',
            storeCode=u'099999',
            sequenceNo=u'12345678901',
            barCodeNo=u'6010000000000',
            orderId=u'123456789012',
            replyCode=u'00'
            )

        # 入金発券取消
        self.famiport_payment_ticketing_cancel_response = FamiPortPaymentTicketingCancelResponse(
            resultCode=u'00',
            storeCode=u'099999',
            sequenceNo=u'12345678901',
            barCodeNo=u'3300000000000',
            orderId=u'123456789012',
            replyCode=u'00'
            )

        # 案内
        self.famiport_information_response = FamiPortInformationResponse(resultCode=u'00', infoKubun='0', infoMessage=u'サンプルインフォメッセージ')

        # 顧客情報取得
        self.famiport_customer_information_response = FamiPortCustomerInformationResponse(
            resultCode=u'00', replyCode='00', name=u'テスト氏名',
            memberId='test_memberId', address1=u'テストアドレス１',
            address2=u'テストアドレス２', identifyNo='1234567890123456',
            )
        self.famiport_customer_information_response.set_encryptKey(self.famiport_payment_ticketing_response.orderId)

    def tearDown(self):
        _teardown_db()

    def test_generate_xmlFamiPortReservationInquiryResponse(self):
        self.check_generate_xmlFamiPortResponse(self.famiport_reservation_inquiry_response)

    def test_generate_xmlFamiPortPaymentTicketingResponse(self):
        self.check_generate_xmlFamiPortResponse(self.famiport_payment_ticketing_response)

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
        root = etree.fromstring(result)
        encrypted_fields = famiport_response.encrypted_fields
        for element in root:
            if element.tag != 'FMIF' \
               and not any(element.tag == element_name for _, element_name in famiport_response._serialized_collection_attrs):  # noqa Skip the root element and tickets
                response_value = getattr(famiport_response, element.tag)
                if isinstance(response_value, (str, unicode)) and response_value != '':  # fromstring() removes empty text element
                    if element.tag not in encrypted_fields:
                        self.assertEqual(element.text, response_value, '<%s> %r (got) != %r (expected)' % (element.tag, element.text, response_value))
                    else:
                        decrypted_text_value = xml_response_generator.famiport_crypt.decrypt(element.text).decode('shift_jis')
                        self.assertEqual(decrypted_text_value, response_value,
                                         '<%s> %r (got) != %r (expected)' % (element.tag, decrypted_text_value, response_value))
