# -*- coding: utf-8 -*-
import logging
import hashlib
import base64
import datetime
import six
from lxml import etree
from sqlalchemy.exc import DBAPIError
from sqlalchemy import orm
from zope.interface import implementer
from .exceptions import FamiPortRequestTypeError, FamiPortResponseBuilderLookupError
from .utils import (
    str_or_blank,
    FamiPortCrypt,
    )
from ..models import (
    FamiPortOrder,
    FamiPortInformationMessage,
    FamiPortRefund,
    FamiPortRefundEntry,
    FamiPortTicket,
    _session,
    )
from .interfaces import (
    IFamiPortResponseBuilderRegistry,
    IFamiPortResponseBuilder,
    IXmlFamiPortResponseGenerator,
    )
from .models import (
    FamiPortTicketResponse,
    FamiPortRequestType,
    ResultCodeEnum,
    ReplyClassEnum,
    ReplyCodeEnum,
    InformationResultCodeEnum,
    NameRequestInputEnum,
    PhoneRequestInputEnum,
    FamiPortReservationInquiryRequest,
    FamiPortPaymentTicketingRequest,
    FamiPortPaymentTicketingCompletionRequest,
    FamiPortPaymentTicketingCancelRequest,
    FamiPortInformationRequest,
    FamiPortCustomerInformationRequest,
    FamiPortRefundEntryRequest,
    FamiPortReservationInquiryResponse,
    FamiPortPaymentTicketingResponse,
    FamiPortPaymentTicketingCompletionResponse,
    FamiPortPaymentTicketingCancelResponse,
    FamiPortInformationResponse,
    FamiPortCustomerInformationResponse,
    FamiPortRefundEntryResponse,
    )


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
            famiport_request = FamiPortPaymentTicketingCompletionRequest()
        elif request_type == FamiPortRequestType.PaymentTicketingCancel:
            famiport_request = FamiPortPaymentTicketingCancelRequest()
        elif request_type == FamiPortRequestType.Information:
            famiport_request = FamiPortInformationRequest()
        elif request_type == FamiPortRequestType.CustomerInformation:
            famiport_request = FamiPortCustomerInformationRequest()
        elif request_type == FamiPortRequestType.RefundEntry:
            famiport_request = FamiPortRefundEntryRequest()
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
                    raise err.__class__(
                        'decrypt error: {}: {}'.format(err.message, value))
            setattr(famiport_request, key, value)
        return famiport_request


@implementer(IFamiPortResponseBuilderRegistry)
class FamiPortResponseBuilderRegistry(object):
    def __init__(self):
        self.builders = {}

    def add(self, corresponding_request_type, builder):
        self.builders[corresponding_request_type] = builder

    def lookup(self, famiport_request):
        builder = self.builders.get(famiport_request.__class__)
        if builder is None:
            for request_type, builder in self.builders.items():
                if isinstance(famiport_request, request_type):
                    break
            else:
                raise FamiPortResponseBuilderLookupError(u'no corresponding response builder found for %r' % famiport_request)
        return builder


@implementer(IFamiPortResponseBuilder)
class FamiPortResponseBuilder(object):
    def build_response(self, famiport_request=None):
        pass


