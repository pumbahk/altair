# -*- coding: utf-8 -*-
import logging
import hashlib
import base64
import datetime
from lxml import etree
from sqlalchemy.exc import DBAPIError
from zope.interface import implementer
from .exc import FamiPortRequestTypeError
from .utils import FamiPortCrypt
from .models import (
    FamiPortOrder,
    FamiPortInformationMessage,
    )
from .interfaces import (
    IFamiPortResponseBuilderFactory,
    IFamiPortResponseBuilder,
    IXmlFamiPortResponseGenerator,
    )
from .communication import (
    FamiPortRequestType,
    ResultCodeEnum,
    ReplyClassEnum,
    ReplyCodeEnum,
    InformationResultCodeEnum,
    InfoKubunEnum,
    FamiPortReservationInquiryRequest,
    FamiPortPaymentTicketingRequest,
    FamiPortPaymentTicketingCompletionRequest,
    FamiPortPaymentTicketingCancelRequest,
    FamiPortInformationRequest,
    FamiPortCustomerInformationRequest,
    FamiPortReservationInquiryResponse,
    FamiPortPaymentTicketingResponse,
    FamiPortPaymentTicketingCompletionResponse,
    FamiPortPaymentTicketingCancelResponse,
    FamiPortInformationResponse,
    FamiPortCustomerInformationResponse,
    )


logger = logging.getLogger(__name__)


def create_encrypt_key(value):
    if value is None:
        return None


def create_decrypt_key(value):
    if value is None:
        return None
    md = hashlib.md5(value)
    hash_value = md.hexdigest()[:32]  # 文字数 32文字の文字列
    return base64.urlsafe_b64encode(hash_value)


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
            famiport_request = FamiPortPaymentTicketingCompletionRequest()
        elif request_type == FamiPortRequestType.PaymentTicketingCancel:
            famiport_request = FamiPortPaymentTicketingCancelRequest()
        elif request_type == FamiPortRequestType.Information:
            famiport_request = FamiPortInformationRequest()
        elif request_type == FamiPortRequestType.CustomerInformation:
            famiport_request = FamiPortCustomerInformationRequest()
        else:
            raise FamiPortRequestTypeError(request_type)
        famiport_request.request_type = request_type

        barcode_no = famiport_request_dict.get('barCodeNo')
        crypto = FamiPortCrypt(barcode_no) if barcode_no is not None else None
        encrypt_fields = famiport_request.encrypted_fields
        for key, value in famiport_request_dict.items():
            if crypto and key in encrypt_fields:
                try:
                    value = crypto.decrypt(value)
                except Exception as err:
                    raise err.__class__('decrypt error: {}: {}'.format(err.message, value))
            setattr(famiport_request, key, value)
        return famiport_request


@implementer(IFamiPortResponseBuilderFactory)
class FamiPortResponseBuilderFactory(object):
    def __init__(self, *args, **kwargs):
        pass

    def __call__(self, famiport_request):
        request_type = famiport_request.request_type
        if request_type == FamiPortRequestType.ReservationInquiry:
            return FamiPortReservationInquiryResponseBuilder()
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

        logger.info(u"Processing famiport reservation inquiry request. " + \
                    u"店舗コード: " + storeCode + u", 利用日時: " + ticketingDate + u", 予約番号: " + reserveNumber)

        resultCode, replyClass, replyCode = None, None, None
        famiport_order = None
        try:
            famiport_order = FamiPortOrder.get_by_reserveNumber(reserveNumber, authNumber)
        except DBAPIError:
            replyCode = ReplyCodeEnum.OtherError
            logger.error(u"DBAPIError has occurred at FamiPortReservationInquiryResponseBuilder.build_response(). " + \
                         u"店舗コード: " + storeCode + u", 利用日時: " + ticketingDate + u", 予約番号: " + reserveNumber)

        if famiport_order is not None:
            resultCode = ResultCodeEnum.Normal
            replyClass = famiport_order.type
            replyCode = ReplyCodeEnum.Normal
        else:
            resultCode = ResultCodeEnum.OtherError
            if replyCode is None:
                replyCode = ReplyCodeEnum.SearchKeyError

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

        nameInput = 0  # 不要（画面表示なし）
        phoneInput = 0  # 不要（画面表示なし）

        famiport_reservation_inquiry_response = FamiPortReservationInquiryResponse(
            resultCode=resultCode, replyClass=replyClass, replyCode=replyCode,
            playGuideId=playGuideId, barCodeNo=barCodeNo, totalAmount=totalAmount,
            ticketPayment=ticketPayment, systemFee=systemFee,
            ticketingFee=ticketingFee, ticketCountTotal=ticketCountTotal,
            ticketCount=ticketCount, kogyoName=kogyoName, koenDate=koenDate,
            name=name, nameInput=nameInput, phoneInput=phoneInput)

        return famiport_reservation_inquiry_response


