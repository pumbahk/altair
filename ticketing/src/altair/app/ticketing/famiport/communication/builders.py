# -*- coding: utf-8 -*-
import logging
import datetime
import itertools
import six
from lxml import etree
from sqlalchemy import or_
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import orm
from zope.interface import implementer
from ..exc import FamiPortError
from .exceptions import (
    FamiPortRequestTypeError,
    FamiPortResponseBuilderLookupError,
    )
from .utils import (
    str_or_blank,
    FamiPortCrypt,
    )
from ..models import (
    FamiPortOrder,
    FamiPortInformationMessage,
    FamiPortRefundEntry,
    FamiPortClient,
    FamiPortTicket,
    FamiPortOrderType,
    )
from .interfaces import (
    IFamiPortResponseBuilderRegistry,
    IFamiPortResponseBuilder,
    IXmlFamiPortResponseGenerator,
    )
from .models import (
    InfoKubunEnum,
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


_strip_zfill = lambda word: word.lstrip(u'0').zfill(1)


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
    def build_response(self, famiport_reservation_inquiry_request, session, now):
        playGuideId = u''
        barCodeNo = u''
        totalAmount = u''
        ticketPayment = u''
        systemFee = u''
        ticketingFee = u''
        ticketCountTotal = u''
        ticketCount = u''
        kogyoName = u''
        koenDate = u''
        name = u''
        nameInput = NameRequestInputEnum.Unnecessary.value
        phoneInput = PhoneRequestInputEnum.Unnecessary.value
        storeCode = _strip_zfill(famiport_reservation_inquiry_request.storeCode)
        ticketingDate = None
        reserveNumber = famiport_reservation_inquiry_request.reserveNumber
        authNumber = famiport_reservation_inquiry_request.authNumber

        logger.info(
            u"processing famiport reservation inquiry request. "
            u"店舗コード: %s, 利用日時: %s, 予約番号: %s "
            % (storeCode, famiport_reservation_inquiry_request.ticketingDate, reserveNumber)
            )

        resultCode, replyClass, replyCode = None, None, None
        try:
            try:
                ticketingDate = datetime.datetime.strptime(
                    famiport_reservation_inquiry_request.ticketingDate,
                    '%Y%m%d%H%M%S'
                    )
            except ValueError:
                logger.error(u"不正な利用日時です (%s)" % famiport_reservation_inquiry_request.ticketingDate)
                raise

            try:
                famiport_order = FamiPortOrder.get_by_reserveNumber(reserveNumber, authNumber, session=session)
            except NoResultFound:
                logger.error(u'FamiPortOrder not found with reserveNumber=%s' % reserveNumber)
                famiport_order = None

            if famiport_order is not None:
                if famiport_order.payment_start_at is not None and  \
                   famiport_order.payment_start_at > ticketingDate:
                    logger.error(u'ticketingDate is earlier than payment_start_at (%r)' % (famiport_order.payment_start_at, ))
                    famiport_order = None

            if famiport_order is not None:
                receipt = famiport_order.create_receipt(storeCode)
                if receipt is None or _strip_zfill(receipt.shop_code) != storeCode:
                    resultCode = ResultCodeEnum.OtherError.value
                    replyCode = ReplyCodeEnum.SearchKeyError.value
                    famiport_order = None
                else:
                    receipt.inquired_at = now
                    session.commit()

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

                playGuideId = famiport_order.famiport_client.code
                barCodeNo = receipt.barcode_no
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
            else:
                resultCode = ResultCodeEnum.OtherError.value
                replyCode = ReplyCodeEnum.SearchKeyError.value
            famiport_reservation_inquiry_response = FamiPortReservationInquiryResponse(
                resultCode=resultCode,
                replyClass=replyClass,
                replyCode=replyCode,
                playGuideId=playGuideId,
                barCodeNo=barCodeNo,
                totalAmount=totalAmount,
                ticketPayment=ticketPayment,
                systemFee=systemFee,
                ticketingFee=ticketingFee,
                ticketCountTotal=ticketCountTotal,
                ticketCount=ticketCount,
                kogyoName=kogyoName,
                koenDate=koenDate,
                name=name,
                nameInput=nameInput,
                phoneInput=phoneInput
                )
        except Exception:
            logger.exception(
                u"an exception occurred at FamiPortReservationInquiryResponseBuilder.build_response(). "
                u"店舗コード: %s, 利用日時: %s, 予約番号: %s"
                % (storeCode, famiport_reservation_inquiry_request.ticketingDate, reserveNumber)
                )
            resultCode = ResultCodeEnum.OtherError.value
            replyCode = ReplyCodeEnum.OtherError.value
            famiport_reservation_inquiry_response = FamiPortReservationInquiryResponse(
                resultCode=resultCode,
                replyClass=replyClass,
                replyCode=replyCode
                )

        return famiport_reservation_inquiry_response


class FamiPortPaymentTicketingResponseBuilder(FamiPortResponseBuilder):
    def __init__(self, moratorium=datetime.timedelta(seconds=1800)):
        # 入金期限を手続き中に過ぎてしまった場合に考慮される、入金期限からの猶予期間
        self.moratorium = moratorium

    def build_response(self, famiport_payment_ticketing_request, session, now):
        famiport_order = None
        resultCode = ResultCodeEnum.Normal.value
        replyCode = ReplyCodeEnum.Normal.value
        barCodeNo = famiport_payment_ticketing_request.barCodeNo
        storeCode = _strip_zfill(famiport_payment_ticketing_request.storeCode)
        mmkNo = famiport_payment_ticketing_request.mmkNo
        sequenceNo = famiport_payment_ticketing_request.sequenceNo
        ticketingDate = ''

        orderId = u''
        replyClass = u''
        playGuideId = u''
        playGuideName = u''
        orderTicketNo = u''
        exchangeTicketNo = u''
        ticketingStart = u''
        ticketingEnd = u''
        totalAmount = u''
        ticketPayment = u''
        systemFee = u''
        ticketingFee = u''
        ticketingCountTotal = u''
        ticketCount = u''
        kogyoName = u''
        koenDate = u''
        tickets = u''

        logger.info(u'Processing famiport payment ticketing request. '
                    u'店舗コード: %s, 発券Famiポート番号: %s, 利用日時: %s, 処理通番: %s, 支払番号: %s'
                    % (storeCode, mmkNo, famiport_payment_ticketing_request.ticketingDate, sequenceNo, barCodeNo))

        try:
            try:
                ticketingDate = datetime.datetime.strptime(
                    famiport_payment_ticketing_request.ticketingDate,
                    '%Y%m%d%H%M%S'
                    )
            except ValueError:
                logger.error(u"不正な利用日時です (%s)" % famiport_payment_ticketing_request.ticketingDate)
                raise

            try:
                famiport_order = FamiPortOrder.get_by_barCodeNo(barCodeNo, session=session)
            except NoResultFound:
                logger.error(u'FamiPortOrder not found with barCodeNo=%s' % barCodeNo)
                famiport_order = None
                resultCode = ResultCodeEnum.OtherError.value
                replyCode = ReplyCodeEnum.SearchKeyError.value

            receipt = None
            if famiport_order is not None:
                receipt = famiport_order.get_receipt(barCodeNo)
                if receipt is None or _strip_zfill(receipt.shop_code) != storeCode:
                    logger.error(u'shop_code differs (%s != %s)' % (receipt.shop_code, storeCode))
                    resultCode = ResultCodeEnum.OtherError.value
                    replyCode = ReplyCodeEnum.SearchKeyError.value
                    famiport_order = None
                elif receipt.can_payment(now):
                    receipt.payment_request_received_at = now
                else:
                    resultCode = ResultCodeEnum.OtherError.value
                    replyCode = ReplyCodeEnum.SearchKeyError.value
                    famiport_order = None

            # validate the request
            if famiport_order is not None:

                orderId = famiport_order.famiport_order_identifier
                order_type = famiport_order.type

                if order_type in (FamiPortOrderType.CashOnDelivery.value, FamiPortOrderType.PaymentOnly.value) or \
                   (order_type == FamiPortOrderType.Payment.value and famiport_order.paid_at is None):
                    if famiport_order.paid_at:
                        resultCode = ResultCodeEnum.OtherError.value
                        replyCode = ReplyCodeEnum.AlreadyPaidError.value
                        famiport_order = None
                    elif famiport_order.payment_start_at is not None \
                            and famiport_order.payment_start_at > ticketingDate:
                        logger.error(u'ticketingDate is earlier than payment_start_at (%r)' % (famiport_order.payment_start_at, ))
                        resultCode = ResultCodeEnum.OtherError.value
                        replyCode = ReplyCodeEnum.SearchKeyError.value
                        famiport_order = None
                    elif famiport_order.payment_due_at is not None \
                            and famiport_order.payment_due_at + self.moratorium < ticketingDate:
                        logger.error(u'ticketingDate is later than payment_due_at (%r) + moratorium (%r)' % (
                            famiport_order.payment_due_at, self.moratorium))
                        resultCode = ResultCodeEnum.OtherError.value
                        replyCode = ReplyCodeEnum.PaymentDueError.value
                        famiport_order = None

                if famiport_order is not None and \
                   (famiport_order.paid_at is not None
                    if order_type == FamiPortOrderType.Payment.value
                        else order_type != FamiPortOrderType.PaymentOnly.value):
                    if famiport_order.issued_at:
                        logger.error(u'tickets for order are already issued at %s' % (famiport_order.issued_at, ))
                        resultCode = ResultCodeEnum.OtherError.value
                        replyCode = ReplyCodeEnum.TicketAlreadyIssuedError.value
                        famiport_order = None
                    elif famiport_order.ticketing_start_at is not None \
                            and famiport_order.ticketing_start_at > ticketingDate:
                        logger.error(u'ticketingDate is earlier than ticketing_start_at (%r)' % (famiport_order.ticketing_start_at,))
                        resultCode = ResultCodeEnum.OtherError.value
                        replyCode = ReplyCodeEnum.TicketingBeforeStartError.value
                        famiport_order = None
                    elif famiport_order.ticketing_end_at is not None \
                            and famiport_order.ticketing_end_at + self.moratorium < ticketingDate:
                        logger.error(u'ticketingDate is later than ticketing_end_at (%r) + moratorium (%r)' % (
                            famiport_order.ticketing_end_at, self.moratorium))
                        resultCode = ResultCodeEnum.OtherError.value
                        replyCode = ReplyCodeEnum.TicketingDueError.value
                        famiport_order = None

            if famiport_order is not None:
                playGuideId = famiport_order.famiport_client.code
                playGuideName = famiport_order.famiport_client.name
                if order_type == FamiPortOrderType.CashOnDelivery.value:
                    replyClass = ReplyClassEnum.CashOnDelivery.value
                    orderTicketNo = barCodeNo
                elif order_type == FamiPortOrderType.Payment.value:
                    if famiport_order.paid_at is None:
                        replyClass = ReplyClassEnum.Prepayment.value
                    else:
                        replyClass = ReplyClassEnum.Paid.value
                    orderTicketNo = barCodeNo
                    exchangeTicketNo = receipt.exchange_number
                    if famiport_order.ticketing_start_at:
                        ticketingStart = famiport_order.ticketing_start_at.strftime("%Y%m%d%H%M%S")
                    if famiport_order.ticketing_end_at:
                        ticketingEnd = famiport_order.ticketing_end_at.strftime("%Y%m%d%H%M%S")
                elif order_type == FamiPortOrderType.Ticketing.value:
                    replyClass = ReplyClassEnum.Paid.value
                    exchangeTicketNo = receipt.exchange_number
                elif order_type == FamiPortOrderType.PaymentOnly.value:
                    replyClass = ReplyClassEnum.PrepaymentOnly.value
                    orderTicketNo = barCodeNo
                else:
                    raise ValueError(u'unknown order type: %r' % order_type)

                totalAmount = str_or_blank(famiport_order.total_amount, 8, fillvalue='0')
                ticketPayment = str_or_blank(famiport_order.ticket_payment, 8, fillvalue='0')
                systemFee = str_or_blank(famiport_order.system_fee, 8, fillvalue='0')
                ticketingFee = str_or_blank(famiport_order.ticketing_fee, 8, fillvalue='0')
                ticketingCountTotal = str_or_blank(famiport_order.ticket_total_count)
                exchangeTicketNo = str_or_blank(exchangeTicketNo)
                ticketCount = str_or_blank(famiport_order.ticket_count)
                kogyoName = famiport_order.famiport_sales_segment.famiport_performance.name

                start_at = famiport_order.famiport_sales_segment.famiport_performance.start_at
                koenDate = start_at.strftime('%Y%m%d%H%M') if start_at else '999999999999'
                tickets = famiport_order.famiport_tickets

                famiport_ticket_responses = []
                if tickets:
                    for ticket in tickets:
                        ftr = FamiPortTicketResponse()
                        ftr.barCodeNo = ticket.barcode_number
                        ftr.ticketClass = str(ticket.type)
                        ftr.templateCode = ticket.template_code
                        ftr.ticketData = ticket.data
                        famiport_ticket_responses.append(ftr)

                resultCode = str_or_blank(resultCode)
                replyCode = str_or_blank(replyCode)
                replyClass = str_or_blank(replyClass)

                famiport_payment_ticketing_response = FamiPortPaymentTicketingResponse(
                    resultCode=resultCode,
                    storeCode=storeCode.zfill(6),
                    sequenceNo=sequenceNo,
                    barCodeNo=barCodeNo,
                    orderId=orderId,
                    replyClass=replyClass,
                    replyCode=replyCode,
                    playGuideId=playGuideId,
                    playGuideName=playGuideName,
                    orderTicketNo=orderTicketNo,
                    exchangeTicketNo=exchangeTicketNo,
                    ticketingStart=ticketingStart,
                    ticketingEnd=ticketingEnd,
                    totalAmount=totalAmount,
                    ticketPayment=ticketPayment,
                    systemFee=systemFee,
                    ticketingFee=ticketingFee,
                    ticketCountTotal=ticketingCountTotal,
                    ticketCount=ticketCount,
                    kogyoName=kogyoName,
                    koenDate=koenDate,
                    tickets=famiport_ticket_responses
                    )
            else:
                famiport_payment_ticketing_response = FamiPortPaymentTicketingResponse(
                    resultCode=str_or_blank(resultCode),
                    replyCode=str_or_blank(replyCode),
                    storeCode=storeCode.zfill(6),
                    sequenceNo=sequenceNo,
                    barCodeNo=barCodeNo,
                    orderId=orderId,
                    replyClass=replyClass,
                    playGuideId=playGuideId,
                    playGuideName=playGuideName
                    )
        except:
            logger.exception(
                u"an exception has occurred at FamiPortPaymentTicketingResponseBuilder.build_response(). "
                u"店舗コード: %s , 発券Famiポート番号: %s , 利用日時: %s , 処理通番: %s , 支払番号: %s"
                % (storeCode, mmkNo, famiport_payment_ticketing_request.ticketingDate, sequenceNo, barCodeNo)
                )
            resultCode = ResultCodeEnum.OtherError.value
            replyCode = ReplyCodeEnum.OtherError.value
            famiport_payment_ticketing_response = FamiPortPaymentTicketingResponse(
                resultCode=str_or_blank(resultCode),
                replyCode=str_or_blank(replyCode),
                sequenceNo=sequenceNo,
                storeCode=storeCode.zfill(6)
                )
        return famiport_payment_ticketing_response


class FamiPortPaymentTicketingCompletionResponseBuilder(FamiPortResponseBuilder):

    def build_response(self, famiport_payment_ticketing_completion_request, session, now):
        resultCode = ResultCodeEnum.Normal.value
        storeCode = _strip_zfill(famiport_payment_ticketing_completion_request.storeCode)
        mmkNo = famiport_payment_ticketing_completion_request.mmkNo
        sequenceNo = famiport_payment_ticketing_completion_request.sequenceNo
        barCodeNo = famiport_payment_ticketing_completion_request.barCodeNo
        orderId = famiport_payment_ticketing_completion_request.orderId

        famiport_order = None
        replyCode = None

        logger.info(u'Processing famiport ticketing completion request. '
                    u'店舗コード: %s, 発券Famiポート番号: %s, 利用日時: %s, 処理通番: %s, 支払番号: %s'
                    % (storeCode, mmkNo, famiport_payment_ticketing_completion_request.ticketingDate, sequenceNo, barCodeNo))

        try:
            try:
                ticketingDate = datetime.datetime.strptime(
                    famiport_payment_ticketing_completion_request.ticketingDate,
                    '%Y%m%d%H%M%S'
                    )
            except ValueError:
                logger.error(u"不正な利用日時です (%s)" % famiport_payment_ticketing_completion_request.ticketingDate)
                raise

            try:
                famiport_order = FamiPortOrder.get_by_barCodeNo(barCodeNo, session=session)
            except NoResultFound:
                logger.error(u'FamiPortOrder not found with barCodeNo=%s' % barCodeNo)
                famiport_order = None

            if famiport_order is not None:
                receipt = famiport_order.get_receipt(barCodeNo)
                if receipt is None:
                    logger.error(u'no FamiPortReceipt record for barcode no: %s' % barCodeNo)
                    resultCode = ResultCodeEnum.OtherError.value
                    replyCode = ReplyCodeEnum.SearchKeyError.value
                    famiport_order = None
                elif _strip_zfill(receipt.shop_code) != storeCode:
                    logger.error(u'shop_code differs (%s != %s)' % (receipt.shop_code, storeCode))
                    resultCode = ResultCodeEnum.OtherError.value
                    replyCode = ReplyCodeEnum.SearchKeyError.value
                    famiport_order = None
                elif receipt.can_completion(now):
                    logger.error(u'settlement error (%s)' % receipt.shop_code)
                    receipt.customer_request_received_at = now

            if famiport_order is not None:
                famiport_order.paid_at = ticketingDate
                famiport_order.issued_at = ticketingDate
                replyCode = ReplyCodeEnum.Normal.value
            else:
                resultCode = ResultCodeEnum.OtherError.value
                replyCode = ReplyCodeEnum.SearchKeyError.value

            famiport_payment_ticketing_completion_response = FamiPortPaymentTicketingCompletionResponse(
                resultCode=resultCode,
                storeCode=storeCode.zfill(6),
                sequenceNo=sequenceNo,
                barCodeNo=barCodeNo,
                orderId=orderId,
                replyCode=replyCode
                )
        except:
            logger.exception(
                u'An exception has occurred at FamiPortPaymentTicketingCancelResponseBuilder.build_response().'
                u'店舗コード: %s , 発券Famiポート番号: %s , 利用日時: %s , 処理通番: %s , 支払番号: %s , 注文ID: %s'
                % (storeCode, mmkNo, famiport_payment_ticketing_completion_request.ticketingDate, sequenceNo, barCodeNo, orderId))
            resultCode = ResultCodeEnum.OtherError.value
            replyCode = ReplyCodeEnum.OtherError.value
            famiport_payment_ticketing_completion_response = FamiPortPaymentTicketingCompletionResponse(
                resultCode=resultCode,
                storeCode=storeCode.zfill(6),
                sequenceNo=sequenceNo,
                barCodeNo=barCodeNo,
                orderId=orderId,
                replyCode=replyCode
                )

        return famiport_payment_ticketing_completion_response


class FamiPortPaymentTicketingCancelResponseBuilder(FamiPortResponseBuilder):
    def build_response(self, famiport_payment_ticketing_cancel_request, session, now):
        famiport_request = famiport_payment_ticketing_cancel_request
        storeCode = _strip_zfill(famiport_request.storeCode)
        famiport_response = FamiPortPaymentTicketingCancelResponse(
            orderId=u'',
            barCodeNo=u'',
            storeCode=storeCode.zfill(6),
            sequenceNo=famiport_request.sequenceNo,
            resultCode=ResultCodeEnum.OtherError.value,
            replyCode=ReplyCodeEnum.OtherError.value,
            )
        try:
            famiport_order = FamiPortOrder.get_by_barCodeNo(
                famiport_request.barCodeNo, session=session)

            if famiport_order is None:  # 検索エラー
                famiport_response.resultCode = ResultCodeEnum.OtherError.value
                famiport_response.replyCode = ReplyCodeEnum.OtherError.value
                return famiport_response

            receipt = famiport_order.get_receipt(famiport_request.barCodeNo)
            if receipt is None:  # バーコードなし
                famiport_response.resultCode = ResultCodeEnum.OtherError.value
                famiport_response.replyCode = ReplyCodeEnum.OtherError.value
            elif _strip_zfill(receipt.shop_code) != storeCode:
                famiport_response.resultCode = ResultCodeEnum.OtherError.value
                famiport_response.replyCode = ReplyCodeEnum.OtherError.value
                famiport_order = None
            elif not receipt.can_cancel(now):  # 入金発券取消が行えない
                famiport_response.resultCode = ResultCodeEnum.OtherError.value
                famiport_response.replyCode = ReplyCodeEnum.OtherError.value
            elif famiport_order.paid_at:  # 支払済
                famiport_response.resultCode = ResultCodeEnum.AlreadyPaidError.value
                famiport_response.replyCode = ReplyCodeEnum.OtherError.value
            elif famiport_order.canceled_at:  # 支払取消済みエラー
                famiport_response.resultCode = ResultCodeEnum.PaymentAlreadyCanceledError.value
                famiport_response.replyCode = ReplyCodeEnum.OtherError.value
            elif famiport_order.issued_at:  # 発券済みエラー
                famiport_response.resultCode = ResultCodeEnum.TicketAlreadyIssuedError.value
                famiport_response.replyCode = ReplyCodeEnum.OtherError.value
            else:  # 正常
                famiport_response.resultCode = ResultCodeEnum.Normal.value
                famiport_response.replyCode = ReplyCodeEnum.Normal.value
                famiport_response.orderId = famiport_order.famiport_order_identifier
                famiport_response.barCodeNo = receipt.barcode_no
                receipt.void_at = now  # 30分破棄処理
        except Exception as err:  # その他の異常
            logger.error(u'famiport order cancel error: {}: {}'.format(
                type(err).__name__, err))
            famiport_response.resultCode = ResultCodeEnum.OtherError.value
            famiport_response.replyCode = ReplyCodeEnum.OtherError.value
        return famiport_response

        # resultCode = ResultCodeEnum.Normal.value
        # storeCode = famiport_payment_ticketing_cancel_request.storeCode
        # mmkNo = famiport_payment_ticketing_cancel_request.mmkNo
        # ticketingDate = None
        # sequenceNo = famiport_payment_ticketing_cancel_request.sequenceNo
        # barCodeNo = famiport_payment_ticketing_cancel_request.barCodeNo

        # try:
        #     try:
        #         ticketingDate = datetime.datetime.strptime(
        #             famiport_payment_ticketing_cancel_request.ticketingDate,
        #             '%Y%m%d%H%M%S'
        #             )
        #     except ValueError:
        #         logger.error(u"不正な利用日時です (%s)" % famiport_payment_ticketing_cancel_request.ticketingDate)
        #         raise
        #     try:
        #         famiport_order = FamiPortOrder.get_by_barCodeNo(barCodeNo, session=session)
        #     except NoResultFound:
        #         logger.error(u'FamiPortOrder not found with barCodeNo=%s' % barCodeNo)
        #         famiport_order = None

        #     if famiport_order is not None:
        #         receipt = famiport_order.get_receipt(barCodeNo)
        #         if receipt.can_cancel(now):
        #             receipt.customer_request_received_at = now
        #         else:
        #             resultCode = ResultCodeEnum.OtherError.value
        #             replyCode = ReplyCodeEnum.OtherError.value
        #             famiport_order = None

        #     orderId = None
        #     replyCode = None
        #     if famiport_order is not None:
        #         orderId = famiport_order.famiport_order_identifier
        #         if famiport_order.paid_at:
        #             replyCode = ReplyCodeEnum.AlreadyPaidError.value
        #         if famiport_order.canceled_at:
        #             replyCode = ReplyCodeEnum.PaymentAlreadyCanceledError.value
        #         if famiport_order.issued_at:
        #             replyCode = ReplyCodeEnum.TicketAlreadyIssuedError.value
        #         # TODO PaymentCancelError
        #         # TODO TicketingCancelError
        #         else:
        #             replyCode = ReplyCodeEnum.Normal.value
        #     else:
        #         resultCode = ResultCodeEnum.OtherError.value
        #         replyCode = ReplyCodeEnum.OtherError.value

        #     famiport_payment_ticketing_cancel_response = FamiPortPaymentTicketingCancelResponse(
        #         resultCode=resultCode,
        #         storeCode=storeCode,
        #         sequenceNo=sequenceNo,
        #         barCodeNo=barCodeNo,
        #         orderId=orderId,
        #         replyCode=replyCode
        #         )
        # except Exception:
        #     logger.exception(
        #         u'an exception has occurred at FamiPortPaymentTicketingCancelResponseBuilder.build_response(). ' \
        #         u'店舗コード: %s , 発券Famiポート番号: %s , 利用日時: %s , 処理通番: %s , 支払番号: %s' \
        #         % (storeCode, mmkNo, famiport_payment_ticketing_cancel_request.ticketingDate, sequenceNo, barCodeNo)
        #         )
        #     famiport_payment_ticketing_cancel_response = FamiPortPaymentTicketingCancelResponse(
        #         resultCode=resultCode,
        #         storeCode=storeCode,
        #         sequenceNo=sequenceNo,
        #         barCodeNo=barCodeNo,
        #         replyCode=replyCode
        #         )
        # return famiport_payment_ticketing_cancel_response


class FamiPortInformationResponseBuilder(FamiPortResponseBuilder):

    def build_response(self, famiport_information_request, session, now):
        """案内通信

        デフォルトは「案内なし(正常)」
        FamiPortInformationMessageにWithInformationに対応するmessageがあれば「案内あり(正常)」としてメッセージを表示する。
        FamiPortInformationMessageにServiceUnavailableに対応するmessageがあれば「サービス不可時案内」としてメッセージを表示する。
        途中でエラーが起こった場合は「その他エラー」としてメッセージを表示する。

        :param famiport_information_request:
        :return: FamiPortInformationResponse
        """
        famiport_request = famiport_information_request
        famiport_response = FamiPortInformationResponse()
        famiport_response.infoKubun = famiport_request.infoKubun
        try:
            if famiport_request.infoKubun == InfoKubunEnum.DirectSales.value:  # 直販
                famiport_response.resultCode = InformationResultCodeEnum.ServiceUnavailable.value
                famiport_response.infoMessage = u'現在お取り扱いしておりません。'
                return famiport_response

            elif famiport_request.infoKubun == InfoKubunEnum.Reserved.value:  # 予済
                famiport_order = None
                if famiport_request.reserveNumber:
                    famiport_order = None
                    try:
                        famiport_order = session \
                            .query(FamiPortOrder) \
                            .filter(FamiPortOrder.reserve_number == famiport_request.reserveNumber) \
                            .filter(FamiPortOrder.invalidated_at == None) \
                            .one()
                    except NoResultFound:
                        pass

                # 条件を作る.
                # 仮に famiport_order がなかったとしてもクライアントコードで引いて来れるメッセージは表示しなければならない
                if famiport_order is None:
                    criteria = [
                        lambda q: \
                            q.filter(
                                FamiPortInformationMessage.event_code_1 == None,
                                FamiPortInformationMessage.event_code_2 == None,
                                FamiPortInformationMessage.performance_code == None,
                                FamiPortInformationMessage.sales_segment_code == None,
                                FamiPortInformationMessage.reserve_number == None
                                )
                            ]
                    if famiport_request.kogyoCode:
                        criteria += [
                            lambda q: \
                                q.filter(
                                    FamiPortInformationMessage.event_code_1 == famiport_request.kogyoCode,
                                    FamiPortInformationMessage.event_code_2 == famiport_request.kogyoSubCode,
                                    FamiPortInformationMessage.performance_code == None,
                                    FamiPortInformationMessage.sales_segment_code == None,
                                    FamiPortInformationMessage.reserve_number == None
                                    ),
                            lambda q: \
                                q.filter(
                                    FamiPortInformationMessage.event_code_1 == famiport_request.kogyoCode,
                                    FamiPortInformationMessage.event_code_2 == famiport_request.kogyoSubCode,
                                    FamiPortInformationMessage.performance_code == famiport_request.koenCode,
                                    FamiPortInformationMessage.sales_segment_code == None,
                                    FamiPortInformationMessage.reserve_number == None
                                    ),
                            lambda q: \
                                q.filter(
                                    FamiPortInformationMessage.event_code_1 == famiport_request.kogyoCode,
                                    FamiPortInformationMessage.event_code_2 == famiport_request.kogyoSubCode,
                                    FamiPortInformationMessage.performance_code == famiport_request.koenCode,
                                    FamiPortInformationMessage.sales_segment_code == famiport_request.uketsukeCode,
                                    FamiPortInformationMessage.reserve_number == None
                                    ),
                            ]
                else:
                    criteria = [
                        lambda q: \
                            q.filter(
                                FamiPortInformationMessage.event_code_1 == None,
                                FamiPortInformationMessage.event_code_2 == None,
                                FamiPortInformationMessage.performance_code == None,
                                FamiPortInformationMessage.sales_segment_code == None,
                                FamiPortInformationMessage.reserve_number == None
                                ),
                        lambda q: \
                            q.filter(
                                FamiPortInformationMessage.event_code_1 == famiport_order.evenet_code_1,
                                FamiPortInformationMessage.event_code_2 == famiport_order.event_code_2,
                                FamiPortInformationMessage.performance_code == None,
                                FamiPortInformationMessage.sales_segment_code == None,
                                FamiPortInformationMessage.reserve_number == None
                                ),
                        lambda q: \
                            q.filter(
                                FamiPortInformationMessage.event_code_1 == famiport_order.evenet_code_1,
                                FamiPortInformationMessage.event_code_2 == famiport_order.event_code_2,
                                FamiPortInformationMessage.performance_code == famiport_order.performance_code,
                                FamiPortInformationMessage.sales_segment_code == None,
                                FamiPortInformationMessage.reserve_number == None
                                ),
                        lambda q: \
                            q.filter(
                                FamiPortInformationMessage.event_code_1 == famiport_order.evenet_code_1,
                                FamiPortInformationMessage.event_code_2 == famiport_order.event_code_2,
                                FamiPortInformationMessage.performance_code == famiport_order.performance_code,
                                FamiPortInformationMessage.sales_segment_code == famiport_order.sales_segment_code,
                                FamiPortInformationMessage.reserve_number == None
                                ),
                        lambda q: \
                            q.filter(
                                FamiPortInformationMessage.event_code_1 == famiport_order.evenet_code_1,
                                FamiPortInformationMessage.event_code_2 == famiport_order.event_code_2,
                                FamiPortInformationMessage.performance_code == famiport_order.performance_code,
                                FamiPortInformationMessage.sales_segment_code == famiport_order.sales_segment_code,
                                FamiPortInformationMessage.reserve_number == famiport_order.reserve_number
                                ),
                        ]

                info_message = None
                for c in criteria:
                    info_messages = sorted(
                        c(session.query(FamiPortInformationMessage)),
                        key=lambda r: r.result_code != InformationResultCodeEnum.ServiceUnavailable.value
                        )
                    if len(info_messages) > 0:
                        info_message = info_messages[0]
                        break

                if info_message is not None:  # メッセージあり
                    famiport_response.resultCode = str_or_blank(
                        info_message.result_code, padding_count=2, fillvalue='0')
                    famiport_response.infoMessage = info_message.message
                    return famiport_response
                else:  # メッセージなし
                    famiport_response.resultCode = InformationResultCodeEnum.NoInformation.value
                    famiport_response.infoMessage = u''
                    return famiport_response
            else:
                raise FamiPortError('unknown infoKubun: {}'.format(famiport_request.infoKubun))
        except Exception as err:  # その他エラー
            logger.exception('FamiPort Information Error: {}: {}'.format(type(err).__name__, err))
            famiport_response.resultCode = InformationResultCodeEnum.OtherError.value
            famiport_response.infoMessage = u'異常が発生しました'
            return famiport_response


class FamiPortCustomerInformationResponseBuilder(FamiPortResponseBuilder):

    def build_response(self, famiport_customer_information_request, session, now):
        storeCode = _strip_zfill(famiport_customer_information_request.storeCode)
        mmkNo = famiport_customer_information_request.mmkNo
        ticketingDate = None
        sequenceNo = famiport_customer_information_request.sequenceNo
        barCodeNo = famiport_customer_information_request.barCodeNo
        orderId = famiport_customer_information_request.orderId

        famiport_order = None
        try:
            try:
                ticketingDate = datetime.datetime.strptime(
                    famiport_customer_information_request.ticketingDate,
                    '%Y%m%d%H%M%S'
                    )
            except ValueError:
                logger.error(u"不正な利用日時です (%s)" % famiport_customer_information_request.ticketingDate)
                raise

            try:
                famiport_order = FamiPortOrder.get_by_barCodeNo(barCodeNo, session=session)
            except NoResultFound:
                logger.error(u'FamiPortOrder not found with barCodeNo=%s' % barCodeNo)
                famiport_order = None

            if famiport_order is not None:
                receipt = famiport_order.get_receipt(barCodeNo)
                if receipt.can_customer(now):
                    resultCode = ResultCodeEnum.OtherError.value
                    replyCode = ReplyCodeEnum.SearchKeyError.value
                    receipt.customer_request_received_at = now
                else:
                    famiport_order = None

            if famiport_order is not None:
                name = famiport_order.customer_name
                # TODO Make sure where to get memberId
                memberId = famiport_order.customer_member_id
                address1 = famiport_order.customer_address_1
                address2 = famiport_order.customer_address_2
                # TODO Make sure where to get identifyNo
                identifyNo = famiport_order.customer_identify_no

                famiport_customer_information_respose = FamiPortCustomerInformationResponse(
                    resultCode=ResultCodeEnum.Normal.value,
                    replyCode=ReplyCodeEnum.Normal.value,
                    name=name,
                    memberId=memberId,
                    address1=address1,
                    address2=address2,
                    identifyNo=identifyNo
                    )
                famiport_customer_information_respose.set_encryptKey(orderId)
            else:
                famiport_customer_information_respose = FamiPortCustomerInformationResponse(
                    resultCode=ResultCodeEnum.OtherError.value,
                    replyCode=ReplyCodeEnum.CustomerNamePrintInformationError.value
                    )
        except Exception:
            logger.exception(
                u'an exception has occurred at FamiPortPaymentTicketingCancelResponseBuilder.build_response(). '
                u'店舗コード: %s , 発券Famiポート番号: %s , 利用日時: %s , 処理通番: %s , 支払番号: %s , 注文ID: %s'
                % (storeCode, mmkNo, ticketingDate, sequenceNo, barCodeNo, orderId)
                )
            famiport_customer_information_respose = FamiPortCustomerInformationResponse(
                resultCode=ResultCodeEnum.OtherError.value,
                replyCode=ReplyCodeEnum.OtherError.value
                )
        return famiport_customer_information_respose


class FamiPortRefundEntryResponseBuilder(FamiPortResponseBuilder):
    def build_response(self, famiport_refund_entry_request, session, now):
        famiport_refund_entry_response = FamiPortRefundEntryResponse(
            businessFlg=famiport_refund_entry_request.businessFlg,
            textTyp=famiport_refund_entry_request.textTyp,
            entryTyp=famiport_refund_entry_request.entryTyp,
            shopNo=famiport_refund_entry_request.shopNo,
            registerNo=famiport_refund_entry_request.registerNo,
            timeStamp=famiport_refund_entry_request.timeStamp,
            )
        barcode_numbers = famiport_refund_entry_request.barcode_numbers
        refund_entries = [
            (
                barcode_number,
                (
                    session.query(FamiPortRefundEntry) \
                        .options(orm.joinedload(FamiPortRefundEntry.famiport_ticket)) \
                        .join(FamiPortRefundEntry.famiport_ticket) \
                        .filter(FamiPortTicket.barcode_number == barcode_number) \
                        .first() \
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
                repayment = u'{0:06}'.format(refund_entry.ticket_payment + refund_entry.ticketing_fee + refund_entry.system_fee + refund_entry.other_fees)
                refund_start = six.text_type(refund_entry.famiport_refund.start_at.strftime('%Y%m%d'))
                refund_end = six.text_type(refund_entry.famiport_refund.end_at.strftime('%Y%m%d'))
                ticket_typ = u'{0}'.format(refund_entry.famiport_ticket.type)
                charge = u'{0:06}'.format(refund_entry.ticketing_fee + refund_entry.system_fee + refund_entry.other_fees)
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

    def __init__(self, famiport_response, xml_encoding='Shift_JIS', encoding='CP932', crypted_part_encoding='UTF-8'):
        self.famiport_crypt = None
        if famiport_response.encrypt_key:
            self.famiport_crypt = FamiPortCrypt(famiport_response.encrypt_key, encoding=crypted_part_encoding)
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
                    element.text = self.famiport_crypt.encrypt(attribute_value)

        for attribute_name, element_name in obj._serialized_collection_attrs:
            attribute_value = getattr(obj, attribute_name)
            for value in attribute_value:
                element = etree.SubElement(root, element_name)
                self._build_xmlTree(element, value)

        return root