class FamiPortReservationInquiryResponseBuilder(FamiPortResponseBuilder):
    def build_response(self, famiport_reservation_inquiry_request=None):
        playGuideId = ''
        barCodeNo = ''
        totalAmount = ''
        ticketPayment = ''
        systemFee = ''
        ticketingFee = ''
        ticketCountTotal = ''
        ticketCount = ''
        kogyoName = ''
        koenDate = ''
        name = ''
        nameInput = NameRequestInputEnum.Unnecessary.value
        phoneInput = PhoneRequestInputEnum.Unnecessary.value

        storeCode = famiport_reservation_inquiry_request.storeCode
        ticketingDate = famiport_reservation_inquiry_request.ticketingDate
        reserveNumber = famiport_reservation_inquiry_request.reserveNumber
        authNumber = famiport_reservation_inquiry_request.authNumber

        logger.info(u"Processing famiport reservation inquiry request. 店舗コード: %s , 利用日時: %s , 予約番号: %s "
                    % (storeCode, ticketingDate, reserveNumber))

        resultCode, replyClass, replyCode = None, None, None
        famiport_order = None
        try:
            famiport_order = FamiPortOrder.get_by_reserveNumber(
                reserveNumber, authNumber)
        except DBAPIError:
            replyCode = ReplyCodeEnum.OtherError.value
            logger.error(u"DBAPIError has occurred at FamiPortReservationInquiryResponseBuilder.build_response(). 店舗コード: %s , 利用日時: %s , 予約番号: %s "
                         % (storeCode, ticketingDate, reserveNumber))

        if famiport_order is not None:
            resultCode = ResultCodeEnum.Normal.value
            replyClass = famiport_order.type
            replyCode = ReplyCodeEnum.Normal.value
            nameInput = NameRequestInputEnum.Necessary.value if famiport_order.customer_name_input else NameRequestInputEnum.Unnecessary.value
            phoneInput = PhoneRequestInputEnum.Necessary.value if famiport_order.customer_phone_input else PhoneRequestInputEnum.Unnecessary.value
            if famiport_order.performance_start_at:
                koenDate = famiport_order.performance_start_at.strftime('%Y%m%d%H%M')
            else:
                # 値が設定されていない場合は画面に表示しない
                # ”888888888888”  (オール8)の場合
                # チケット料金の注意事項(下記参照)を表示する
                # （「2：前払い（後日渡し）の前払い時」または「4:前払いのみ」の場合のみ）
                # チケット料金に表示されている金額は、有料組織の年会費などの場合もある
                # ”999999999999 (オール9)の場合、
                # 期間内有効券と判断して公演日時を表示しない。
                koenDate = '99999999999999'
        else:
            resultCode = ResultCodeEnum.OtherError.value
            if replyCode is None:
                replyCode = ReplyCodeEnum.SearchKeyError.value

        if replyCode == ReplyCodeEnum.Normal.value:
            playGuideId = famiport_order.famiport_client.playguide.discrimination_code
            barCodeNo = famiport_order.barcode_no
            totalAmount = famiport_order.total_amount
            ticketPayment = str_or_blank(famiport_order.ticket_payment)
            systemFee = str_or_blank(famiport_order.system_fee)
            ticketingFee = str_or_blank(famiport_order.ticketing_fee)
            ticketCountTotal = str_or_blank(famiport_order.ticket_total_count)
            ticketCount = str_or_blank(famiport_order.ticket_count)
            kogyoName = famiport_order.famiport_sales_segment.famiport_performance.name
            name = famiport_order.customer_name

        totalAmount = str_or_blank(totalAmount, 8, fillvalue='0')
        ticketPayment = str_or_blank(ticketPayment, 8, fillvalue='0')
        systemFee = str_or_blank(systemFee, 8, fillvalue='0')
        ticketingFee = str_or_blank(ticketingFee, 8, fillvalue='0')
        replyClass = str_or_blank(replyClass)

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
        replyCode = None
        famiport_order = None
        resultCode = ResultCodeEnum.Normal.value
        barCodeNo = famiport_payment_ticketing_request.barCodeNo
        storeCode = famiport_payment_ticketing_request.storeCode
        mmkNo = famiport_payment_ticketing_request.mmkNo
        sequenceNo = famiport_payment_ticketing_request.sequenceNo
        ticketingDate = datetime.datetime.now()

        orderId = ''
        replyClass = ''
        playGuideId = ''
        playGuideName = ''
        orderTicketNo = ''
        exchangeTicketNo = ''
        ticketingStart = ''
        ticketingEnd = ''
        totalAmount = ''
        ticketPayment = ''
        systemFee = ''
        ticketingFee = ''
        ticketingCountTotal = ''
        ticketCount = ''
        kogyoName = ''
        koenDate = ''
        tickets = ''
        try:
            ticketingDate = datetime.datetime.strptime(
                famiport_payment_ticketing_request.ticketingDate, '%Y%m%d%H%M%S')
        except ValueError:
            logger.error(u"不正な利用日時です。")

        logger.info(u'Processing famiport payment ticketing request. ' +
                    u'店舗コード: %s, 発券Famiポート番号: %s, 利用日時: %s, 処理通番: %s, 支払番号: %s'
                    % (storeCode, mmkNo, ticketingDate.strftime('%Y%m%d%H%M%S'), sequenceNo, barCodeNo))

        try:
            famiport_order = FamiPortOrder.get_by_barCodeNo(barCodeNo)
        except DBAPIError:
            replyCode = ReplyCodeEnum.OtherError.value
            logger.error(u"DBAPIError has occurred at FamiPortPaymentTicketingResponseBuilder.build_response(). ' + \
                         u'店舗コード: %s , 発券Famiポート番号: %s , 利用日時: %s , 処理通番: %s , 支払番号: %s"
                         % (storeCode, mmkNo, ticketingDate.strftime('%Y%m%d%H%M%S'), sequenceNo, barCodeNo))

        if famiport_order is not None:
            orderId = famiport_order.famiport_order_identifier
            replyClass = famiport_order.type
            if famiport_order.payment_due_at and famiport_order.payment_due_at < ticketingDate:
                replyCode = ReplyCodeEnum.PaymentDueError.value
            if famiport_order.paid_at:
                replyCode = ReplyCodeEnum.AlreadyPaidError.value
            if famiport_order.issued_at:
                replyCode = ReplyCodeEnum.TicketAlreadyIssuedError.value
            if famiport_order.ticketing_end_at and famiport_order.ticketing_end_at < ticketingDate:
                replyCode = ReplyCodeEnum.TicketingDueError.value
            # TODO PaymentCancelError
            if famiport_order.ticketing_start_at and famiport_order.ticketing_start_at > ticketingDate:
                replyCode = ReplyCodeEnum.TicketingBeforeStartError.value
            # TODO TicketingCancelError
            else:
                replyCode = ReplyCodeEnum.Normal.value
            playGuideId = famiport_order.famiport_client.playguide.discrimination_code
            playGuideName = famiport_order.famiport_client.playguide.name
            if replyClass == ReplyClassEnum.CashOnDelivery.value:
                orderTicketNo = barCodeNo
            elif replyClass == ReplyClassEnum.Prepayment.value:
                orderTicketNo = barCodeNo
                exchangeTicketNo = famiport_order.exchange_number
                ticketingStart = famiport_order.ticketing_start_at
                ticketingEnd = famiport_order.ticketing_end_at
            elif replyClass == ReplyClassEnum.Paid.value:
                exchangeTicketNo = famiport_order.exchange_number
            elif replyClass == ReplyClassEnum.PrepaymentOnly.value:
                orderTicketNo = barCodeNo
            else:
                pass

            totalAmount = str_or_blank(famiport_order.total_amount, 8, fillvalue='0')
            ticketPayment = str_or_blank(famiport_order.ticket_payment, 8, fillvalue='0')
            systemFee = str_or_blank(famiport_order.system_fee, 8, fillvalue='0')
            ticketingFee = str_or_blank(famiport_order.ticketing_fee, 8, fillvalue='0')
            ticketingCountTotal = str_or_blank(famiport_order.ticket_total_count)
            ticketCount = str_or_blank(famiport_order.ticket_count)
            kogyoName = famiport_order.famiport_sales_segment.famiport_performance.name

            start_at = famiport_order.famiport_sales_segment.famiport_performance.start_at
            koenDate = start_at.strftime('%Y%m%d%H%M') if start_at else '999999999999'
            tickets = famiport_order.famiport_tickets
        else:
            resultCode = ResultCodeEnum.OtherError.value
            if replyCode is None:
                replyCode = ReplyCodeEnum.SearchKeyError.value

        famiport_ticket_responses = []
        if tickets:

            for ticket in tickets:
                ftr = FamiPortTicketResponse()
                ftr.barCodeNo = ticket.barcode_number
                ftr.ticketClass = str(ticket.type)
                ftr.templateCode = ticket.template_code
                ftr.ticketData = ticket.data
                famiport_ticket_responses.append(ftr)

        playGuideId = str_or_blank(playGuideId, 5, fillvalue='0')
        totalAmount = str_or_blank(totalAmount)
        ticketPayment = str_or_blank(ticketPayment)
        systemFee = str_or_blank(systemFee)
        ticketingFee = str_or_blank(ticketingFee)
        ticketCount = str_or_blank(ticketCount)
        ticketingCountTotal = str_or_blank(ticketingCountTotal)
        replyClass = str_or_blank(replyClass)

        famiport_payment_ticketing_response = FamiPortPaymentTicketingResponse(
            resultCode=resultCode, storeCode=storeCode, sequenceNo=sequenceNo,
            barCodeNo=barCodeNo, orderId=orderId, replyClass=replyClass,
            replyCode=replyCode, playGuideId=playGuideId, playGuideName=playGuideName,
            orderTicketNo=orderTicketNo, exchangeTicketNo=exchangeTicketNo,
            ticketingStart=ticketingStart, ticketingEnd=ticketingEnd,
            totalAmount=totalAmount, ticketPayment=ticketPayment, systemFee=systemFee,
            ticketingFee=ticketingFee, ticketCountTotal=ticketingCountTotal,
            ticketCount=ticketCount, kogyoName=kogyoName, koenDate=koenDate, tickets=famiport_ticket_responses)
        return famiport_payment_ticketing_response