class FamiPortPaymentTicketingResponseBuilder(FamiPortResponseBuilder):
    def build_response(self, famiport_payment_ticketing_request=None):
        resultCode = ResultCodeEnum.Normal
        barCodeNo = famiport_payment_ticketing_request.barCodeNo
        storeCode = famiport_payment_ticketing_request.storeCode
        mmkNo = famiport_payment_ticketing_request.mmkNo
        sequenceNo = famiport_payment_ticketing_request.sequenceNo
        ticketingDate = None
        try:
            ticketingDate = datetime.datetime.strptime(famiport_payment_ticketing_request.ticketingDate, '%Y%m%d%H%M%S')
        except ValueError:
            logger.error(u"不正な利用日時です。")

        logger.info(u'Processing famiport payment ticketing request. '  +
                    u'店舗コード: {}, 発券Famiポート番号: {}, 利用日時: {}, 処理通番: {}, 支払番号: {}'.format(
                        storeCode, mmkNo, ticketingDate, sequenceNo, barCodeNo))

        famiport_order, replyCode = None, None
        try:
            famiport_order = FamiPortOrder.get_by_barCodeNo(barCodeNo)
        except DBAPIError:
            replyCode = ReplyCodeEnum.OtherError
            logger.error(u"DBAPIError has occurred at FamiPortPaymentTicketingResponseBuilder.build_response(). " + \
                         u"店舗コード: " + storeCode + u", 発券Famiポート番号: " + mmkNo + u", 利用日時: ", ticketingDate + u", 処理通番: " + sequenceNo + u", 支払番号: " + barCodeNo)

        orderId, replyClass, playGuideId, playGuideName, orderTicketNo, exchangeTicketNo, ticketingStart, ticketingEnd = None, None, None, None, None, None, None, None
        totalAmount, ticketPayment, systemFee, ticketingFee, ticketingCountTotal, ticketCount, kogyoName, koenDate, ticket = None, None, None, None, None, None, None, None, None
        if famiport_order is not None:
            orderId = famiport_order.famiport_order_identifier
            replyClass = famiport_order.type
            if famiport_order.payment_due_at < ticketingDate:
                replyCode = ReplyCodeEnum.PaymentDueError
            if famiport_order.paid_at:
                replyCode = ReplyCodeEnum.AlreadyPaidError
            if famiport_order.issued_at:
                replyCode = ReplyCodeEnum.TicketAlreadyIssuedError
            if famiport_order.ticketing_end_at > ticketingDate:
                replyCode = ReplyCodeEnum.TicketingDueError
            # TODO PaymentCancelError
            if famiport_order.ticketing_start_at < ticketingDate:
                replyCode = ReplyCodeEnum.TicketingBeforeStartError
            # TODO TicketingCancelError
            else:
                replyCode = ReplyCodeEnum.Normal
            playGuideId = famiport_order.playguide_id
            playGuideName = famiport_order.playguide_name
            if replyClass == ReplyClassEnum.CashOnDelivery:
                orderTicketNo = barCodeNo
            elif replyClass == ReplyClassEnum.Prepayment:
                orderTicketNo = barCodeNo
                exchangeTicketNo = famiport_order.exchange_number
                ticketingStart = famiport_order.ticketing_start_at
                ticketingEnd = famiport_order.ticketing_end_at
            elif replyClass == ReplyClassEnum.Paid:
                exchangeTicketNo = famiport_order.exchange_number
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
            if replyCode is None:
                replyCode = ReplyCodeEnum.SearchKeyError

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

        famiport_order, replyCode = None, None
        try:
            famiport_order = FamiPortOrder.get_by_barCodeNo(barCodeNo)
        except DBAPIError:
            replyCode = ReplyCodeEnum.OtherError
            logger.error(u"DBAPIError has occurred at FamiPortPaymentTicketingCancelResponseBuilder.build_response(). " + \
                         u"店舗コード: " + storeCode + u", 発券Famiポート番号: " +  mmkNo + u", 利用日時: ", ticketingDate + u", 処理通番: " + sequenceNo + u", 支払番号: " + barCodeNo + u", 注文ID: " + orderId)

        if famiport_order is not None:
            replyCode = ReplyCodeEnum.Normal
        else:
            resultCode = ResultCodeEnum.OtherError
            if replyCode is None:
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
            logger.error(u"DBAPIError has occurred at FamiPortPaymentTicketingCancelResponseBuilder.build_response(). " + \
                         u"店舗コード: " + storeCode + u", 発券Famiポート番号: " +  mmkNo + u", 利用日時: ", ticketingDate + u", 処理通番: " + sequenceNo + u", 支払番号: " + barCodeNo)

        orderId, replyCode = None, None
        if famiport_order is not None:
            orderId = famiport_order.famiport_order_identifier
            if famiport_order.paid_at:
                replyCode = ReplyCodeEnum.AlreadyPaidError
            if famiport_order.canceled_at:
                replyCode = ReplyCodeEnum.PaymentAlreadyCanceledError
            if famiport_order.issued_at:
                replyCode = ReplyCodeEnum.TicketAlreadyIssuedError
            # TODO PaymentCancelError
            # TODO TicketingCancelError
            else:
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

        resultCode = InformationResultCodeEnum.NoInformation  # デフォルトは案内なし(正常)
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
            logger.error(u"DBAPIError has occurred at FamiPortPaymentTicketingCancelResponseBuilder.build_response(). 店舗コード: " + storeCode)
            resultCode == InformationResultCodeEnum.OtherError
            infoMessage = u'エラーが起こりました。'
            return FamiPortInformationResponse(resultCode=resultCode, infoKubun=infoKubun, infoMessage=infoMessage)
        if infoMessage != None:  # サービス不可時案内
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

        return FamiPortInformationResponse(resultCode=resultCode, infoKubun=infoKubun, infoMessage=None)  # 案内なし(正常)


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
            logger.error(u"DBAPIError has occurred at FamiPortPaymentTicketingCancelResponseBuilder.build_response(). " + \
                         u"店舗コード: " + storeCode + u", 発券Famiポート番号: " +  mmkNo + u", 利用日時: ", ticketingDate + u", 処理通番: " + sequenceNo + u", 支払番号: " + barCodeNo + u", 注文ID: " + orderId)

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
            memberId = famiport_order.memberId
            address1 = famiport_order.address1
            address2 = famiport_order.address2
            identifyNo = famiport_order.identifyNo

        famiport_customer_information_respose = FamiPortCustomerInformationResponse(resultCode=resultCode, replyCode=replyCode, name=name, memberId=memberId, address1=address1, address2=address2, identifyNo=identifyNo)
        famiport_customer_information_respose.set_encryptKey(orderId)
        return famiport_customer_information_respose


