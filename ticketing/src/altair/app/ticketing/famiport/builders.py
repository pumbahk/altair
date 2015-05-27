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
        storeCode = famiport_reservation_inquiry_request.storeCode
        ticketingDate = famiport_reservation_inquiry_request.ticketingDate
        reserveNumber = famiport_reservation_inquiry_request.reserveNumber
        authNumber = famiport_reservation_inquiry_request.authNumber

        logger.info("Processing famiport reservation inquiry request. " + \
                    "店舗コード: " + storeCode +  ", 利用日時: " + ticketingDate + ", 予約番号: " + reserveNumber)

        famiport_order = None
        try:
            famiport_order = FamiPortOrder.get_by_reserveNumber(reserveNumber, authNumber)
        except DBAPIError:
            logger.error("DBAPIError has occurred at FamiPortReservationInquiryResponseBuilder.build_response(). " + \
                         "店舗コード: " + storeCode +  ", 利用日時: " + ticketingDate + ", 予約番号: " + reserveNumber)

        if famiport_order is not None:
            resultCode = ResultCodeEnum.Normal
            replyCode = ReplyCodeEnum.Normal
        else:
            resultCode = ResultCodeEnum.OtherError
            replyCode = ReplyCodeEnum.SearchKeyError

        replyClass = ReplyClassEnum.CashOnDelivery # TODO Change the value depending on the type

        playGuideId, barCodeNo, totalAmount, ticketPayment, systemFee, ticketingFee, ticketCountTotal, ticketCount, kogyoName, koenDate, name, nameInput, phoneInput = \
            None, None, None, None, None, None, None, None, None, None, None, None, None
        if replyCode == ReplyCodeEnum.Normal:
            playGuideId = famiport_order.playguide_id
            barCodeNo = famiport_order.barcode_no
            totalAmount = str(famiport_order.total_amount)
            ticketPayment = str(famiport_order.ticket_payment)
            systemFee = str(famiport_order.system_fee)
            ticketingFee = str(famiport_order.ticketing_fee)
            ticketCountTotal = str(famiport_order.ticket_total_count)
            ticketCount = str(famiport_order.ticket_count)
            kogyoName = famiport_order.kogyo_name
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
        mmkNo = famiport_payment_ticketing_request.mmkNo
        ticketingDate = famiport_payment_ticketing_request.ticketingDate
        sequenceNo = famiport_payment_ticketing_request.sequenceNo

        logger.info("Processing famiport payment ticketing request. " + \
                    "店舗コード: " + storeCode + ", 発券Famiポート番号: " +  mmkNo + ", 利用日時: ", ticketingDate + ", 処理通番: " + sequenceNo + ", 支払番号: " + barCodeNo)

        famiport_order = None
        try:
            famiport_order = FamiPortOrder.get_by_barCodeNo(barCodeNo)
        except DBAPIError:
            logger.error("DBAPIError has occurred at FamiPortPaymentTicketingResponseBuilder.build_response(). " + \
                         "店舗コード: " + storeCode + ", 発券Famiポート番号: " +  mmkNo + ", 利用日時: ", ticketingDate + ", 処理通番: " + sequenceNo + ", 支払番号: " + barCodeNo)

        orderId, replyClass, playGuideId, playGuideName, orderTicketNo, exchangeTicketNo, ticketingStart, ticketingEnd = None, None, None, None, None, None, None, None
        totalAmount, ticketPayment, systemFee, ticketingFee, ticketingCountTotal, ticketCount, kogyoName, koenDate, ticket = None, None, None, None, None, None, None, None, None
        if famiport_order is not None:
            orderId = famiport_order.famiport_order_identifier
            replyClass = ReplyClassEnum.CashOnDelivery # TODO Change the value depending on famiport_order's pdmp status
            replyCode = ReplyCodeEnum.Normal # TODO Change the value depending on famiport_order's status
            playGuideId = famiport_order.playguide_id
            playGuideName = famiport_order.playguide_name
            if replyClass == ReplyClassEnum.CashOnDelivery:
                orderTicketNo = barCodeNo
            elif replyClass == ReplyClassEnum.Prepayment:
                orderTicketNo = barCodeNo
                exchangeTicketNo = famiport_order.exchangeTicketNo
                ticketingStart = famiport_order.ticketing_start
                ticketingEnd = famiport_order.ticketing_end
            elif replyClass == ReplyClassEnum.Paid:
                exchangeTicketNo = famiport_order.exchangeTicketNo
            elif replyClass == ReplyClassEnum.PrepaymentOnly:
                 orderTicketNo = barCodeNo
            else:
                pass
            totalAmount = str(famiport_order.total_amount)
            ticketPayment = str(famiport_order.ticket_payment)
            systemFee = str(famiport_order.system_fee)
            ticketingFee = str(famiport_order.ticketing_fee)
            ticketingCountTotal = str(famiport_order.ticket_total_count)
            ticketCount = str(famiport_order.ticket_count)
            kogyoName = famiport_order.kogyo_name
            koenDate = famiport_order.koen_date.strftime("%Y%m%d%H%M")
            ticket = famiport_order.famiport_tickets
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
        mmkNo = famiport_payment_ticketing_completion_request.mmkNo
        ticketingDate = famiport_payment_ticketing_completion_request.ticketingDate
        sequenceNo = famiport_payment_ticketing_completion_request.sequenceNo
        barCodeNo = famiport_payment_ticketing_completion_request.barCodeNo
        orderId = famiport_payment_ticketing_completion_request.orderId

        famiport_order = None
        try:
            famiport_order = FamiPortOrder.get_by_barCodeNo(barCodeNo)
        except DBAPIError:
            replyCode = ReplyCodeEnum.OtherError
            logger.error("DBAPIError has occurred at FamiPortPaymentTicketingCancelResponseBuilder.build_response(). " + \
                         "店舗コード: " + storeCode + ", 発券Famiポート番号: " +  mmkNo + ", 利用日時: ", ticketingDate + ", 処理通番: " + sequenceNo + ", 支払番号: " + barCodeNo + ", 注文ID: " + orderId)

        replyCode = None
        if famiport_order is not None:
            replyCode = ReplyCodeEnum.Normal
        else:
            resultCode = ResultCodeEnum.OtherError
            replyCode = ReplyCodeEnum.SearchKeyError

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

        famiport_order = None
        try:
            famiport_order = FamiPortOrder.get_by_barCodeNo(barCodeNo)
        except DBAPIError:
            logger.error("DBAPIError has occurred at FamiPortPaymentTicketingCancelResponseBuilder.build_response(). " + \
                         "店舗コード: " + storeCode + ", 発券Famiポート番号: " +  mmkNo + ", 利用日時: ", ticketingDate + ", 処理通番: " + sequenceNo + ", 支払番号: " + barCodeNo)

        orderId, replyCode = None, None
        if famiport_order is not None:
            orderId = famiport_order.famiport_order_identifier
            replyCode = ReplyCodeEnum.Normal # TODO Change the value depending on famiport_order's status
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
        elif infoKubun == InfoKubunEnum.DirectSales:
            kogyoCode = famiport_information_request.kogyoCode
            kogyoSubCode = famiport_information_request.kogyoSubCode
            koenCode = famiport_information_request.koenCode
            uketsukeCode = famiport_information_request.uketsukeCode
        else:
            pass

        infoMessage = None
        try:
            infoMessage = FamiPortInformationMessage.get_message(InformationResultCodeEnum.ServiceUnavailable)
        except DBAPIError:
            logger.error("DBAPIError has occurred at FamiPortPaymentTicketingCancelResponseBuilder.build_response(). 店舗コード: " + storeCode)
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
        storeCode = famiport_customer_information_request.storeCode
        mmkNo = famiport_customer_information_request.mmkNo
        ticketingDate = famiport_customer_information_request.ticketingDate
        sequenceNo = famiport_customer_information_request.sequenceNo
        barCodeNo = famiport_customer_information_request.barCodeNo
        orderId = famiport_customer_information_request.orderId

        famiport_order = None
        try:
            famiport_order = FamiPortOrder.get_by_barCodeNo(barCodeNo)
        except DBAPIError:
            logger.error("DBAPIError has occurred at FamiPortPaymentTicketingCancelResponseBuilder.build_response(). " + \
                         "店舗コード: " + storeCode + ", 発券Famiポート番号: " +  mmkNo + ", 利用日時: ", ticketingDate + ", 処理通番: " + sequenceNo + ", 支払番号: " + barCodeNo + ", 注文ID: " + orderId)

        resultCode, replyCode = None, None
        if famiport_order is not None:
            resultCode = ResultCodeEnum.Normal
            replyCode = ReplyCodeEnum.Normal
        else:
            resultCode = ResultCodeEnum.OtherError
            replyCode = ReplyCodeEnum.CustomerNamePrintInformationError

        name, memberId, address1, address2, identifyNo = None, None, None, None, None
        if replyCode == ReplyCodeEnum.Normal:
            name = famiport_order.name
            memberId =  famiport_order.memberId
            address1 = famiport_order.address1
            address2 = famiport_order.address2
            identifyNo = famiport_order.identifyNo

        famiport_customer_information_respose = FamiPortCustomerInformationResponse(resultCode=resultCode, replyCode=replyCode, name=name, memberId=memberId, address1=address1, address2=address2, identifyNo=identifyNo)
        famiport_customer_information_respose.set_encryptKey(orderId)
        return famiport_customer_information_respose

@implementer(IXmlFamiPortResponseGenerator)
class XmlFamiPortResponseGenerator(object):
    def __init__(self, famiport_response):
        if famiport_response.encrypt_key:
            hash = hashlib.md5()
            hash.update(famiport_response.encrypt_key)
            str_digest = hash.hexdigest()
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
                else:
                    element = etree.SubElement(root, attribute_name)
                    # TODO Take care of problematic chars in UTF-8 to SJIS conversion
                    element.text = attribute_value if attribute_name not in object.encrypt_fields else self.famiport_crypt.encrypt(attribute_value.encode('shift_jis'))
        return root
