# -*- coding: utf-8 -*-
import six
import logging
import datetime
from decimal import Decimal
from lxml import etree
from sqlalchemy import orm
from sqlalchemy.orm.exc import NoResultFound
from zope.interface import implementer

from ..exc import FamiPortError
from .exceptions import (
    FamiPortRequestTypeError,
    FamiPortResponseBuilderLookupError,
    FamiPortInvalidResponseError,
    )
from altair.app.ticketing.famiport.utils import FamiPortCrypt, str_or_blank
from ..models import (
    FamiPortOrder,
    FamiPortReceipt,
    FamiPortInformationMessage,
    FamiPortRefundEntry,
    FamiPortClient,
    FamiPortTicket,
    FamiPortOrderType,
    FamiPortReceiptType,
    FamiPortOrderTicketNoSequence,
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
    FamiPortRefundEntryResponseErrorCodeEnum,
    FamiPortRefundEntryResponseTextTypeEnum,
    FamiPortRefundEntryResponseResultCodeEnum,
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

        unserialized_attrs = getattr(famiport_request, '_unserialized_attrs', None)
        if unserialized_attrs is None:
            for key, value in famiport_request_dict.items():
                if crypto and key in encrypt_fields:
                    try:
                        value = crypto.decrypt(value)
                    except Exception as err:
                        raise err.__class__(
                            'decrypt error: {}: key={}, value={}, secret={}'.format(
                                err.message, key, value, barcode_no))
                setattr(famiport_request, key, value)
        else:
            for attribute_name, key in unserialized_attrs:
                value = famiport_request_dict.get(key)
                if value is not None and crypto and attribute_name in encrypt_fields:
                    try:
                        value = crypto.decrypt(value)
                    except Exception as err:
                        raise err.__class__(
                            'decrypt error: {}: {}'.format(err.message, value))
                setattr(famiport_request, attribute_name, value)
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
    def __init__(self, registry):
        request = registry

    def build_response(self, famiport_request=None):
        pass

    def is_normal_response(self, resultCode, replyCode):
        if resultCode == ResultCodeEnum.Normal.value and replyCode == ReplyCodeEnum.Normal.value:
            return True
        else:
            return False


class FamiPortReservationInquiryResponseBuilder(FamiPortResponseBuilder):
    def build_response(self, famiport_reservation_inquiry_request, session, now, request):
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

        resultCode = ResultCodeEnum.Normal.value
        replyCode = ReplyCodeEnum.Normal.value
        replyClass = None
        try:
            try:
                ticketingDate = datetime.datetime.strptime(
                    famiport_reservation_inquiry_request.ticketingDate,
                    '%Y%m%d%H%M%S'
                    )
            except ValueError:
                logger.exception(u"不正な利用日時です (%s)" % famiport_reservation_inquiry_request.ticketingDate)
                raise

            try:
                famiport_receipt = FamiPortReceipt.get_by_reserve_number(reserveNumber, session=session)
            except NoResultFound:
                logger.info(u'FamiPortOrder not found with reserveNumber=%s' % reserveNumber)
                replyCode = ReplyCodeEnum.SearchKeyError.value
                famiport_receipt = None

            if famiport_receipt is not None:
                famiport_order = famiport_receipt.famiport_order
                playGuideId = famiport_order.famiport_client.code
                if famiport_receipt.canceled_at is not None:
                    replyCode = ReplyCodeEnum.SearchKeyError.value
                    famiport_receipt = None
                elif famiport_receipt.payment_request_received_at is not None and \
                   famiport_receipt.completed_at is None:
                    if famiport_receipt.made_reissueable_at is not None:
                        logger.info(u'FamiPortReceipt(reserve_number=%s) has been made reissueable (%s).' % (famiport_receipt.reserve_number, famiport_receipt.made_reissueable_at))
                    else:
                        logger.warning(u'FamiPortReceipt(reserve_number=%s) already got the corresponding payment-ticketing request received (%s).' % (famiport_receipt.reserve_number, famiport_receipt.payment_request_received_at))
                        replyCode = ReplyCodeEnum.TicketAlreadyIssuedError.value
                        famiport_receipt = None
                elif famiport_receipt.payment_request_received_at is not None and \
                     famiport_receipt.completed_at is not None:
                    if famiport_receipt.made_reissueable_at is not None:
                        logger.info(u'FamiPortReceipt(reserve_number=%s) has been made reissueable (%s).' % (famiport_receipt.reserve_number, famiport_receipt.made_reissueable_at))
                    else:
                        logger.warning(u'FamiPortReceipt(reserve_number=%s) is already completed (%s).' % (famiport_receipt.reserve_number, famiport_receipt.completed_at))
                        replyCode = ReplyCodeEnum.AlreadyPaidError.value
                        famiport_receipt = None
                elif famiport_order.auth_number is not None and famiport_order.auth_number != authNumber:
                    logger.error(u'authNumber differs (%s != %s)' % (famiport_order.auth_number, authNumber))
                    replyCode = ReplyCodeEnum.SearchKeyError.value
                    famiport_receipt = None
                else:
                    if famiport_receipt.type == FamiPortReceiptType.CashOnDelivery.value:
                        if famiport_order.payment_start_at is not None and  \
                           famiport_order.payment_start_at > ticketingDate:
                            logger.warning(u'ticketingDate is earlier than payment_start_at (%s)' % (famiport_order.payment_start_at, ))
                            replyCode = ReplyCodeEnum.SearchKeyError.value
                            famiport_receipt = None
                        elif famiport_order.payment_due_at is not None and \
                             famiport_order.payment_due_at < ticketingDate:
                            if famiport_receipt.made_reissueable_at is not None:
                                logger.warning(u'ticketingDate is later than payment_due_at (%s) but FamiPortReceipt(reserve_number=%s) has been made reissueable (%s).' % (famiport_order.payment_due_at, famiport_receipt.reserve_number, famiport_receipt.made_reissueable_at))
                            else:
                                logger.warning(u'ticketingDate is later than payment_due_at (%s)' % (famiport_order.payment_due_at, ))
                                replyCode = ReplyCodeEnum.PaymentDueError.value
                                famiport_receipt = None
                        else:
                            replyClass = ReplyClassEnum.CashOnDelivery.value
                            if famiport_receipt.completed_at is not None:
                                if famiport_receipt.made_reissueable_at is not None:
                                    logger.info(u'FamiPortReceipt(reserve_number=%s) has been made reissueable (%s).' % (famiport_receipt.reserve_number, famiport_receipt.made_reissueable_at))
                                else:
                                    raise FamiPortInvalidResponseError('invalid FamiPortResponse')
                    elif famiport_receipt.type == FamiPortReceiptType.Payment.value:
                        if famiport_order.payment_start_at is not None and  \
                           famiport_order.payment_start_at > ticketingDate:
                            logger.warning(u'ticketingDate is earlier than payment_start_at (%s)' % (famiport_order.payment_start_at, ))
                            replyCode = ReplyCodeEnum.SearchKeyError.value
                            famiport_receipt = None
                        elif famiport_order.payment_due_at is not None and \
                             famiport_order.payment_due_at < ticketingDate:
                            logger.warning(u'ticketingDate is later than payment_due_at (%s)' % (famiport_order.payment_due_at, ))
                            replyCode = ReplyCodeEnum.PaymentDueError.value
                            famiport_receipt = None
                        else:
                            if famiport_order.type == FamiPortOrderType.PaymentOnly.value:
                                replyClass = ReplyClassEnum.PrepaymentOnly.value
                            else:
                                replyClass = ReplyClassEnum.Prepayment.value
                            if famiport_receipt.completed_at is not None:
                                if famiport_receipt.made_reissueable_at is not None:
                                    logger.info(u'FamiPortReceipt(reserve_number=%s) has been made reissueable (%s).' % (famiport_receipt.reserve_number, famiport_receipt.made_reissueable_at))
                                else:
                                    raise FamiPortInvalidResponseError('invalid FamiPortResponse')
                    elif famiport_receipt.type == FamiPortReceiptType.Ticketing.value:

                        if famiport_order.ticketing_start_at is not None and  \
                           famiport_order.ticketing_start_at > ticketingDate:
                            logger.warning(u'ticketingDate is earlier than ticketing_start_at (%s)' % (famiport_order.ticketing_start_at, ))
                            replyCode = ReplyCodeEnum.TicketingBeforeStartError.value
                            famiport_receipt = None
                        elif famiport_order.ticketing_end_at is not None and \
                             famiport_order.ticketing_end_at < ticketingDate:
                            if famiport_receipt.made_reissueable_at is not None:
                                logger.warning(u'ticketingDate is later than ticketing_end_at (%s) but FamiPortReceipt(reserve_number=%s) has been made reissueable (%s).' % (famiport_order.ticketing_end_at, famiport_receipt.reserve_number, famiport_receipt.made_reissueable_at))
                            else:
                                logger.warning(u'ticketingDate is later than ticketing_end_at (%s)' % (famiport_order.ticketing_end_at, ))
                                replyCode = ReplyCodeEnum.TicketingDueError.value
                                famiport_receipt = None
                        else:
                            replyClass = ReplyClassEnum.Paid.value
                            if famiport_receipt.completed_at is not None:
                                if famiport_receipt.made_reissueable_at is not None:
                                    logger.info(u'FamiPortReceipt(reserve_number=%s) has been made reissueable (%s).' % (famiport_receipt.reserve_number, famiport_receipt.made_reissueable_at))
                                else:
                                    raise FamiPortInvalidResponseError('invalid FamiPortResponse')
                    else:
                        raise AssertionError('invalid FamiPortReceiptType: %d' % famiport_receipt.type)

            if famiport_receipt is not None:
                famiport_receipt.shop_code = storeCode
                if famiport_receipt.made_reissueable_at is None:
                    famiport_receipt.barcode_no = FamiPortOrderTicketNoSequence.get_next_value(session)
                famiport_receipt.mark_inquired(now, request)
                session.add(famiport_receipt)
                session.commit()

            if famiport_receipt is not None:
                famiport_order = famiport_receipt.famiport_order
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

                if famiport_receipt.made_reissueable_at is None:
                    totalAmount, ticketPayment, systemFee, ticketingFee = famiport_receipt.calculate_total_and_fees()
                else:
                    totalAmount = ticketPayment = systemFee = ticketingFee = Decimal(0)

                barCodeNo = famiport_receipt.barcode_no
                ticketCountTotal = str_or_blank(famiport_order.ticket_total_count)
                ticketCount = str_or_blank(famiport_order.ticket_count)
                kogyoName = famiport_order.famiport_performance.name
                name = famiport_order.customer_name if not famiport_order.customer_name_input else u''

                totalAmount = str_or_blank(totalAmount, 8, fillvalue='0')
                ticketPayment = str_or_blank(ticketPayment, 8, fillvalue='0')
                systemFee = str_or_blank(systemFee, 8, fillvalue='0')
                ticketingFee = str_or_blank(ticketingFee, 8, fillvalue='0')
                replyClass = str_or_blank(replyClass)
                replyCode = ReplyCodeEnum.Normal.value

            famiport_reservation_inquiry_response = FamiPortReservationInquiryResponse(
                _request=famiport_reservation_inquiry_request,
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
            replyClass = None
            replyCode = ReplyCodeEnum.OtherError.value
            famiport_reservation_inquiry_response = FamiPortReservationInquiryResponse(
                _request=famiport_reservation_inquiry_request,
                resultCode=resultCode,
                replyClass=replyClass,
                replyCode=replyCode,
                playGuideId=playGuideId
                )

        return famiport_reservation_inquiry_response


class FamiPortPaymentTicketingResponseBuilder(FamiPortResponseBuilder):
    def __init__(self, registry, moratorium=datetime.timedelta(seconds=1800)):
        super(FamiPortPaymentTicketingResponseBuilder, self).__init__(registry)
        # 入金期限を手続き中に過ぎてしまった場合に考慮される、入金期限からの猶予期間
        self.moratorium = moratorium

    def build_response(self, famiport_payment_ticketing_request, session, now, request):
        """入金発券要求からバーコードを印字するための情報を返す
        """
        famiport_order = None
        resultCode = ResultCodeEnum.Normal.value
        replyCode = ReplyCodeEnum.Normal.value
        barCodeNo = famiport_payment_ticketing_request.barCodeNo
        storeCode = _strip_zfill(famiport_payment_ticketing_request.storeCode)
        mmkNo = famiport_payment_ticketing_request.mmkNo
        sequenceNo = famiport_payment_ticketing_request.sequenceNo
        ticketingDate = ''

        orderId = None
        replyClass = None
        playGuideId = famiport_payment_ticketing_request.playGuideId
        playGuideName = None
        orderTicketNo = None
        exchangeTicketNo = None
        ticketingStart = None
        ticketingEnd = None
        totalAmount = None
        ticketPayment = None
        systemFee = None
        ticketingFee = None
        ticketingCountTotal = None
        ticketCount = None
        kogyoName = None
        koenDate = None
        tickets = None

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
                logger.exception(u"不正な利用日時です (%s)" % famiport_payment_ticketing_request.ticketingDate)
                raise

            famiport_receipt = None
            try:
                famiport_receipt = FamiPortReceipt.get_by_barcode_no(barCodeNo, session=session)
            except NoResultFound:
                # Famiポートと電子バーコードの両方で操作が行われた時に最初に来た入金発券要求リクエストで処理が通るので
                # 後から来た入金発券要求リクエストのバーコード番号から予約は見つかりません。
                # ユーザーは最初行った操作アクセスで入金・発券を行えているのでアラートに出しません。TKT-7860
                logger.warn(u'FamiPortOrder not found with barCodeNo=%s', barCodeNo)
                replyCode = ReplyCodeEnum.SearchKeyError.value

            if famiport_receipt is not None:
                famiport_order = famiport_receipt.famiport_order
                playGuideId = famiport_order.famiport_client.code
                playGuideName = famiport_order.famiport_client.name
                if famiport_receipt.canceled_at is not None:
                    replyCode = ReplyCodeEnum.SearchKeyError.value
                    famiport_receipt = None
                elif famiport_receipt is None or _strip_zfill(famiport_receipt.shop_code) != storeCode:
                    logger.error(u'shop_code differs (%s != %s)' % (famiport_receipt.shop_code, storeCode))
                    replyCode = ReplyCodeEnum.SearchKeyError.value
                    famiport_receipt = None
                elif famiport_receipt.payment_request_received_at is not None:
                    if famiport_receipt.completed_at is not None:
                        logger.warning(u'FamiPortReceipt(reserve_number=%s, barcode_no=%s) is already paid or issued (%s).' % (famiport_receipt.reserve_number, famiport_receipt.barcode_no, famiport_receipt.completed_at))
                        replyCode = ReplyCodeEnum.AlreadyPaidError.value
                        famiport_receipt = None
                    else:
                        logger.warning(u'FamiPortReceipt(reserve_number=%s, barcode_no=%s) already got the corresponding payment-ticketing request received (%s).' % (famiport_receipt.reserve_number, famiport_receipt.barcode_no, famiport_receipt.payment_request_received_at))
                        replyCode = ReplyCodeEnum.TicketAlreadyIssuedError.value
                        famiport_receipt = None
                elif not famiport_receipt.can_payment(now):
                    logger.error(u'FamiPortReceipt(reserve_number=%s, barcode_no=%s) is not marked inquired or invalid status.' % (famiport_receipt.reserve_number, famiport_receipt.barcode_no, ))
                    replyCode = ReplyCodeEnum.SearchKeyError.value
                    famiport_receipt = None

            # validate the request
            if famiport_receipt is not None:
                receipt_type = famiport_receipt.type
                famiport_order = famiport_receipt.famiport_order
                if receipt_type in (FamiPortReceiptType.CashOnDelivery.value, FamiPortReceiptType.Payment.value):
                    if famiport_receipt.completed_at is not None:
                        if famiport_receipt.made_reissueable_at is not None:
                            logger.info(u'tickets for order are already issued at %s' % (famiport_receipt.completed_at, ))
                        else:
                            replyCode = ReplyCodeEnum.AlreadyPaidError.value
                            famiport_receipt = None
                    else:
                        if famiport_order.payment_start_at is not None \
                           and famiport_order.payment_start_at > ticketingDate:
                            logger.warning(u'ticketingDate (%s) is earlier than payment_start_at (%s)' % (
                                ticketingDate,
                                famiport_order.payment_start_at,
                                ))
                            replyCode = ReplyCodeEnum.SearchKeyError.value
                            famiport_receipt = None
                        elif famiport_order.payment_due_at is not None \
                                and famiport_order.payment_due_at + self.moratorium < ticketingDate:
                            logger.warning(u'ticketingDate (%s) is later than payment_due_at (%s) + moratorium (%r)' % (
                                ticketingDate, famiport_order.payment_due_at, self.moratorium))
                            replyCode = ReplyCodeEnum.PaymentDueError.value
                            famiport_receipt = None
                if famiport_receipt is not None and \
                   receipt_type in (FamiPortReceiptType.CashOnDelivery.value, FamiPortReceiptType.Ticketing.value):
                    if famiport_order.type == FamiPortOrderType.Payment.value and famiport_order.payment_famiport_receipt.completed_at is None: # 後日発券で未入金
                        logger.info(u'tickets for order are not paid yet')
                        replyCode = ReplyCodeEnum.SearchKeyError.value # 未入金の状態で後日発券しようとしている
                        famiport_receipt = None
                    elif famiport_receipt.completed_at is not None:
                        if famiport_receipt.made_reissueable_at is not None:
                            logger.info(u'tickets for order are already issued at %s' % (famiport_receipt.completed_at, ))
                        else:
                            logger.warning(u'tickets for order are already issued at %s' % (famiport_order.issued_at, ))
                            replyCode = ReplyCodeEnum.TicketAlreadyIssuedError.value
                            famiport_receipt = None
                    elif famiport_order.ticketing_start_at is not None \
                            and famiport_order.ticketing_start_at > ticketingDate:
                        logger.warning(u'ticketingDate (%s) is earlier than ticketing_start_at (%s)' % (ticketingDate, famiport_order.ticketing_start_at,))
                        replyCode = ReplyCodeEnum.TicketingBeforeStartError.value
                        famiport_receipt = None
                    elif famiport_order.ticketing_end_at is not None \
                            and famiport_order.ticketing_end_at + self.moratorium < ticketingDate:
                        if famiport_receipt.made_reissueable_at is not None:
                            logger.warning(u'ticketingDate (%s) is later than ticketing_end_at (%s) but FamiPortReceipt(reserve_number=%s, barcode_no=%s) has been made reissueable (%s).' % (ticketingDate, famiport_order.ticketing_end_at, famiport_receipt.reserve_number, famiport_receipt.barcode_no, famiport_receipt.made_reissueable_at))
                        else:
                            logger.warning(u'ticketingDate (%s) is later than ticketing_end_at (%s) + moratorium (%r)' % (
                                ticketingDate, famiport_order.ticketing_end_at, self.moratorium))
                            replyCode = ReplyCodeEnum.TicketingDueError.value
                            famiport_receipt = None

            if famiport_receipt is not None:
                famiport_order = famiport_receipt.famiport_order
                orderTicketNo = barCodeNo
                if famiport_order.type == FamiPortOrderType.CashOnDelivery.value:
                    replyClass = ReplyClassEnum.CashOnDelivery.value
                    exchangeTicketNo = None
                elif famiport_order.type == FamiPortOrderType.Payment.value:
                    if famiport_receipt.type == FamiPortReceiptType.Payment.value:
                        replyClass = ReplyClassEnum.Prepayment.value
                    elif famiport_receipt.type == FamiPortReceiptType.Ticketing.value:
                        replyClass = ReplyClassEnum.Paid.value
                        orderTicketNo = None
                        ticketingStart = None
                        ticketingEnd = None
                    else:
                        raise ValueError(u'unknown receipt type: %r' % famiport_receipt.type)
                    if famiport_order.ticketing_start_at:
                        ticketingStart = famiport_order.ticketing_start_at.strftime("%Y%m%d%H%M%S")
                    if famiport_order.ticketing_end_at:
                        ticketingEnd = famiport_order.ticketing_end_at.strftime("%Y%m%d%H%M%S")
                    exchangeTicketNo = famiport_order.ticketing_famiport_receipt.reserve_number
                elif famiport_order.type == FamiPortOrderType.Ticketing.value:
                    replyClass = ReplyClassEnum.Paid.value
                    exchangeTicketNo = famiport_receipt.reserve_number
                    orderTicketNo = None
                    ticketingStart = None
                    ticketingEnd = None
                elif famiport_order.type == FamiPortOrderType.PaymentOnly.value:
                    replyClass = ReplyClassEnum.PrepaymentOnly.value
                    exchangeTicketNo = None
                else:
                    raise ValueError(u'unknown order type: %r' % famiport_order.type)

                if famiport_receipt.made_reissueable_at is None:
                    totalAmount, ticketPayment, systemFee, ticketingFee = famiport_receipt.calculate_total_and_fees()
                else:
                    totalAmount = ticketPayment = systemFee = ticketingFee = Decimal(0)

                orderId = famiport_receipt.famiport_order_identifier
                totalAmount = str_or_blank(totalAmount, 8, fillvalue='0')
                ticketPayment = str_or_blank(ticketPayment, 8, fillvalue='0')
                systemFee = str_or_blank(systemFee, 8, fillvalue='0')
                ticketingFee = str_or_blank(ticketingFee, 8, fillvalue='0')
                ticketingCountTotal = str_or_blank(famiport_order.ticket_total_count)
                exchangeTicketNo = str_or_blank(exchangeTicketNo)
                ticketCount = str_or_blank(famiport_order.ticket_count)
                kogyoName = famiport_order.famiport_performance.name

                start_at = famiport_order.famiport_performance.start_at
                koenDate = start_at.strftime('%Y%m%d%H%M') if start_at else '999999999999'
                tickets = famiport_order.famiport_tickets

                famiport_ticket_responses = []
                if replyClass == ReplyClassEnum.Prepayment.value:  # 前払い後日発券の前払い時はチケット情報は不要
                    pass
                elif replyClass == ReplyClassEnum.PrepaymentOnly.value:  # 前払いのみの場合はチケット情報は1つのみ送る
                    ftr = self._create_famiport_ticket_response_for_payment_sheet(famiport_order)
                    if ftr is not None:
                        famiport_ticket_responses.append(ftr)
                else:  # それ以外ではチケット情報をすべて送る
                    for ticket in tickets:
                        ftr = self._create_famiport_ticket_response(ticket)
                        famiport_ticket_responses.append(ftr)

                if self.is_normal_response(resultCode, replyCode):
                    # 正常なレスポンスを返せたらpayment_request_received_atを立てる
                    famiport_receipt.mark_payment_request_received(now, request)
                    session.commit()
                else:
                    # tkt904:エラーが起きているのに正常レスポンスとして返えそうとしてしまっているケース
                    logger.error('invalid FamiPortResponse.(processing reserve_number={})'.format(famiport_receipt.reserve_number))
                    raise FamiPortInvalidResponseError('invalid FamiPortResponse')

                resultCode = str_or_blank(resultCode)
                replyCode = str_or_blank(replyCode)
                replyClass = str_or_blank(replyClass)
                ticketingStart = str_or_blank(ticketingStart)
                ticketingEnd = str_or_blank(ticketingEnd)

                famiport_payment_ticketing_response = FamiPortPaymentTicketingResponse(
                    _request=famiport_payment_ticketing_request,
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
                    _request=famiport_payment_ticketing_request,
                    resultCode=str_or_blank(resultCode),
                    replyCode=str_or_blank(replyCode),
                    storeCode=storeCode.zfill(6),
                    playGuideId=playGuideId,
                    playGuideName=playGuideName,
                    sequenceNo=sequenceNo,
                    barCodeNo=barCodeNo,
                    orderId=orderId,
                    replyClass=str_or_blank(replyClass)
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
                _request=famiport_payment_ticketing_request,
                resultCode=str_or_blank(resultCode),
                replyCode=str_or_blank(replyCode),
                playGuideId=playGuideId,
                sequenceNo=sequenceNo,
                storeCode=storeCode.zfill(6)
                )
        return famiport_payment_ticketing_response

    def _create_famiport_ticket_response(self, famiport_ticket):
        ftr = FamiPortTicketResponse()
        ftr.barCodeNo = famiport_ticket.barcode_number
        ftr.ticketClass = str(famiport_ticket.type)
        ftr.templateCode = famiport_ticket.template_code
        ftr.ticketData = u'<?xml version="1.0" encoding="Shift_JIS" ?>' + famiport_ticket.data
        return ftr

    def _create_famiport_ticket_response_for_payment_sheet(self, famiport_order):
        if famiport_order.payment_sheet_text:
            ftr = FamiPortTicketResponse()
            ftr.barCodeNo = None
            ftr.ticketClass = None
            ftr.templateCode = None
            ftr.ticketData = famiport_order.payment_sheet_text
        else:
            ftr = None
        return ftr


class FamiPortPaymentTicketingCompletionResponseBuilder(FamiPortResponseBuilder):
    def __init__(self, registry):
        super(FamiPortPaymentTicketingCompletionResponseBuilder, self).__init__(registry)
        try:
            self.sp_shop_code = _strip_zfill(registry.settings.get('altair.famima.sp_shop_code'))
        except AttributeError as e:
            logger.error('altair.famima.sp_shop_code is not defined in the loaded config.')
            raise e

    def build_response(self, famiport_payment_ticketing_completion_request, session, now, request):
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
                logger.exception(u"不正な利用日時です (%s)" % famiport_payment_ticketing_completion_request.ticketingDate)
                raise

            try:
                famiport_receipt = FamiPortReceipt.get_by_barcode_no(barCodeNo, session=session)
            except NoResultFound:
                logger.exception(u'FamiPortOrder not found with barCodeNo=%s' % barCodeNo)
                famiport_receipt = None

            if famiport_receipt is not None:
                # 入金発券完了リクエストの店番は実店番で、スマホ店番はこの完了処理で実店番に更新される必要があります。
                # よってスマホ店番のレシートデータは正常系です。
                if _strip_zfill(famiport_receipt.shop_code) != storeCode \
                        and self.sp_shop_code != famiport_receipt.shop_code:
                    logger.error(u'shop_code differs (%s != %s)' % (famiport_receipt.shop_code, storeCode))
                    replyCode = ReplyCodeEnum.SearchKeyError.value
                    famiport_receipt = None
                elif not famiport_receipt.can_completion(now):
                    logger.error(u'settlement error (%s)' % famiport_receipt.shop_code)
                    replyCode = ReplyCodeEnum.OtherError.value
                    famiport_receipt = None
                else:
                    # 正常系
                    famiport_order = famiport_receipt.famiport_order
                    replyCode = ReplyCodeEnum.Normal.value
                    if famiport_receipt.type == FamiPortReceiptType.CashOnDelivery.value:
                        if famiport_receipt.made_reissueable_at is None and famiport_receipt.completed_at is not None:
                            logger.info(u"FamiPortReceipt(type=%d, id=%ld, reserve_number=%s): already paid" % (famiport_receipt.type, famiport_receipt.id, famiport_receipt.reserve_number))
                            replyCode = ReplyCodeEnum.AlreadyPaidError.value
                        else:
                            logger.info(u"FamiPortReceipt(type=%d, id=%ld, reserve_number=%s): payment and ticketing" % (famiport_receipt.type, famiport_receipt.id, famiport_receipt.reserve_number))
                            if famiport_receipt.made_reissueable_at is not None:
                                logger.info(u'FamiPortReceipt(reserve_number=%s) has been made reissueable (%s).' % (famiport_receipt.reserve_number, famiport_receipt.made_reissueable_at))
                            famiport_receipt.shop_code = storeCode  # 実店番に更新する
                            famiport_receipt.mark_completed(now, request)
                            famiport_order.mark_issued(now, request)
                            famiport_order.mark_paid(now, request)
                            session.commit()
                    elif famiport_receipt.type == FamiPortReceiptType.Payment.value:
                        # 前払後日の支払 / 支払いのみ
                        if famiport_receipt.completed_at is not None:
                            logger.info(u"FamiPortReceipt(type=%d, id=%ld, reserve_number=%s): already paid" % (famiport_receipt.type, famiport_receipt.id, famiport_receipt.reserve_number))
                            replyCode = ReplyCodeEnum.AlreadyPaidError.value
                        else:
                            logger.info(u"FamiPortReceipt(type=%d, id=%ld, reserve_number=%s): payment" % (famiport_receipt.type, famiport_receipt.id, famiport_receipt.reserve_number))
                            famiport_receipt.shop_code = storeCode  # 実店番に更新する
                            famiport_receipt.mark_completed(now, request)
                            famiport_order.mark_paid(now, request)
                            session.commit()
                    elif famiport_receipt.type == FamiPortReceiptType.Ticketing.value:
                        # 前払後日の発券 / 発券のみ
                        if famiport_receipt.made_reissueable_at is None and famiport_receipt.completed_at is not None:
                            logger.warning(u"FamiPortReceipt(type=%d, id=%ld, reserve_number=%s): already issued" % (famiport_receipt.type, famiport_receipt.id, famiport_receipt.reserve_number))
                            replyCode = ReplyCodeEnum.AlreadyPaidError.value
                        else:
                            logger.info(u"FamiPortReceipt(type=%d, id=%ld, reserve_number=%s): ticketing" % (famiport_receipt.type, famiport_receipt.id, famiport_receipt.reserve_number))
                            if famiport_receipt.made_reissueable_at is not None:
                                logger.info(u'FamiPortReceipt(reserve_number=%s) has been made reissueable (%s).' % (famiport_receipt.reserve_number, famiport_receipt.made_reissueable_at))
                            famiport_receipt.shop_code = storeCode  # 実店番に更新する
                            famiport_receipt.mark_completed(now, request)
                            famiport_order.mark_issued(now, request)
                            session.commit()
                    else:
                        raise AssertionError('NEVER GET HERE')
            else:
                replyCode = ReplyCodeEnum.SearchKeyError.value

            famiport_payment_ticketing_completion_response = FamiPortPaymentTicketingCompletionResponse(
                _request=famiport_payment_ticketing_completion_request,
                resultCode=resultCode,
                storeCode=storeCode.zfill(6),
                sequenceNo=sequenceNo,
                barCodeNo=barCodeNo,
                orderId=orderId,
                replyCode=replyCode
                )
        except:
            logger.exception(
                u'An exception has occurred at FamiPortPaymentTicketingCompletionResponseBuilder.build_response().'
                u'店舗コード: %s , 発券Famiポート番号: %s , 利用日時: %s , 処理通番: %s , 支払番号: %s , 注文ID: %s'
                % (storeCode, mmkNo, famiport_payment_ticketing_completion_request.ticketingDate, sequenceNo, barCodeNo, orderId))
            resultCode = ResultCodeEnum.OtherError.value
            replyCode = ReplyCodeEnum.OtherError.value
            famiport_payment_ticketing_completion_response = FamiPortPaymentTicketingCompletionResponse(
                _request=famiport_payment_ticketing_completion_request,
                resultCode=resultCode,
                storeCode=storeCode.zfill(6),
                sequenceNo=sequenceNo,
                barCodeNo=barCodeNo,
                orderId=orderId,
                replyCode=replyCode
                )

        return famiport_payment_ticketing_completion_response


class FamiPortPaymentTicketingCancelResponseBuilder(FamiPortResponseBuilder):
    def build_response(self, famiport_payment_ticketing_cancel_request, session, now, request):
        famiport_request = famiport_payment_ticketing_cancel_request
        storeCode = _strip_zfill(famiport_request.storeCode)
        logger.info(
            u'Processing famiport ticketing cancel request. ' \
            u'店舗コード: %s, 発券Famiポート番号: %s, 利用日時: %s, 処理通番: %s, 支払番号: %s' \
                % (
                    famiport_payment_ticketing_cancel_request.storeCode,
                    famiport_payment_ticketing_cancel_request.mmkNo,
                    famiport_payment_ticketing_cancel_request.ticketingDate,
                    famiport_payment_ticketing_cancel_request.sequenceNo,
                    famiport_payment_ticketing_cancel_request.barCodeNo
                )
            )
        famiport_response = FamiPortPaymentTicketingCancelResponse(
            _request=famiport_payment_ticketing_cancel_request,
            orderId=u'',
            barCodeNo=u'',
            storeCode=storeCode.zfill(6),
            sequenceNo=famiport_payment_ticketing_cancel_request.sequenceNo,
            resultCode=ResultCodeEnum.OtherError.value,
            replyCode=ReplyCodeEnum.OtherError.value,
            )
        try:
            try:
                ticketingDate = datetime.datetime.strptime(
                    famiport_payment_ticketing_cancel_request.ticketingDate,
                    '%Y%m%d%H%M%S'
                    )
            except ValueError:
                logger.exception(u"不正な利用日時です (%s)" % famiport_payment_ticketing_cancel_request.ticketingDate)
                raise
            try:
                cancelCode = int(famiport_payment_ticketing_cancel_request.cancelCode)
            except (ValueError, TypeError):
                logger.exception(u"不正なキャンセルコードです (%s)" % famiport_payment_ticketing_cancel_request.cancelCode)
                raise

            famiport_receipt = FamiPortReceipt.get_by_barcode_no(
                famiport_payment_ticketing_cancel_request.barCodeNo,
                session=session)

            if famiport_receipt is None:  # 検索エラー
                logger.info('no FamiPortReceipt found that corresponds to %s' % famiport_payment_ticketing_cancel_request.barCodeNo)
                famiport_response.resultCode = ResultCodeEnum.OtherError.value
                famiport_response.replyCode = ReplyCodeEnum.OtherError.value
                return famiport_response

            if _strip_zfill(famiport_receipt.shop_code) != storeCode:
                logger.info('store code differs (%s != %s)' % (famiport_receipt.shop_code, storeCode))
                famiport_response.replyCode = ReplyCodeEnum.OtherError.value
                famiport_receipt = None
            elif famiport_receipt.completed_at is not None:  # 支払済
                logger.info('paid / ticketed')
                if famiport_receipt.type in (FamiPortReceiptType.CashOnDelivery.value, FamiPortReceiptType.Payment.value):
                    famiport_response.resultCode = ResultCodeEnum.Normal.value
                    famiport_response.replyCode = ReplyCodeEnum.AlreadyPaidError.value  # 支払い済み
                else:
                    famiport_response.resultCode = ResultCodeEnum.Normal.value
                    famiport_response.replyCode = ReplyCodeEnum.TicketAlreadyIssuedError.value  # 発券済み
                famiport_receipt = None
            elif famiport_receipt.canceled_at is not None:  # 支払取消済みエラー
                logger.info('already canceled')
                if famiport_receipt.type in (FamiPortReceiptType.CashOnDelivery.value, FamiPortReceiptType.Payment.value):
                    famiport_response.resultCode = ResultCodeEnum.Normal.value
                    famiport_response.replyCode = ReplyCodeEnum.PaymentAlreadyCanceledError.value  # 支払い取り消し済みエラー
                else:
                    famiport_response.resultCode = ResultCodeEnum.Normal.value
                    famiport_response.replyCode = ReplyCodeEnum.TicketingAlreadyCanceledError.value  # 発券取り消し済みエラー

                famiport_receipt = None
            else:  # 正常
                famiport_response.resultCode = ResultCodeEnum.Normal.value
                famiport_response.replyCode = ReplyCodeEnum.Normal.value
                famiport_response.orderId = famiport_receipt.famiport_order_identifier
                famiport_response.barCodeNo = famiport_receipt.barcode_no
                famiport_receipt.mark_voided(now, request, cancelCode)  # 30分破棄処理
                session.commit()
        except Exception as err:  # その他の異常
            logger.exception(u'famiport order cancel error')
            logger.exception(
                u"an exception occurred at FamiPortPaymentTicketingCancelResponseBuilder.build_response(). "
                u'店舗コード: %s, 発券Famiポート番号: %s, 利用日時: %s, 処理通番: %s, 支払番号: %s' \
                    % (
                        famiport_payment_ticketing_cancel_request.storeCode,
                        famiport_payment_ticketing_cancel_request.mmkNo,
                        famiport_payment_ticketing_cancel_request.ticketingDate,
                        famiport_payment_ticketing_cancel_request.sequenceNo,
                        famiport_payment_ticketing_cancel_request.barCodeNo
                    )
                )
            famiport_response.resultCode = ResultCodeEnum.OtherError.value
            famiport_response.replyCode = ReplyCodeEnum.OtherError.value
        return famiport_response


class FamiPortInformationResponseBuilder(FamiPortResponseBuilder):

    def build_response(self, famiport_information_request, session, now, request):
        """案内通信

        デフォルトは「案内なし(正常)」
        FamiPortInformationMessageにWithInformationに対応するmessageがあれば「案内あり(正常)」としてメッセージを表示する。
        FamiPortInformationMessageにServiceUnavailableに対応するmessageがあれば「サービス不可時案内」としてメッセージを表示する。
        途中でエラーが起こった場合は「その他エラー」としてメッセージを表示する。

        :param famiport_information_request:
        :return: FamiPortInformationResponse
        """
        famiport_request = famiport_information_request
        famiport_response = FamiPortInformationResponse(
            _request=famiport_information_request
            )
        famiport_response.infoKubun = famiport_request.infoKubun
        try:
            if famiport_request.infoKubun == InfoKubunEnum.DirectSales.value:  # 直販
                famiport_response.resultCode = InformationResultCodeEnum.ServiceUnavailable.value
                famiport_response.infoMessage = u'現在お取り扱いしておりません。'
                return famiport_response

            elif famiport_request.infoKubun == InfoKubunEnum.Reserved.value:  # 予済
                famiport_receipt = None
                if famiport_request.reserveNumber:
                    famiport_receipt = None
                    try:
                        famiport_receipt = FamiPortReceipt.get_by_reserve_number(famiport_request.reserveNumber, session)
                    except NoResultFound:
                        pass

                # 条件を作る.
                # 仮に famiport_order がなかったとしてもクライアントコードで引いて来れるメッセージは表示しなければならない
                if famiport_receipt is None:
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
                    famiport_order = famiport_receipt.famiport_order
                    famiport_sales_segment = famiport_order.famiport_sales_segment
                    famiport_sales_segment_code = famiport_sales_segment.code if famiport_sales_segment else None
                    famiport_performance = famiport_order.famiport_performance
                    famiport_event = famiport_performance.famiport_event
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
                                FamiPortInformationMessage.event_code_1 == famiport_event.code_1,
                                FamiPortInformationMessage.event_code_2 == famiport_event.code_2,
                                FamiPortInformationMessage.performance_code == None,
                                FamiPortInformationMessage.sales_segment_code == None,
                                FamiPortInformationMessage.reserve_number == None
                                ),
                        lambda q: \
                            q.filter(
                                FamiPortInformationMessage.event_code_1 == famiport_event.code_1,
                                FamiPortInformationMessage.event_code_2 == famiport_event.code_2,
                                FamiPortInformationMessage.performance_code == famiport_performance.code,
                                FamiPortInformationMessage.sales_segment_code == None,
                                FamiPortInformationMessage.reserve_number == None
                                ),
                        lambda q: \
                            q.filter(
                                FamiPortInformationMessage.event_code_1 == famiport_event.code_1,
                                FamiPortInformationMessage.event_code_2 == famiport_event.code_2,
                                FamiPortInformationMessage.performance_code == famiport_performance.code,
                                FamiPortInformationMessage.sales_segment_code == famiport_sales_segment_code,
                                FamiPortInformationMessage.reserve_number == None
                                ),
                        lambda q: \
                            q.filter(
                                FamiPortInformationMessage.event_code_1 == famiport_event.code_1,
                                FamiPortInformationMessage.event_code_2 == famiport_event.code_2,
                                FamiPortInformationMessage.performance_code == famiport_performance.code,
                                FamiPortInformationMessage.sales_segment_code == famiport_sales_segment_code,
                                FamiPortInformationMessage.reserve_number == famiport_receipt.reserve_number
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
                raise AssertionError('unknown infoKubun: {}'.format(famiport_request.infoKubun))
        except Exception as err:  # その他エラー
            logger.exception('FamiPort Information Error: {}: {}'.format(type(err).__name__, err))
            famiport_response.resultCode = InformationResultCodeEnum.OtherError.value
            famiport_response.infoMessage = u'異常が発生しました'
            return famiport_response


class FamiPortCustomerInformationResponseBuilder(FamiPortResponseBuilder):

    def build_response(self, famiport_customer_information_request, session, now, request):
        storeCode = _strip_zfill(famiport_customer_information_request.storeCode)
        mmkNo = famiport_customer_information_request.mmkNo
        ticketingDate = None
        sequenceNo = famiport_customer_information_request.sequenceNo
        barCodeNo = famiport_customer_information_request.barCodeNo
        orderId = famiport_customer_information_request.orderId

        try:
            try:
                ticketingDate = datetime.datetime.strptime(
                    famiport_customer_information_request.ticketingDate,
                    '%Y%m%d%H%M%S'
                    )
            except ValueError:
                logger.exception(u"不正な利用日時です (%s)" % famiport_customer_information_request.ticketingDate)
                raise

            famiport_receipt = None
            try:
                famiport_receipt = FamiPortReceipt.get_by_barcode_no(barCodeNo, session=session)
            except NoResultFound:
                logger.error(u'FamiPortReceipt not found with barCodeNo=%s' % barCodeNo)

            famiport_order = None
            if famiport_receipt is not None:
                if famiport_receipt.can_completion(now):
                    logger.warning(u'Payment request is not made against FamiPortReceipt(barCodeNo=%s)' % barCodeNo)
                famiport_order = famiport_receipt.famiport_order

            if famiport_order is not None:
                name = famiport_order.customer_name
                # TODO Make sure where to get memberId
                memberId = famiport_order.customer_member_id
                address1 = famiport_order.customer_address_1
                address2 = famiport_order.customer_address_2
                # TODO Make sure where to get identifyNo
                identifyNo = famiport_order.customer_identify_no

                famiport_customer_information_response = FamiPortCustomerInformationResponse(
                    _request=famiport_customer_information_request,
                    resultCode=ResultCodeEnum.Normal.value,
                    replyCode=ReplyCodeEnum.Normal.value,
                    name=name,
                    memberId=memberId,
                    address1=address1,
                    address2=address2,
                    identifyNo=identifyNo
                    )
                famiport_customer_information_response.set_encryptKey(orderId)
            else:
                famiport_customer_information_response = FamiPortCustomerInformationResponse(
                    _request=famiport_customer_information_request,
                    resultCode=ResultCodeEnum.Normal.value,
                    replyCode=ReplyCodeEnum.CustomerNamePrintInformationError.value
                    )
        except Exception:
            logger.exception(
                u'an exception has occurred at FamiPortPaymentTicketingCancelResponseBuilder.build_response(). '
                u'店舗コード: %s , 発券Famiポート番号: %s , 利用日時: %s , 処理通番: %s , 支払番号: %s , 注文ID: %s'
                % (storeCode, mmkNo, ticketingDate, sequenceNo, barCodeNo, orderId)
                )
            famiport_customer_information_response = FamiPortCustomerInformationResponse(
                _request=famiport_customer_information_request,
                resultCode=ResultCodeEnum.OtherError.value,
                replyCode=ReplyCodeEnum.OtherError.value
                )
        return famiport_customer_information_response


class FamiPortRefundEntryResponseBuilder(FamiPortResponseBuilder):
    def build_response(self, famiport_refund_entry_request, session, now, request):
        shop_code = _strip_zfill(famiport_refund_entry_request.shopNo)
        text_type = FamiPortRefundEntryResponseTextTypeEnum.ResponseToInquiry.value
        error_code = FamiPortRefundEntryResponseErrorCodeEnum.OutOfService.value
        try:
            given_text_type = None
            try:
                given_text_type = int(famiport_refund_entry_request.textTyp)
            except (ValueError, TypeError):
                logger.exception(u"invalid TextTyp (%s)" % famiport_refund_entry_request.textTyp)
                error_code = FamiPortRefundEntryResponseErrorCodeEnum.InvalidParameter.value
                raise
            text_type = None
            if given_text_type == FamiPortRefundEntryResponseTextTypeEnum.Inquiry.value:  # 0: 問い合わせ -> 応答では1を応答
                text_type = FamiPortRefundEntryResponseTextTypeEnum.ResponseToInquiry.value
            elif given_text_type == FamiPortRefundEntryResponseTextTypeEnum.Settlement.value:  # 2: 確定 -> 応答では4を応答
                text_type = FamiPortRefundEntryResponseTextTypeEnum.ResponseToSettlement.value  # なぜか4 (textTypは連番ではないらしい)
            else:
                error_code = FamiPortRefundEntryResponseErrorCodeEnum.InvalidParameter.value
                raise ValueError(u"invalid TextTyp (%s)" % famiport_refund_entry_request.textTyp)

            famiport_refund_entry_response = FamiPortRefundEntryResponse(
                _request=famiport_refund_entry_request,
                businessFlg=famiport_refund_entry_request.businessFlg,
                textTyp=u'%d' % text_type,
                entryTyp=famiport_refund_entry_request.entryTyp,
                shopNo=shop_code.zfill(7),
                registerNo=famiport_refund_entry_request.registerNo,
                timeStamp=famiport_refund_entry_request.timeStamp
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
            def build_per_ticket_record(barcode_number, refund_entry, fill_with_blank=False):
                result_code = None
                if fill_with_blank:
                    main_title = u''
                    perf_day = u''
                    repayment = u''
                    refund_start = u''
                    refund_end = u''
                    ticket_typ = u''
                    charge = u''
                else:
                    main_title = None
                    perf_day = None
                    repayment = None
                    refund_start = None
                    refund_end = None
                    ticket_typ = None
                    charge = None
                if barcode_number is None:
                    pass
                elif refund_entry is None:
                    result_code = FamiPortRefundEntryResponseResultCodeEnum.NoData.value
                else:
                    if refund_entry.refunded_at is not None:
                        result_code = FamiPortRefundEntryResponseResultCodeEnum.AlreadyMarkedRefunded.value
                    else:
                        issuing_shop_code = refund_entry.famiport_ticket.famiport_order.issuing_shop_code
                        assert issuing_shop_code is not None
                        issuing_shop_code = _strip_zfill(issuing_shop_code)
                        famiport_performance = refund_entry.famiport_ticket.famiport_order.famiport_performance
                        main_title = famiport_performance.name or u''
                        perf_day = six.text_type(famiport_performance.start_at.strftime('%Y%m%d')) if famiport_performance.start_at else u''
                        repayment = u'{0}'.format(refund_entry.ticket_payment + refund_entry.ticketing_fee + refund_entry.other_fees)
                        refund_start = six.text_type(refund_entry.famiport_refund.start_at.strftime('%Y%m%d'))
                        refund_end = six.text_type(refund_entry.famiport_refund.end_at.strftime('%Y%m%d'))
                        ticket_typ = u'{0}'.format(refund_entry.famiport_ticket.type)
                        charge = u'{0}'.format(refund_entry.ticketing_fee + refund_entry.other_fees)
                        if refund_entry.famiport_refund.start_at > now \
                           or refund_entry.famiport_refund.end_at < now:
                            result_code = FamiPortRefundEntryResponseResultCodeEnum.OutOfTerm.value
                        else:
                            if issuing_shop_code != shop_code:
                                result_code = FamiPortRefundEntryResponseResultCodeEnum.IssuedAtDifferentShop.value
                            else:
                                result_code = FamiPortRefundEntryResponseResultCodeEnum.Refundable.value
                            if given_text_type == FamiPortRefundEntryResponseTextTypeEnum.Settlement.value:
                                refund_entry.refunded_at = now
                                refund_entry.shop_code = shop_code
                                session.commit()
                return dict(
                    barCode=barcode_number,
                    resultCode=u'%d' % result_code if result_code is not None else None,
                    mainTitle=main_title,
                    perfDay=perf_day,
                    repayment=repayment,
                    refundStart=refund_start,
                    refundEnd=refund_end,
                    ticketTyp=ticket_typ,
                    charge=charge
                    )

            famiport_refund_entry_response.per_ticket_records = [
                build_per_ticket_record(barcode_number, refund_entry, fill_with_blank=(i == 0))
                for i, (barcode_number, refund_entry) in enumerate(refund_entries)
                ]
            famiport_refund_entry_response.errorCode = u'%d' % FamiPortRefundEntryResponseErrorCodeEnum.Success.value
        except:
            famiport_refund_entry_response = FamiPortRefundEntryResponse(
                _request=famiport_refund_entry_request,
                businessFlg=famiport_refund_entry_request.businessFlg,
                entryTyp=famiport_refund_entry_request.entryTyp,
                shopNo=famiport_refund_entry_request.shopNo,
                registerNo=famiport_refund_entry_request.registerNo,
                timeStamp=famiport_refund_entry_request.timeStamp,
                errorCode=u'%d' % error_code
                )
            logger.exception(
                u"an exception occurred at FamiPortRefundEntryResponseBuilder.build_response(). "
                u'処理区分: %s, 店舗コード: %s, レジ番号: %s, オペレーション開始日: %s' \
                % (famiport_refund_entry_request.textTyp, famiport_refund_entry_request.shopNo, famiport_refund_entry_request.registerNo, famiport_refund_entry_request.timeStamp)
                )
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
                pretty_print=False,  # trueにするとSerializationError: IO_ENCODERが発生するようになった
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
        for attribute_name_or_pair in obj._serialized_attrs:
            if isinstance(attribute_name_or_pair, basestring):
                attribute_name = attribute_name_or_pair
                element_name = attribute_name_or_pair
            else:
                attribute_name = attribute_name_or_pair[0]
                element_name = attribute_name_or_pair[1]
            attribute_value = getattr(obj, attribute_name)
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


class TextFamiPortResponseGenerator(object):
    def __init__(self, famiport_response, xml_encoding='Shift_JIS', encoding='CP932', crypted_part_encoding='UTF-8'):
        self.famiport_crypt = None
        if famiport_response.encrypt_key:
            self.famiport_crypt = FamiPortCrypt(famiport_response.encrypt_key, encoding=crypted_part_encoding)
        self.xml_encoding = xml_encoding
        self.encoding = encoding

    def serialize(self, famiport_response, *args, **kwds):
        """
        """
        key_value_pairs = self._build(famiport_response)
        buf = u'\r\n'.join(
            u'{}={}'.format(key, (value or u''))
            for key, value in key_value_pairs)
        return buf.encode(self.encoding)

    def _build(self, obj):
        """Build XML tree from object"""
        if obj is None:
            return ''

        key_value_pairs = []
        for attribute_name_or_pair in obj._serialized_attrs:
            if isinstance(attribute_name_or_pair, basestring):
                attribute_name = attribute_name_or_pair
                element_name = attribute_name_or_pair
            else:
                attribute_name = attribute_name_or_pair[0]
                element_name = attribute_name_or_pair[1]
            attribute_value = getattr(obj, attribute_name)
            if attribute_name not in obj.encrypted_fields:
                key_value_pairs.append((element_name, attribute_value))
            elif self.famiport_crypt:
                assert attribute_value is not None
                key_value_pairs.append((element_name, self.famiport_crypt.encrypt(attribute_value)))

        return key_value_pairs