@implementer(IXmlFamiPortResponseGenerator)
class XmlFamiPortResponseGenerator(object):
    def __init__(self, famiport_response, xml_encoding='Shift_JIS', encoding='CP932'):
        if famiport_response.encrypt_key:
            hash = hashlib.md5()
            hash.update(famiport_response.encrypt_key)
            str_digest = hash.hexdigest()
            self.famiport_crypt = FamiPortCrypt(base64.urlsafe_b64encode(str_digest))
        self.xml_encoding = xml_encoding
        self.encoding = encoding

    def generate_xmlResponse(self, famiport_response, root_name="FMIF"):
        """Generate XML text of famiport_response with encrypted_fields encrypted.
        Assume filed name in famiport_response is same as tag name in XML.
        List fields in famiport_response are repeated with same tag name in XML.

        :param famiport_response: FamiPortResponse object to generate XMl from.
        :param encrypted_fields: List of field names to encrypt.
        :return: Shift-JIS encoded string of generated XML
        """

        root = etree.Element(root_name)
        doc_root = self._build_xmlTree(root, famiport_response)
        my_xml_declaration = '<?xml version="1.0" encoding="%s" ?>' % self.xml_encoding
        return ''.join((
            my_xml_declaration,
            etree.tostring(
                doc_root,
                encoding=self.encoding,
                xml_declaration=False,
                pretty_print=True
                ),
            ))

    def _build_xmlTree(self, root, obj):
        """
        Build XML tree from object.
        :param root: root of XML tree
        :param object: object to build XML tree from
        :return: root of the XML tree built
        """

        if obj is None:
            return root

        # Create an element for each attribute_name with element.text=attribute_value and put under root.
        for attribute_name in obj._serialized_attrs:
            attribute_value = getattr(obj, attribute_name)
            element_name = attribute_name  # XXX: assuming the element name is identical to the corresponding attribute name
            if attribute_value is not None:
                element = etree.SubElement(root, element_name)
                # TODO Take care of problematic chars in UTF-8 to SJIS conversion
                if attribute_name not in obj.encrypted_fields:
                    element.text = attribute_value
                else:
                    element.text = self.famiport_crypt.encrypt(attribute_value.encode(self.encoding))

        for attribute_name, element_name in obj._serialized_collection_attrs:
            attribute_value = getattr(obj, attribute_name)
            for value in attribute_value:
                element = etree.SubElement(root, element_name)
                self._build_xmlTree(element, value)

        return root