class FamiPortPaymentTicketingCompletionResponseBuilder(FamiPortResponseBuilder):

    def build_response(self, famiport_payment_ticketing_completion_request=None):
        resultCode = ResultCodeEnum.Normal.value
        storeCode = famiport_payment_ticketing_completion_request.storeCode
        mmkNo = famiport_payment_ticketing_completion_request.mmkNo
        ticketingDate = datetime.datetime.strptime(
            famiport_payment_ticketing_completion_request.ticketingDate, '%Y%m%d%H%M%S')
        sequenceNo = famiport_payment_ticketing_completion_request.sequenceNo
        barCodeNo = famiport_payment_ticketing_completion_request.barCodeNo
        orderId = famiport_payment_ticketing_completion_request.orderId

        famiport_order = None
        replyCode = None

        try:
            famiport_order = FamiPortOrder.get_by_barCodeNo(barCodeNo)
        except DBAPIError:
            replyCode = ReplyCodeEnum.OtherError.value
            logger.error(u'DBAPIError has occurred at FamiPortPaymentTicketingCancelResponseBuilder.build_response().' +
                         u'店舗コード: %s , 発券Famiポート番号: %s , 利用日時: %s , 処理通番: %s , 支払番号: %s , 注文ID: %s'
                         % (storeCode, mmkNo, ticketingDate.strftime('%Y%m%d%H%M%S'), sequenceNo, barCodeNo, orderId))

        if famiport_order is not None:
            famiport_order.paid_at = ticketingDate
            famiport_order.issued_at = ticketingDate
            replyCode = ReplyCodeEnum.Normal.value
        else:
            resultCode = ResultCodeEnum.OtherError.value
            if replyCode is None:
                replyCode = ReplyCodeEnum.SearchKeyError.value

        famiport_payment_ticketing_completion_response = FamiPortPaymentTicketingCompletionResponse(
            resultCode=resultCode, storeCode=storeCode, sequenceNo=sequenceNo, barCodeNo=barCodeNo, orderId=orderId, replyCode=replyCode)
        return famiport_payment_ticketing_completion_response


