# -*- coding: utf-8 -*-

from sqlalchemy.exc import DBAPIError
from zope.interface import implementer
from .interfaces import IFamiPortResponseBuilderFactory, IFamiPortResponseBuilder, IXmlFamiPortResponseGenerator
from .models import FamiPortOrder, FamiPortInformationMessage
from .utils import FamiPortRequestType, FamiPortCrypt, ResultCodeEnum, ReplyClassEnum, ReplyCodeEnum, InformationResultCodeEnum, InfoKubunEnum
from .requests import FamiPortReservationInquiryRequest, FamiPortPaymentTicketingRequest, FamiPortPaymentTicketingCompletionRequest, \
                    FamiPortPaymentTicketingCancelRequest, FamiPortInformationRequest, FamiPortCustomerInformationRequest
from .responses import FamiPortReservationInquiryResponse, FamiPortPaymentTicketingResponse, FamiPortPaymentTicketingCompletionResponse, \
                    FamiPortPaymentTicketingCancelResponse, FamiPortInformationResponse, FamiPortCustomerInformationResponse

from lxml import etree
from inspect import ismethod

import logging
import hashlib
import base64

logger = logging.getLogger(__name__)

class FamiPortRequestFactory(object):
    @classmethod
    def create_request(self, famiport_request_dict, request_type):
        if not famiport_request_dict or not request_type:
            return None

        famiport_request = None
        if request_type == FamiPortRequestType.ReservationInquiry:
            famiport_request = FamiPortReservationInquiryRequest()
        elif request_type == FamiPortRequestType.PaymentTicketing:
            famiport_request = FamiPortPaymentTicketingRequest()
        elif request_type == FamiPortRequestType.PaymentTicketingCompletion:
            famiport_request =  FamiPortPaymentTicketingCompletionRequest()
        elif request_type == FamiPortRequestType.PaymentTicketingCancel:
            famiport_request = FamiPortPaymentTicketingCancelRequest()
        elif request_type == FamiPortRequestType.Information:
            famiport_request = FamiPortInformationRequest()
        elif request_type == FamiPortRequestType.CustomerInformation:
            famiport_request = FamiPortCustomerInformationRequest()
        else:
            pass
        famiport_request.request_type = request_type

        for key, value in famiport_request_dict.items():
            setattr(famiport_request, key, value)

        return famiport_request

@implementer(IFamiPortResponseBuilderFactory)
class FamiPortResponseBuilderFactory(object):
    def __init__(self, *args, **kwargs):
        pass

    def __call__(self, famiport_request):
        request_type = famiport_request.request_type
        if request_type == FamiPortRequestType.ReservationInquiry:
            return  FamiPortReservationInquiryResponseBuilder()
        elif request_type == FamiPortRequestType.PaymentTicketing:
            return FamiPortPaymentTicketingResponseBuilder()
        elif request_type == FamiPortRequestType.PaymentTicketingCompletion:
            return FamiPortPaymentTicketingCompletionResponseBuilder()
        elif request_type == FamiPortRequestType.PaymentTicketingCancel:
            return FamiPortPaymentTicketingCancelResponseBuilder()
        elif request_type == FamiPortRequestType.Information:
            return FamiPortInformationResponseBuilder()
        elif request_type == FamiPortRequestType.CustomerInformation:
            return FamiPortCustomerInformationResponseBuilder()
        else:
            pass

@implementer(IFamiPortResponseBuilder)
class FamiPortResponseBuilder(object):
    def __init__(self, *args, **kwargs):
        pass

    def build_response(self, famiport_request=None):
        pass