class FamiPortPaymentTicketingCancelResponseBuilder(FamiPortResponseBuilder):

    def build_response(self, famiport_payment_ticketing_cancel_request=None):
        resultCode = ResultCodeEnum.Normal.value
        storeCode = famiport_payment_ticketing_cancel_request.storeCode
        mmkNo = famiport_payment_ticketing_cancel_request.mmkNo
        ticketingDate = famiport_payment_ticketing_cancel_request.ticketingDate
        sequenceNo = famiport_payment_ticketing_cancel_request.sequenceNo
        barCodeNo = famiport_payment_ticketing_cancel_request.barCodeNo

        famiport_order = None
        try:
            famiport_order = FamiPortOrder.get_by_barCodeNo(barCodeNo)
        except DBAPIError:
            logger.error(u'DBAPIError has occurred at FamiPortPaymentTicketingCancelResponseBuilder.build_response(). ' +
                         u'店舗コード: %s , 発券Famiポート番号: %s , 利用日時: %s , 処理通番: %s , 支払番号: %s'
                         % (storeCode, mmkNo, ticketingDate, sequenceNo, barCodeNo))

        orderId = None
        replyCode = None
        if famiport_order is not None:
            orderId = famiport_order.famiport_order_identifier
            if famiport_order.paid_at:
                replyCode = ReplyCodeEnum.AlreadyPaidError.value
            if famiport_order.canceled_at:
                replyCode = ReplyCodeEnum.PaymentAlreadyCanceledError.value
            if famiport_order.issued_at:
                replyCode = ReplyCodeEnum.TicketAlreadyIssuedError.value
            # TODO PaymentCancelError
            # TODO TicketingCancelError
            else:
                replyCode = ReplyCodeEnum.Normal.value
        else:
            resultCode = ResultCodeEnum.OtherError.value
            replyCode = ReplyCodeEnum.OtherError.value

        famiport_payment_ticketing_cancel_response = FamiPortPaymentTicketingCancelResponse(
            resultCode=resultCode, storeCode=storeCode, sequenceNo=sequenceNo, barCodeNo=barCodeNo, orderId=orderId, replyCode=replyCode)
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
        # デフォルトは案内なし(正常)
        resultCode = InformationResultCodeEnum.NoInformation.value
        infoKubun = famiport_information_request.infoKubun
        storeCode = famiport_information_request.storeCode
        infoMessage = ''
        try:
            infoMessage = FamiPortInformationMessage.get_message(
                InformationResultCodeEnum.ServiceUnavailable)
        except DBAPIError:
            logger.error(
                u"DBAPIError has occurred at FamiPortPaymentTicketingCancelResponseBuilder.build_response(). 店舗コード: %s" % storeCode)
            resultCode == InformationResultCodeEnum.OtherError.value
            infoMessage = u'エラーが起こりました。'
            return FamiPortInformationResponse(
                resultCode=resultCode,
                infoKubun=infoKubun,
                infoMessage=infoMessage,
                )

        if infoMessage is not None:  # サービス不可時案内
            resultCode = InformationResultCodeEnum.ServiceUnavailable.value
            return FamiPortInformationResponse(
                resultCode=resultCode,
                infoKubun=infoKubun,
                infoMessage=infoMessage,
                )

        try:
            infoMessage = FamiPortInformationMessage.get_message(
                InformationResultCodeEnum.WithInformation)
        except DBAPIError:
            resultCode == InformationResultCodeEnum.OtherError.value
            infoMessage = u'エラーが起こりました。'
            return FamiPortInformationResponse(
                resultCode=resultCode,
                infoKubun=infoKubun,
                infoMessage=infoMessage,
                )

        if infoMessage is not None:  # 文言の設定あり
            resultCode = InformationResultCodeEnum.WithInformation.value
            return FamiPortInformationResponse(
                resultCode=resultCode,
                infoKubun=infoKubun,
                infoMessage=infoMessage,
                )

        # 案内なし(正常)
        return FamiPortInformationResponse(
            resultCode=resultCode,
            infoKubun=infoKubun,
            infoMessage='',
            )


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
            logger.error(u'DBAPIError has occurred at FamiPortPaymentTicketingCancelResponseBuilder.build_response(). ' +
                         u'店舗コード: %s , 発券Famiポート番号: %s , 利用日時: %s , 処理通番: %s , 支払番号: %s , 注文ID: %s'
                         % (storeCode, mmkNo, ticketingDate, sequenceNo, barCodeNo, orderId))

        resultCode = None
        replyCode = None
        if famiport_order is not None:
            resultCode = ResultCodeEnum.Normal.value
            replyCode = ReplyCodeEnum.Normal.value
        else:
            resultCode = ResultCodeEnum.OtherError.value
            replyCode = ReplyCodeEnum.CustomerNamePrintInformationError.value

        name = ''
        memberId = ''
        address1 = ''
        address2 = ''
        identifyNo = ''

        if replyCode == ReplyCodeEnum.Normal.value:
            name = famiport_order.customer_name
            # TODO Make sure where to get memberId
            memberId = famiport_order.customer_member_id
            address1 = famiport_order.customer_address_1
            address2 = famiport_order.customer_address_2
            # TODO Make sure where to get identifyNo
            identifyNo = famiport_order.customer_identify_no

        famiport_customer_information_respose = FamiPortCustomerInformationResponse(
            resultCode=resultCode, replyCode=replyCode, name=name, memberId=memberId,
            address1=address1, address2=address2, identifyNo=identifyNo)
        famiport_customer_information_respose.set_encryptKey(orderId)
        return famiport_customer_information_respose