class FamiPortReservationInquiryResponseBuilder(FamiPortResponseBuilder):
    def build_response(self, famiport_reservation_inquiry_request=None):
        reserveNumber = famiport_reservation_inquiry_request.reserveNumber
        famiport_order = FamiPortOrder.get_by_reserveNumber(reserveNumber)
        if famiport_order is not None:
            resultCode = ResultCodeEnum.Normal
            replyCode = ReplyCodeEnum.Normal

        replyClass = ReplyClassEnum.CashOnDelivery # TODO Change the value depending on the type

        playGuideId, barCodeNo, totalAmount, ticketPayment, systemFee, ticketingFee, ticketCountTotal, ticketCount, kogyoName, koenDate, name, nameInput, phoneInput = \
            None, None, None, None, None, None, None, None, None, None, None, None, None
        if replyCode == ReplyCodeEnum.Normal:
            playGuideId = ''
            barCodeNo = famiport_order.barCodeNo
            totalAmount = famiport_order.totalAmount
            ticketPayment = famiport_order.ticketPayment
            systemFee = famiport_order.systemFee
            ticketingFee = famiport_order.ticketingFee
            ticketCountTotal = famiport_order.ticketCountTotal
            ticketCount = famiport_order.ticketCount
            kogyoName = '' # TODO Set the values accordingly
            koenDate = '' # TODO Set the values accordingly
            name = famiport_order.name

        nameInput = 0 # 不要（画面表示なし）
        phoneInput = 0 # 不要（画面表示なし）

        famiport_reservation_inquiry_response = FamiPortReservationInquiryResponse(resultCode=resultCode, replyClass=replyClass, replyCode=replyCode, \
                                                                                   playGuideId=playGuideId, barCodeNo=barCodeNo, totalAmount=totalAmount, ticketPayment=ticketPayment, systemFee=systemFee, \
                                                                                   ticketingFee=ticketingFee, ticketCountTotal=ticketCountTotal, ticketCount=ticketCount, kogyoName=kogyoName, koenDate=koenDate, \
                                                                                   name=name, nameInput=nameInput, phoneInput=phoneInput)
        return famiport_reservation_inquiry_response

class FamiPortPaymentTicketingResponseBuilder(FamiPortResponseBuilder):
    def build_response(self, famiport_payment_ticketing_request=None):
        resultCode = ResultCodeEnum.Normal
        barCodeNo = famiport_payment_ticketing_request.barCodeNo
        storeCode = famiport_payment_ticketing_request.storeCode
        sequenceNo = famiport_payment_ticketing_request.sequenceNo
        try:
            famiport_order = FamiPortOrder.get_from_barCodeNo(barCodeNo)
        except DBAPIError:
            logger.error("DBAPIError has occurred at FamiPortPaymentTicketingResponseBuilder.build_response(). barCodeNo: " + barCodeNo + ", storeCode: " + storeCode + ", sequenceNo: " + sequenceNo)

        orderId, replyClass, playGuideId, playGuideName, orderTicketNo, exchangeTicketNo, ticketingStart, ticketingEnd = None, None, None, None, None, None, None, None
        totalAmount, ticketPayment, systemFee, ticketingFee, ticketingCountTotal, ticketCount, kogyoName, koenDate, ticket = None, None, None, None, None, None, None, None, None
        if famiport_order is not None:
            orderId = famiport_order.orderId
            replyClass = ReplyClassEnum.CashOnDelivery # TODO Change the value depending on famiport_order's pdmp status
            replyCode = ReplyCodeEnum.Normal # TODO Change the value depending on famiport_order's status
            playGuideId = ''
            playGuideName = ''
            if replyClass == ReplyClassEnum.CashOnDelivery:
                orderTicketNo = barCodeNo
            elif replyClass == ReplyClassEnum.Prepayment:
                orderTicketNo = barCodeNo
                exchangeTicketNo = famiport_order.exchangeTicketNo
                ticketingStart = famiport_order.ticketingStart
                ticketingEnd = famiport_order.ticketingEnd
            elif replyClass == ReplyClassEnum.Paid:
                exchangeTicketNo = famiport_order.exchangeTicketNo
            elif replyClass == ReplyClassEnum.PrepaymentOnly:
                 orderTicketNo = barCodeNo
            else:
                pass
            totalAmount = famiport_order.totalAmount
            ticketPayment = famiport_order.ticketPayment
            systemFee = famiport_order.systemFee
            ticketingFee = famiport_order.ticketingFee
            ticketingCountTotal = famiport_order.ticketingCountTotal
            ticketCount = famiport_order.ticketCount
            kogyoName = u'' # TODO Get from famiport_order -> order -> event.title
            koenDate = u''# TODO Get from famiport_order -> order -> performance.start_on as YYYYMMDDhhmm
            ticket = famiport_order.ticket
        else:
            resultCode = ResultCodeEnum.OtherError
            replyCode = ReplyCodeEnum.OtherError

        famiport_payment_ticketing_response = FamiPortPaymentTicketingResponse(resultCode=resultCode, storeCode=storeCode, sequenceNo=sequenceNo, barCodeNo=barCodeNo, orderId=orderId, replyClass=replyClass, \
                                                                               replyCode=replyCode, playGuideId=playGuideId, playGuideName=playGuideName, orderTicketNo=orderTicketNo, exchangeTicketNo=exchangeTicketNo,\
                                                                               ticketingStart=ticketingStart, ticketingEnd=ticketingEnd, totalAmount=totalAmount, ticketPayment=ticketPayment, systemFee=systemFee,\
                                                                               ticketingFee=ticketingFee, ticketCountTotal=ticketingCountTotal, ticketCount=ticketCount, kogyoName=kogyoName, koenDate=koenDate, \
                                                                               ticket=ticket)
        return famiport_payment_ticketing_response

class FamiPortPaymentTicketingCompletionResponseBuilder(FamiPortResponseBuilder):
    def build_response(self, famiport_payment_ticketing_completion_request=None):
        resultCode = ResultCodeEnum.Normal
        storeCode = famiport_payment_ticketing_completion_request.storeCode
        sequenceNo = famiport_payment_ticketing_completion_request.sequenceNo
        barCodeNo = famiport_payment_ticketing_completion_request.barCodeNo

        try:
            famiport_order = FamiPortOrder.get_from_barCodeNo(barCodeNo)
        except DBAPIError:
            logger.error("DBAPIError has occurred at FamiPortPaymentTicketingCancelResponseBuilder.build_response(). barCodeNo: " + barCodeNo + ", storeCode: " + storeCode + ", sequenceNo: " + sequenceNo)

        orderId, replyCode = None, None
        if famiport_order is not None:
            orderId = famiport_order.orderId
            replyCode = ReplyCodeEnum.Normal
        else:
            resultCode = ResultCodeEnum.OtherError
            replyCode = ReplyCodeEnum.OtherError

        famiport_payment_ticketing_completion_response = FamiPortPaymentTicketingCompletionResponse(resultCode=resultCode, storeCode=storeCode, sequenceNo=sequenceNo, barCodeNo=barCodeNo, \
                                                                                                    orderId=orderId, replyCode=replyCode)
        return famiport_payment_ticketing_completion_response

class FamiPortPaymentTicketingCancelResponseBuilder(FamiPortResponseBuilder):
    def build_response(self, famiport_payment_ticketing_cancel_request=None):
        resultCode = ResultCodeEnum.Normal
        storeCode = famiport_payment_ticketing_cancel_request.storeCode
        mmkNo = famiport_payment_ticketing_cancel_request.mmkNo
        ticketingDate = famiport_payment_ticketing_cancel_request.ticketingDate
        sequenceNo = famiport_payment_ticketing_cancel_request.sequenceNo
        barCodeNo = famiport_payment_ticketing_cancel_request.barCodeNo

        try:
            famiport_order = FamiPortOrder.get_from_barCodeNo(barCodeNo)
        except DBAPIError:
            logger.error("DBAPIError has occurred at FamiPortPaymentTicketingCancelResponseBuilder.build_response(). " + \
                         "店舗コード: " + storeCode + ", 発券Famiポート番号: " +  mmkNo + ", 利用日時: ", ticketingDate + ", 処理通番: " + sequenceNo + ", 支払番号: " + barCodeNo)

        orderId, replyCode = None, None
        if famiport_order is not None:
            orderId = famiport_order.orderId
            replyCode = ReplyCodeEnum.Normal
        else:
            resultCode = ResultCodeEnum.OtherError
            replyCode = ReplyCodeEnum.OtherError

        famiport_payment_ticketing_cancel_response = FamiPortPaymentTicketingCancelResponse(resultCode=resultCode, storeCode=storeCode, sequenceNo=sequenceNo, barCodeNo=barCodeNo, orderId=orderId, replyCode=replyCode)
        return famiport_payment_ticketing_cancel_response