class FamiPortRefundEntryResponseBuilder(FamiPortResponseBuilder):
    def build_response(self, famiport_refund_entry_request):
        famiport_refund_entry_response = FamiPortRefundEntryResponse(
            businessFlg=famiport_refund_entry_request.businessFlg,
            textTyp=famiport_refund_entry_request.textTyp,
            entryTyp=famiport_refund_entry_request.entryTyp,
            shopNo=famiport_refund_entry_request.shopNo,
            registerNo=famiport_refund_entry_request.registerNo,
            timeStamp=famiport_refund_entry_request.timeStamp,
            )
        barcode_numbers = famiport_refund_entry_request.barcode_numbers
        session = _session
        refund_entries = [
            (
                barcode_number,
                (
                    session.query(FamiPortRefundEntry) \
                        .options(orm.joinedload(FamiPortRefundEntry.famiport_ticket)) \
                        .join(FamiPortRefundEntry.famiport_ticket) \
                        .filter_by(FamiPortTicket.barcode_number == barcode_number) \
                        .one() \
                    if barcode_number \
                    else None
                    )
                )
            for barcode_number in barcode_numbers
            ]
        def build_per_ticket_record(barcode_number, refund_entry):
            if refund_entry is None:
                result_code = u'01'
                main_title = u''
                perf_day = u''
                repayment = u''
                refund_start = u''
                refund_end = u''
                ticket_typ = u''
                charge=u''
            else:
                if refund_entry.refunded_at is not None:
                    result_code = u'02'
                else:
                    if refund_entry.famiport_refund.start_at > now \
                       or refund_entry.famiport_refund.end_at < now:
                        result_code = u'03'
                    else:
                        result_code = u'00'
                famiport_performance = refund_entry.famiport_ticket.famiport_order.famiport_sales_segment.famiport_performance
                main_title = famiport_performance.name
                perf_day = six.text_type(famiport_performance.start_at.strftime('%Y%m%d')) if famiport_performance.start_at else u'19700101'
                repayment = u'{0:06d}'.format(refund_entry.ticket_payment + refund_entry.ticketing_fee + refund_entry.system_fee + refund_entry.other_fees)
                refund_start = six.text_type(refund_entry.famiport_refund.start_at.strftime('%Y%m%d'))
                refund_end = six.text_type(refund_entry.famiport_refund.end_at.strftime('%Y%m%d'))
                ticket_typ = u'{0:d}'.format(refund_entry.famiport_ticket.type)
                charge = u'{0:06d}'.format(refund_entry.ticketing_fee + refund_entry.system_fee + refund_entry.other_fees)
            return dict(
                barCode=barcode_number,
                resultCode=result_code,
                mainTitle=main_title,
                perfDay=perf_day,
                repayment=repayment,
                refundStart=refund_start,
                refundEnd=refund_end,
                ticketTyp=ticket_typ,
                charge=charge
                )

        famiport_refund_entry_response.per_ticket_records = [
            build_per_ticket_record(barcode_number, refund_entry)
            for barcode_number, refund_entry in refund_entries
            ]
        return famiport_refund_entry_response