class FamiPortInformationResponseBuilder(FamiPortResponseBuilder):
    def build_response(self, famiport_information_request=None):
        """
        デフォルトは「案内なし(正常)」
        FamiPortInformationMessageにWithInformationに対応するmessageがあれば「案内あり(正常)」としてメッセージを表示する。
        FamiPortInformationMessageにServiceUnavailableに対応するmessageがあれば「サービス不可時案内」としてメッセージを表示する。
        途中でエラーが起こった場合は「その他エラー」としてメッセージを表示する。

        :param famiport_information_request:
        :return: FamiPortInformationResponse
        """

        resultCode = InformationResultCodeEnum.NoInformation # デフォルトは案内なし(正常)
        infoKubun = famiport_information_request.infoKubun
        storeCode = famiport_information_request.storeCode
        if infoKubun == InfoKubunEnum.Reserved:
            reserveNumber = famiport_information_request.reserveNumber
            logger.info("Processing famiport information request from store: " + storeCode + " with reserveNumber: " + reserveNumber)

        infoMessage = None
        try:
            infoMessage = FamiPortInformationMessage.get_message(InformationResultCodeEnum.ServiceUnavailable)
        except DBAPIError:
            resultCode == InformationResultCodeEnum.OtherError
            infoMessage = u'エラーが起こりました。'
            return FamiPortInformationResponse(resultCode=resultCode, infoKubun=infoKubun, infoMessage=infoMessage)
        if infoMessage != None: # サービス不可時案内
            resultCode = InformationResultCodeEnum.ServiceUnavailable
            return FamiPortInformationResponse(resultCode=resultCode, infoKubun=infoKubun, infoMessage=infoMessage)

        try:
            infoMessage = FamiPortInformationMessage.get_message(InformationResultCodeEnum.WithInformation)
        except DBAPIError:
            resultCode == InformationResultCodeEnum.OtherError
            infoMessage = u'エラーが起こりました。'
            return FamiPortInformationResponse(resultCode=resultCode, infoKubun=infoKubun, infoMessage=infoMessage)
        if infoMessage != None: # 文言の設定あり
            resultCode = InformationResultCodeEnum.WithInformation
            return FamiPortInformationResponse(resultCode=resultCode, infoKubun=infoKubun, infoMessage=infoMessage)

        return FamiPortInformationResponse(resultCode=resultCode, infoKubun=infoKubun, infoMessage=None) # 案内なし(正常)

class FamiPortCustomerInformationResponseBuilder(FamiPortResponseBuilder):
    def build_response(self, famiport_customer_information_request=None):
        orderId = famiport_customer_information_request.orderId
        # TODO Get name, memberId, address from DB with orderId
        resultCode, replyCode = None, None
        if orderId is not None:
            resultCode = ResultCodeEnum.Normal
            replyCode = ReplyCodeEnum.Normal
        else:
            resultCode = ResultCodeEnum.OtherError
            replyCode = ReplyCodeEnum.CustomerNamePrintInformationError
        name, memberId, address1, address2, identifyNo = None, None, None, None, None
        if replyCode == ReplyCodeEnum.Normal:
            # TODO Set the real value for these
            name = 'テスト名字' + '　' + 'テスト名前'
            memberId =  '123abc'
            address1 = '東京都品川区西五反田1-2-3'
            address2 = 'HSビル 9F'
            identifyNo = ''
        famiport_customer_information_response = FamiPortCustomerInformationResponse(resultCode=resultCode, replyCode=replyCode, name=name, memberId=memberId, address1=address1, address2=address2, identifyNo=identifyNo)
        return famiport_customer_information_response

""" Commenting out since seems not necessary at this point.
@implementer(IXmlFamiPortResponseGeneratorFactory)
class XmlFamiPortResponseGeneratorFactory(object):
    def __init__(self, *args, **kwargs):
        pass

    def __call__(self, famiport_response):
        return XmlFamiPortResponseGenerator()
"""

@implementer(IXmlFamiPortResponseGenerator)
class XmlFamiPortResponseGenerator(object):
    def __init__(self, famiport_response):
        encrypt_key_item = famiport_response.encrypt_key
        if encrypt_key_item:
            hash = hashlib.md5()
            hash.update(encrypt_key_item)
            str_digest = hash.hexdigest()
            key = bytes(str_digest)
            self.famiport_crypt = FamiPortCrypt(base64.urlsafe_b64encode(str_digest))

    def generate_xmlResponse(self, famiport_response, root_name = "FMIF"):
        """Generate XML text of famiport_response with encrypt_fields encrypted.
        Assume filed name in famiport_response is same as tag name in XML.
        List fields in famiport_response are repeated with same tag name in XML.

        :param famiport_response: FamiPortResponse object to generate XMl from.
        :param encrypt_fields: List of field names to encrypt.
        :return: Shift-JIS encoded string of generated XML
        """

        root = etree.Element(root_name)
        doc_root = self._build_xmlTree(root, famiport_response)
        return etree.tostring(doc_root, encoding='shift_jis', xml_declaration=True, pretty_print=True)
        # elementTree = ElementTree(doc_root)
        # bytesIO = BytesIO()
        # elementTree.write(bytesIO, encoding='Shift_JIS', xml_declaration=True, pretty_print=True)
        # xml_response = bytesIO.getvalue()
        # bytesIO.close()
        # return xml_response

    def _build_xmlTree(self, root, object):
        """
        Build XML tree from object.
        :param root: root of XML tree
        :param object: object to build XML tree from
        :return: root of the XML tree built
        """

        if object is None:
            return root

        attribute_names = object.__slots__ # Get attribute names of the object
        # Create an element for each attribute_name with element.text=attribute_value and put under root.
        for attribute_name in attribute_names:
            attribute_value = getattr(object, attribute_name)
            if attribute_value is not None:
                if isinstance(attribute_value, (list, tuple)): # In case of list or tuple attribute such as FamiPortPaymentTicketingResponse.ticket
                    for value in attribute_value:
                        element = etree.SubElement(root, attribute_name)
                        attr_names = [attribute for attribute in dir(value) if not ismethod(attribute) and not attribute.startswith("_")]
                        for attr_name in attr_names:
                            sub_element = etree.SubElement(element, attr_name)
                            attr_value = getattr(value, attr_name)
                            if attr_value is not None:
                                # TODO Take care of problematic chars in UTF-8 to SJIS conversion
                                sub_element.text = attr_value if attr_name not in object.encrypt_fields else self.famiport_crypt.encrypt(attr_value.encode('shift_jis'))
                                """
                                if isinstance(attr_value, unicode):
                                    sjis_attr_value = attr_value.encode('shift_jis')
                                    print "sjis_attr_value: ", sjis_attr_value
                                    sub_element.text = sjis_attr_value
                                else:
                                    sub_element.text = attr_value
                                """
                else:
                    element = etree.SubElement(root, attribute_name)
                    # TODO Take care of problematic chars in UTF-8 to SJIS conversion
                    # if isinstance(attribute_value, unicode):
                    #    attribute_value = attribute_value.encode('shift_jis') # Encode for encrypt
                    # print '(attribute_name, attribute_value)', (attribute_name, attribute_value)
                    # element.text = attribute_value.decode('shift_jis') if attribute_name not in object.encrypt_fields else self.famiport_crypt.encrypt(attribute_value)
                    element.text = attribute_value if attribute_name not in object.encrypt_fields else self.famiport_crypt.encrypt(attribute_value.encode('shift_jis'))
                    """
                    if isinstance(attribute_value, unicode):
                        sjis_attribute_value = attribute_value.encode('shift-jis')
                        element.text = sjis_attribute_value if attribute_name not in object.encrypt_fields else self.famiport_crypt.encrypt(sjis_attribute_value)
                    else:
                        element.text = attribute_value if attribute_name not in object.encrypt_fields else self.famiport_crypt.encrypt(attribute_value)
                    """

        return root