@implementer(IXmlFamiPortResponseGenerator)
class XmlFamiPortResponseGenerator(object):

    def __init__(self, famiport_response, xml_encoding='Shift_JIS', encoding='CP932'):
        self.famiport_crypt = None
        if famiport_response.encrypt_key:
            hash = hashlib.md5()
            hash.update(famiport_response.encrypt_key)
            str_digest = hash.hexdigest()
            self.famiport_crypt = FamiPortCrypt(
                base64.urlsafe_b64encode(str_digest))
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
        """Build XML tree from object.

        :param root: root of XML tree
        :param object: object to build XML tree from
        :return: root of the XML tree built
        """

        if obj is None:
            return root

        # Create an element for each attribute_name with
        # element.text=attribute_value and put under root.
        for attribute_name in obj._serialized_attrs:
            attribute_value = getattr(obj, attribute_name)
            # XXX: assuming the element name is identical to the corresponding
            # attribute name
            element_name = attribute_name
            if attribute_value is not None:
                element = etree.SubElement(root, element_name)
                # TODO Take care of problematic chars in UTF-8 to SJIS
                # conversion
                if attribute_name not in obj.encrypted_fields:
                    try:
                        element.text = attribute_value
                    except (TypeError, ValueError) as err:
                        raise err.__class__('illigal type: {}: {}'.format(attribute_name, err))
                elif self.famiport_crypt:
                    element.text = self.famiport_crypt.encrypt(
                        attribute_value.encode(self.encoding))

        for attribute_name, element_name in obj._serialized_collection_attrs:
            attribute_value = getattr(obj, attribute_name)
            for value in attribute_value:
                element = etree.SubElement(root, element_name)
                self._build_xmlTree(element, value)

        return root
