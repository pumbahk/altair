# -*- coding: utf-8 -*-
import sys
import six
import logging
from datetime import datetime
from decimal import Decimal, ROUND_DOWN
from sqlalchemy import func
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from altair.sqlahelper import get_db_session
import functools
from .models import (
    FamiPortOrder,
    FamiPortOrderType,
    FamiPortTicket,
    FamiPortTicketType,
    FamiPortClient,
    FamiPortVenue,
    FamiPortEvent,
    FamiPortPerformance,
    FamiPortPerformanceType,
    FamiPortPrefecture,
    FamiPortReceipt,
    FamiPortReceiptType,
    FamiPortSalesSegment,
    FamiPortGenre1,
    FamiPortGenre2,
    FamiPortSalesChannel,
    FamiPortBarcodeNoSequence,
    FamiPortOrderIdentifierSequence,
    FamiPortRefund,
    FamiPortRefundEntry,
    )
from .exc import FamiPortError, FamiPortAPIError, FamiPortAPINotFoundError, FamiPortAlreadyPaidError, \
    FamiPortAlreadyIssuedError, FamiPortAlreadyCanceledError, FamiportPaymentDateNoneError, FamiPortTicketingDateNoneError
from .communication.api import (  # noqa
    get_response_builder,  # noqa B/W compatibility
    get_xmlResponse_generator,  # noqa B/W compatibility
    )

logger = logging.getLogger(__name__)

class UnspecifiedType(object):
    pass

Unspecified = UnspecifiedType()

def get_famiport_sales_segment_by_code(session, client_code, event_code_1, event_code_2, performance_code, code):
    retval = session.query(FamiPortSalesSegment) \
                    .join(FamiPortSalesSegment.famiport_performance) \
                    .join(FamiPortPerformance.famiport_event) \
                    .filter(FamiPortEvent.client_code == client_code) \
                    .filter(FamiPortEvent.code_1 == event_code_1, FamiPortEvent.code_2 == event_code_2) \
                    .filter(FamiPortPerformance.code == performance_code) \
                    .filter(FamiPortSalesSegment.code == code) \
                    .filter(FamiPortEvent.invalidated_at == None) \
                    .filter(FamiPortPerformance.invalidated_at == None) \
                    .filter(FamiPortSalesSegment.invalidated_at == None) \
                    .one()
    return retval

def get_famiport_venue_by_userside_id(session, client_code, userside_id):
    retval = session.query(FamiPortVenue) \
                    .filter_by(client_code=client_code, userside_id=userside_id) \
                    .one()
    return retval

def get_famiport_venue_by_name(session, client_code, name):
    retval = session.query(FamiPortVenue) \
                    .filter_by(client_code=client_code, name=name) \
                    .one()
    return retval

def get_famiport_sales_segment_by_code(session, client_code, event_code_1, event_code_2, performance_code, code):
    retval = session.query(FamiPortSalesSegment) \
                    .join(FamiPortSalesSegment.famiport_performance) \
                    .join(FamiPortPerformance.famiport_event) \
                    .filter(FamiPortEvent.client_code == client_code,
                            FamiPortEvent.code_1 == event_code_1,
                            FamiPortEvent.code_2 == event_code_2
                            ) \
                    .filter(FamiPortPerformance.code == performance_code) \
                    .filter(FamiPortSalesSegment.code == code) \
                    .filter(FamiPortEvent.invalidated_at == None) \
                    .filter(FamiPortPerformance.invalidated_at == None) \
                    .filter(FamiPortSalesSegment.invalidated_at == None) \
                    .one()
    return retval


def get_famiport_sales_segment_by_userside_id(session, client_code, userside_id):
    retval = session.query(FamiPortSalesSegment) \
                    .join(FamiPortSalesSegment.famiport_performance) \
                    .join(FamiPortPerformance.famiport_event) \
                    .filter(FamiPortEvent.client_code == client_code,
                            FamiPortSalesSegment.userside_id == userside_id) \
                    .filter(FamiPortEvent.invalidated_at == None) \
                    .filter(FamiPortPerformance.invalidated_at == None) \
                    .filter(FamiPortSalesSegment.invalidated_at == None) \
                    .one()
    return retval

def get_famiport_performance_by_code(session, client_code, event_code_1, event_code_2, code):
    retval = session.query(FamiPortPerformance) \
                    .join(FamiPortPerformance.famiport_event) \
                    .filter(FamiPortEvent.client_code == client_code) \
                    .filter(FamiPortEvent.code_1 == event_code_1, FamiPortEvent.code_2 == event_code_2) \
                    .filter(FamiPortPerformance.code == code) \
                    .filter(FamiPortEvent.invalidated_at == None) \
                    .filter(FamiPortPerformance.invalidated_at == None) \
                    .one()
    return retval

def get_famiport_performance_by_userside_id(session, client_code, userside_id):
    retval = session.query(FamiPortPerformance) \
                    .join(FamiPortPerformance.famiport_event) \
                    .filter(FamiPortEvent.client_code == client_code,
                            FamiPortPerformance.userside_id == userside_id) \
                    .filter(FamiPortEvent.invalidated_at == None) \
                    .filter(FamiPortPerformance.invalidated_at == None) \
                    .one()
    return retval

def get_famiport_event_by_code(session, client_code, code_1, code_2):
    retval = session.query(FamiPortEvent) \
                    .filter(FamiPortEvent.client_code == client_code,
                            FamiPortEvent.code_1 == code_1,
                            FamiPortEvent.code_2 == code_2) \
                    .filter(FamiPortEvent.invalidated_at == None) \
                    .one()
    return retval

def get_famiport_event_by_userside_id(session, client_code, userside_id):
    retval = session.query(FamiPortEvent) \
                    .filter(FamiPortEvent.client_code == client_code,
                            FamiPortEvent.userside_id == userside_id) \
                    .filter(FamiPortEvent.invalidated_at == None) \
                    .one()
    return retval

def get_famiport_order(session, client_code, order_no=None, famiport_order_identifier=None):
    if order_no is None:
        if famiport_order_identifier is None:
            raise FamiPortError('order_no and famiport_order_identifier cannot be None at the same time')
        try:
            retval = session.query(FamiPortOrder) \
                .filter(FamiPortOrder.client_code == client_code) \
                .filter(FamiPortOrder.famiport_order_identifier == famiport_order_identifier) \
                .filter(FamiPortOrder.invalidated_at == None) \
                .one()
        except NoResultFound:
            raise FamiPortError('no corresponding order found for famiport_order_identifier=%s' % famiport_order_identifier)
    else:
        try:
            retval = session.query(FamiPortOrder) \
                .filter(FamiPortOrder.client_code == client_code) \
                .filter(FamiPortOrder.order_no == order_no) \
                .filter(FamiPortOrder.invalidated_at == None) \
                .one()
        except MultipleResultsFound:
            raise FamiPortError('multiple order exist for order_no=%s. use famiport_order_identifier to be more specific' % order_no)
        except NoResultFound:
            raise FamiPortError('no corresponding order found for order_no=%s' % order_no)
        if famiport_order_identifier is not None and retval.famiport_order_identifier != famiport_order_identifier:
            raise FamiPortError('famiport_order_identifier differs (%s != %s)' % (famiport_order_identifier, retval.famiport_order_identifier))
    return retval

def get_famiport_client(session, client_code):
    sys.exc_clear()
    try:
        return session.query(FamiPortClient) \
                        .filter_by(code=client_code) \
                        .one()
    except NoResultFound:
        raise FamiPortAPIError('no such client: %s' % client_code)
    except:
        raise FamiPortAPIError('internal error')

def create_famiport_ticket(session, famiport_playguide, ticket_dict):
    return FamiPortTicket(
        type=ticket_dict['type'],
        barcode_number=FamiPortBarcodeNoSequence.get_next_value(famiport_playguide.discrimination_code, session),
        template_code=ticket_dict['template'],
        price=ticket_dict['price'],
        userside_id=ticket_dict['userside_id'],
        userside_token_id=ticket_dict['userside_token_id'],
        data=ticket_dict['data'],
        logically_subticket=ticket_dict['logically_subticket']
        )

def validate_sales_channel(sales_channel):
    if sales_channel not in (FamiPortSalesChannel.FamiPortOnly.value, FamiPortSalesChannel.WebOnly.value, FamiPortSalesChannel.FamiPortAndWeb.value):
        raise FamiPortAPIError('invalid sales_channel: %d' % sales_channel)

def validate_prefecture(prefecture):
    if not FamiPortPrefecture.is_valid_id(prefecture):
        raise FamiPortAPIError('invalid prefecture: %d' % prefecture)

def validate_order_info(type_, payment_start_at, payment_due_at, ticketing_start_at, ticketing_end_at, ticket_payment, ticketing_fee, system_fee, total_amount):
    if type_ in (FamiPortOrderType.CashOnDelivery.value, FamiPortOrderType.Payment.value, FamiPortOrderType.PaymentOnly.value):
        if payment_start_at is None:
            raise FamiportPaymentDateNoneError(u'支払開始日時を正しく入力してください')
        if payment_due_at is None:
            raise FamiportPaymentDateNoneError(u'支払期限日時を正しく入力してください')
        if payment_start_at > payment_due_at:
            raise FamiportPaymentDateNoneError(u'支払開始日時は支払期限日時より前の日時を入力してください')
    if type_ in (FamiPortOrderType.CashOnDelivery.value, FamiPortOrderType.Payment.value, FamiPortOrderType.Ticketing.value):
        if ticketing_start_at is None:
            raise FamiPortTicketingDateNoneError(u'発券開始日時を正しく入力してください')
        if ticketing_end_at is None:
            raise FamiPortTicketingDateNoneError(u'発券期限日時を正しく入力してください')
        if ticketing_start_at > ticketing_end_at:
            raise FamiPortTicketingDateNoneError(u'発券開始日時は発券期限日時より前の日時を入力してください')
    if ticket_payment + ticketing_fee + system_fee != total_amount:
        raise FamiPortError('ticketing_payment + ticketing_fee + system_fee != total_amount')

def create_famiport_order(
        session,
        client_code,
        type_,
        famiport_performance,
        famiport_sales_segment,
        order_no,
        customer_name,
        customer_phone_number,
        customer_address_1,
        customer_address_2,
        total_amount,
        system_fee,
        ticketing_fee,
        ticket_payment,
        tickets,
        payment_start_at=None,
        payment_due_at=None,
        ticketing_start_at=None,
        ticketing_end_at=None,
        payment_sheet_text=None,
        require_ticketing_fee_on_ticketing=None,
        now=None
        ):
    """FamiPortOrderを作成する"""
    if now is None:
        now = datetime.now()
    famiport_client = get_famiport_client(session, client_code)
    famiport_order_identifier = FamiPortOrderIdentifierSequence.get_next_value(famiport_client.prefix, session)
    if type_ == FamiPortOrderType.CashOnDelivery.value:
        ticketing_start_at = payment_start_at
        ticketing_end_at = payment_due_at
    validate_order_info(
        type_=type_,
        payment_start_at=payment_start_at,
        payment_due_at=payment_due_at,
        ticketing_start_at=ticketing_start_at,
        ticketing_end_at=ticketing_end_at,
        total_amount=total_amount,
        ticket_payment=ticket_payment,
        system_fee=system_fee,
        ticketing_fee=ticketing_fee
        )
    famiport_order = FamiPortOrder(
        client_code=client_code,
        type=type_,
        order_no=order_no,
        famiport_performance=famiport_performance,
        famiport_sales_segment=famiport_sales_segment,
        famiport_order_identifier=famiport_order_identifier,
        customer_name=customer_name,
        customer_phone_number=customer_phone_number,
        customer_address_1=customer_address_1,
        customer_address_2=customer_address_2,
        total_amount=total_amount,
        system_fee=system_fee,
        ticketing_fee=ticketing_fee,
        ticket_payment=ticket_payment,
        payment_start_at=payment_start_at,
        payment_due_at=payment_due_at,
        ticketing_start_at=ticketing_start_at,
        ticketing_end_at=ticketing_end_at,
        famiport_tickets=[
            create_famiport_ticket(session, famiport_client.playguide, ticket_dict)
            for ticket_dict in tickets
            ],
        payment_sheet_text=payment_sheet_text,
        require_ticketing_fee_on_ticketing=require_ticketing_fee_on_ticketing,
        created_at=now,
        updated_at=now
        )
    session.add(famiport_order)
    session.flush()
    famiport_order.add_receipts()
    session.commit()
    return famiport_order

def can_cancel_famiport_order(
        request,
        session,
        client_code,
        order_no,
        now
        ):
    """FamiPortOrderがキャンセル出来る状態か確認する(true or false)"""
    if now is None:
        now = datetime.now()
    famiport_order = get_famiport_order(session, order_no=order_no, client_code=client_code)
    return famiport_order.can_cancel(now, request)

def cancel_famiport_order_by_order_no(
        request,
        session, 
        client_code,
        order_no,
        now=None
        ):
    """FamiPortOrderをキャンセルする"""
    if now is None:
        now = datetime.now()
    famiport_order = get_famiport_order(session, order_no=order_no, client_code=client_code)
    famiport_order.mark_canceled(now, request)


def mark_order_reissueable_by_order_no(
        request,
        session,
        order_no,
        cancel_reason_code=None,
        cancel_reason_text=None,
        client_code=None,
        now=None
        ):
    """FamiPortOrderに再発券許可"""
    if now is None:
        now = datetime.now()
    famiport_order = get_famiport_order(session, order_no=order_no, client_code=client_code)
    famiport_order.make_reissueable(now, request, cancel_reason_code, cancel_reason_text)


def make_suborder_by_order_no(
        request,
        session,
        order_no,
        type_=None,
        reason=None,
        cancel_reason_code=None,
        cancel_reason_text=None,
        client_code=None,
        now=None
        ):
    """FamiPortOrderを同席番再予約"""
    if now is None:
        now = datetime.now()
    famiport_order = get_famiport_order(session, order_no=order_no, client_code=client_code)
    famiport_order.make_suborder(now, request, type_, reason, cancel_reason_code, cancel_reason_text)

def update_famiport_order_by_order_no(
        session,
        client_code,
        order_no,
        famiport_order_identifier,
        type_,
        event_code_1,
        event_code_2,
        performance_code,
        sales_segment_code,
        customer_name,
        customer_phone_number,
        customer_address_1,
        customer_address_2,
        total_amount,
        system_fee,
        ticketing_fee,
        ticket_payment,
        tickets,
        payment_start_at,
        payment_due_at,
        ticketing_start_at,
        ticketing_end_at,
        payment_sheet_text,
        require_ticketing_fee_on_ticketing
        ):
    famiport_order = get_famiport_order(
        session,
        order_no=(order_no if order_no is not Unspecified else None),
        famiport_order_identifier=(famiport_order_identifier if famiport_order_identifier is not Unspecified else None),
        client_code=client_code
        )

    if famiport_order.canceled_at is not None:
        raise FamiPortAlreadyCanceledError('FamiPortOrder(id=%ld) is already canceled' % famiport_order.id)

    if famiport_order.type != type_:
        raise FamiPortError(u'type differs')

    famiport_sales_segment = famiport_order.famiport_sales_segment
    famiport_performance = famiport_order.famiport_performance
    famiport_event = famiport_performance.famiport_event

    if event_code_1 is Unspecified:
        if event_code_2 is Unspecified:
            event_code_1 = famiport_event.code_1
            event_code_2 = famiport_event.code_2
            if performance_code is Unspecified:
                performance_code = famiport_performance.code
                if sales_segment_code is Unspecified:
                    if famiport_sales_segment is not None:
                        sales_segment_code = famiport_sales_segment.code
            elif sales_segment_code is Unspecified:
                raise FamiPortError('sales_segment_code may not be left Unspecified when the performance is being changed')
        else:
            raise FamiPortError('neither event_code_1 nor event_code_2 can be Unspecified while the other is not Unspecified')
    elif performance_code is Unspecified or sales_segment_code is Unspecified:
        raise FamiPortError('performance_code or sales_segment_code may not be left when the event is being changed')

    event_differs = False
    performance_differs = False
    sales_segment_differs = False

    if famiport_event.code_1 != event_code_1 or famiport_event.code_2 != event_code_2:
        logger.warning(
            u'event_code_1, event_code_2 differs ('
            u'original_event_code_1={original_event_code_1}, '
            u'original_event_code_2={original_event_code_2}, '
            u'original_performance_code={original_performance_code}, '
            u'original_sales_segment_code={original_sales_segment_code}, '
            u'new_event_code_1={event_code_1}, '
            u'new_event_code_2={event_code_2}, '
            u'new_performance_code={performance_code}, '
            u'new_sales_segment_code={sales_segment_code})'.format(
                original_event_code_1=famiport_event.code_1,
                original_event_code_2=famiport_event.code_2,
                original_performance_code=famiport_performance.code,
                original_sales_segment_code=(famiport_sales_segment.code if famiport_sales_segment is not None else None),
                event_code_1=event_code_1,
                event_code_2=event_code_2,
                performance_code=performance_code,
                sales_segment_code=sales_segment_code
                )
            )
        event_differs = True
    elif famiport_performance.code != performance_code:
        logger.warning(
            u'performance_code differs ('
            u'original_event_code_1={original_event_code_1}, '
            u'original_event_code_2={original_event_code_2}, '
            u'original_performance_code={original_performance_code}, '
            u'original_sales_segment_code={original_sales_segment_code}, '
            u'new_event_code_1={event_code_1}, '
            u'new_event_code_2={event_code_2}, '
            u'new_performance_code={performance_code}, '
            u'new_sales_segment_code={sales_segment_code})'.format(
                original_event_code_1=famiport_event.code_1,
                original_event_code_2=famiport_event.code_2,
                original_performance_code=famiport_performance.code,
                original_sales_segment_code=(famiport_sales_segment.code if famiport_sales_segment is not None else None),
                event_code_1=event_code_1,
                event_code_2=event_code_2,
                performance_code=performance_code,
                sales_segment_code=sales_segment_code
                )
            )
        performance_differs = True
    elif famiport_sales_segment is not None and famiport_sales_segment.code != sales_segment_code:
        logger.warning(
            u'sales_segment_code differs ('
            u'original_event_code_1={original_event_code_1}, '
            u'original_event_code_2={original_event_code_2}, '
            u'original_performance_code={original_performance_code}, '
            u'original_sales_segment_code={original_sales_segment_code}, '
            u'new_event_code_1={event_code_1}, '
            u'new_event_code_2={event_code_2}, '
            u'new_performance_code={performance_code}, '
            u'new_sales_segment_code={sales_segment_code})'.format(
                original_event_code_1=famiport_event.code_1,
                original_event_code_2=famiport_event.code_2,
                original_performance_code=famiport_performance.code,
                original_sales_segment_code=(famiport_sales_segment.code if famiport_sales_segment is not None else None),
                event_code_1=event_code_1,
                event_code_2=event_code_2,
                performance_code=performance_code,
                sales_segment_code=sales_segment_code
                )
            )
        sales_segment_differs = True

    if event_differs:
        try:
            famiport_event = get_famiport_event_by_code(
                session,
                client_code=client_code,
                code_1=famiport_event.code_1,
                code_2=famiport_event.code_2
                )
        except NoResultFound:
            raise FamiPortError(u'FamiPortEvent not found for client_code=%s, code_1=%s, code_2=%s' % (client_code, event_code_1, event_code_2))
        performance_differs = True

    if performance_differs:
        try:
            famiport_performance = get_famiport_performance_by_code(
                session,
                client_code=client_code,
                event_code_1=event_code_1,
                event_code_2=event_code_2,
                code=performance_code
                )
        except NoResultFound:
            raise FamiPortError(u'FamiPortPerformance not found for client_code=%s, event_code_1=%s, event_code_2=%s, code=%s' % (client_code, event_code_1, event_code_2, performance_code))
        sales_segment_differs = True

    if sales_segment_differs:
        if sales_segment_code is not None:
            try:
                famiport_sales_segment = get_famiport_sales_segment_by_code(
                    session,
                    client_code=client_code,
                    event_code_1=event_code_1,
                    event_code_2=event_code_2,
                    performance_code=performance_code,
                    code=sales_segment_code
                    )
            except NoResultFound:
                raise FamiPortError(u'FamiPortSalesSegment not found for client_code=%s, event_code_1=%s, event_code_2=%s, performance_code=%s, code=%s' % (client_code, event_code_1, event_code_2, performance_code, sales_segment_code))
        else:
            famiport_sales_segment = None

    def check_updatable(payment_related=False, ticketing_related=False):
        if famiport_order.type in (FamiPortOrderType.CashOnDelivery.value, FamiPortOrderType.Payment.value, FamiPortOrderType.PaymentOnly.value):
            if payment_related and famiport_order.paid_at is not None:
                raise FamiPortAlreadyPaidError(u'すでに支払い済みの予約です。FamiPortOrder(id=%ld)' % famiport_order.id)
        if famiport_order.type in (FamiPortOrderType.CashOnDelivery.value, FamiPortOrderType.Ticketing.value):
            if ticketing_related and famiport_order.issued_at is not None:
                raise FamiPortAlreadyIssuedError('FamiPortOrder(id=%ld) is already issued' % famiport_order.id)

    _total_amount = famiport_order.total_amount
    _system_fee = famiport_order.system_fee
    _ticketing_fee = famiport_order.ticketing_fee
    _ticket_payment = famiport_order.ticket_payment
    _payment_start_at = famiport_order.payment_start_at
    _payment_due_at = famiport_order.payment_due_at
    _ticketing_start_at = famiport_order.ticketing_start_at
    _ticketing_end_at = famiport_order.ticketing_end_at

    if total_amount is not Unspecified and total_amount != _total_amount:
        check_updatable(payment_related=True, ticketing_related=False)
        _total_amount = total_amount
    if system_fee is not Unspecified and system_fee != _system_fee:
        check_updatable(payment_related=True, ticketing_related=False)
        _system_fee = system_fee
    if ticketing_fee is not Unspecified and ticketing_fee != _ticketing_fee:
        check_updatable(payment_related=True, ticketing_related=False)
        _ticketing_fee = ticketing_fee
    if ticket_payment is not Unspecified and ticket_payment != _ticket_payment:
        check_updatable(payment_related=True, ticketing_related=False)
        _ticket_payment = ticket_payment
    if payment_start_at is not Unspecified and payment_start_at != _payment_start_at:
        check_updatable(payment_related=True, ticketing_related=False)
        _payment_start_at = payment_start_at
    if payment_due_at is not Unspecified and payment_due_at != _payment_due_at:
        check_updatable(payment_related=True, ticketing_related=False)
        _payment_due_at = payment_due_at
    if ticketing_start_at is not Unspecified and ticketing_start_at != _ticketing_start_at:
        if famiport_order.type == FamiPortOrderType.CashOnDelivery:
            ticketing_start_at = _payment_start_at
        check_updatable(payment_related=False, ticketing_related=True)
        _ticketing_start_at = ticketing_start_at
    if ticketing_end_at is not Unspecified and ticketing_end_at != _ticketing_end_at:
        if famiport_order.type == FamiPortOrderType.CashOnDelivery:
            ticketing_end_at = _payment_due_at
        check_updatable(payment_related=False, ticketing_related=True)
        _ticketing_end_at = ticketing_end_at

    logger.debug(
        'payment_start_at=%r, payment_due_at=%r, ticketing_start_at=%r, ticketing_due_at=%r' % (
            payment_start_at,
            payment_due_at,
            ticketing_start_at,
            ticketing_end_at,
            )
        )

    validate_order_info(
        famiport_order.type,
        payment_start_at=_payment_start_at,
        payment_due_at=_payment_due_at,
        ticketing_start_at=_ticketing_start_at,
        ticketing_end_at=_ticketing_end_at,
        ticket_payment=_ticket_payment,
        ticketing_fee=_ticketing_fee,
        system_fee=_system_fee,
        total_amount=_total_amount
        )

    added_famiport_tickets = None
    deleted_famiport_tickets = None 
    if tickets is not Unspecified:
        check_updatable(payment_related=False, ticketing_related=True)
        added_famiport_tickets = []
        updated_famiport_ticket_count = 0
        ticket_map = {
            famiport_ticket.barcode_number: famiport_ticket
            for famiport_ticket in famiport_order.famiport_tickets
            }
        for ticket_dict in tickets:
            famiport_ticket = ticket_map.pop(ticket_dict['barcode_number']) if 'barcode_number' in ticket_dict else None
            if famiport_ticket is not None:
                famiport_ticket.type = ticket_dict['type']
                famiport_ticket.template_code = ticket_dict['template']
                famiport_ticket.data = ticket_dict['data']
                famiport_ticket.logically_subticket = ticket_dict['logically_subticket']
                updated_famiport_ticket_count += 1
            else:
                famiport_ticket = create_famiport_ticket(session, famiport_order.famiport_client.playguide, ticket_dict)
                added_famiport_tickets.append(famiport_ticket)
        deleted_famiport_tickets = ticket_map.values()
        logger.info('added tickets: %d; updated tickets: %d; deleted tickets: %d' % (len(added_famiport_tickets), updated_famiport_ticket_count, len(deleted_famiport_tickets)))

    famiport_order.famiport_performance = famiport_performance
    famiport_order.famiport_sales_segment = famiport_sales_segment

    if customer_name is not Unspecified:
        logger.info('updating FamiPortOrder(id=%ld).customer_name' % famiport_order.id)
        famiport_order.customer_name = customer_name
    if customer_phone_number is not Unspecified:
        logger.info('updating FamiPortOrder(id=%ld).customer_phone_number' % famiport_order.id)
        famiport_order.customer_phone_number = customer_phone_number
    if customer_address_1 is not Unspecified:
        logger.info('updating FamiPortOrder(id=%ld).customer_address_1' % famiport_order.id)
        famiport_order.customer_address_1 = customer_address_1
    if customer_address_2 is not Unspecified:
        logger.info('updating FamiPortOrder(id=%ld).customer_address_2' % famiport_order.id)
        famiport_order.customer_address_2 = customer_address_2
    if total_amount is not Unspecified:
        logger.info('updating FamiPortOrder(id=%ld).total_amount' % famiport_order.id)
        famiport_order.total_amount = total_amount
    if system_fee is not Unspecified:
        logger.info('updating FamiPortOrder(id=%ld).system_fee' % famiport_order.id)
        famiport_order.system_fee = system_fee
    if ticketing_fee is not Unspecified:
        logger.info('updating FamiPortOrder(id=%ld).ticketing_fee' % famiport_order.id)
        famiport_order.ticketing_fee = ticketing_fee
    if ticket_payment is not Unspecified:
        logger.info('updating FamiPortOrder(id=%ld).ticket_payment' % famiport_order.id)
        famiport_order.ticket_payment = ticket_payment
    if added_famiport_tickets or deleted_famiport_tickets:
        logger.info('updating FamiPortOrder(id=%ld).famiport_tickets' % famiport_order.id)
        famiport_order.famiport_tickets.extend(added_famiport_tickets)
        for famiport_ticket in deleted_famiport_tickets:
            famiport_order.famiport_tickets.remove(famiport_ticket)
    if payment_start_at is not Unspecified:
        logger.info('updating FamiPortOrder(id=%ld).payment_start_at' % famiport_order.id)
        famiport_order.payment_start_at = payment_start_at
    if payment_due_at is not Unspecified:
        logger.info('updating FamiPortOrder(id=%ld).payment_due_at' % famiport_order.id)
        famiport_order.payment_due_at = payment_due_at
    if ticketing_start_at is not Unspecified:
        logger.info('updating FamiPortOrder(id=%ld).ticketing_start_at' % famiport_order.id)
        famiport_order.ticketing_start_at = ticketing_start_at
    if ticketing_end_at is not Unspecified:
        logger.info('updating FamiPortOrder(id=%ld).ticketing_end_at' % famiport_order.id)
        famiport_order.ticketing_end_at = ticketing_end_at
    if payment_sheet_text is not Unspecified:
        logger.info('updating FamiPortOrder(id=%ld).payment_sheet_text' % famiport_order.id)
        famiport_order.payment_sheet_text = payment_sheet_text
    if require_ticketing_fee_on_ticketing is not Unspecified:
        logger.info('updating FamiPortOrder(id=%ld).require_ticketing_fee_on_ticketing' % famiport_order.id)
        famiport_order.require_ticketing_fee_on_ticketing = require_ticketing_fee_on_ticketing


def get_or_create_refund(
        session,
        client_code,
        userside_id,
        refund_id,
        send_back_due_at,
        start_at,
        end_at):
    if userside_id is None and refund_id is None:
        raise FamiPortError('either userside_id or refund_id can be None')
    q = session.query(FamiPortRefund).filter_by(client_code=client_code)
    if userside_id is not None:
        q = q.filter_by(userside_id=userside_id)
    elif refund_id is not None:
        q = q.filter_by(id=refund_id)
    famiport_refund = None
    try:
        famiport_refund = q.one()
    except NoResultFound:
        pass
    if famiport_refund is None:
        famiport_refund = FamiPortRefund(
            client_code=client_code,
            userside_id=userside_id,
            send_back_due_at=send_back_due_at,
            start_at=start_at,
            end_at=end_at
            )
        session.add(famiport_refund)
        return famiport_refund, True
    else:
        return famiport_refund, False

def _get_ticket_count_group_by_token(request, famiport_order_id):
    session = get_db_session(request, 'famiport_slave')

    # 一つ商品明細トークンが複数主券を持つ場合はトークンのIDが一つしかないため
    # トークンのIDをGROUP BYで主券の数を得る
    results = session.query(
        FamiPortTicket.userside_token_id.label('token_id'),
        func.count(FamiPortTicket.id).label('cnt')) \
        .filter(FamiPortTicket.famiport_order_id == famiport_order_id) \
        .filter(FamiPortTicket.logically_subticket == False) \
        .filter(FamiPortTicket.type.in_([FamiPortTicketType.Ticket.value, FamiPortTicketType.TicketWithBarcode.value])) \
        .group_by(FamiPortTicket.userside_token_id) \
        .all()

    return {result.token_id: int(result.cnt) for result in results}

def _get_ticket_amount(ticket_price, cnt, is_first):
    """
    :param ticket_price: Decimal
    :param cnt: int
    :param is_first: bool
    :return: Decimal
    """
    # 一つ商品明細トークンが複数主券を持つ場合は払戻のチケット代をチケットの数で割る
    # チケット枚数で金額を割り切れない対応するために、切り捨てでticketの金額を計算する
    ticket_amount = (ticket_price/cnt).quantize(Decimal('1.'), rounding=ROUND_DOWN)
    # 割り切れない余りを1つ目のチケットにつける
    if is_first:
        remainder = ticket_price % cnt
        ticket_amount += remainder
    return ticket_amount

def refund_order_by_order_no(
        request,
        client_code,
        refund_id,
        order_no,
        famiport_order_identifier,
        per_order_fee,
        per_ticket_fee,
        refund_total_amount):
    session = get_db_session(request, 'famiport')
    famiport_order = get_famiport_order(session, client_code=client_code, order_no=order_no, famiport_order_identifier=famiport_order_identifier)

    if famiport_order.canceled_at:
        raise FamiPortError(u'famiport_order: %s is already canceled' % famiport_order.order_no)

    famiport_tickets = sorted([famiport_ticket
                               for famiport_ticket in famiport_order.famiport_tickets
                               if not famiport_ticket.is_subticket],
                              key=lambda x: x.id)

    if len(famiport_tickets) == 0:
        raise FamiPortError('no tickets can be refunded')

    try:
        famiport_refund = session.query(FamiPortRefund).filter_by(client_code=client_code, id=refund_id).with_lockmode('update').one()
    except NoResultFound:
        raise FamiPortError('no corresponding FamiPortRefund found (refund_id=%ld)' % refund_id)

    # 一つ商品明細トークンが持ってるFamiPortチケットの数を取得
    ticket_cnt = _get_ticket_count_group_by_token(request, famiport_order.id)
    # Refund検証ための変数を設定
    refund_ticket_cnt = 0
    total_amount_for_check = 0
    serial = famiport_refund.last_serial
    for famiport_ticket in famiport_tickets:

        famiport_refund_entry = session.query(FamiPortRefundEntry) \
            .join(FamiPortTicket) \
            .filter(FamiPortRefundEntry.famiport_refund_id == famiport_refund.id) \
            .filter(FamiPortTicket.famiport_order_id == famiport_order.id) \
            .filter(FamiPortTicket.id == famiport_ticket.id) \
            .first()
        if not famiport_refund_entry:
            famiport_refund_entry = FamiPortRefundEntry()

        # 主券の数で実際払戻金額を計算
        ticket_amount = _get_ticket_amount(famiport_ticket.price,
                                           ticket_cnt.get(famiport_ticket.userside_token_id, 1),
                                           refund_ticket_cnt == 0)

        # すべてが0の場合はデータを追加しない
        if ticket_amount == 0 and (per_order_fee == 0 or refund_ticket_cnt > 0) and per_ticket_fee == 0:
            if famiport_refund_entry.id:
                session.delete(famiport_refund_entry)
            continue

        if famiport_refund_entry.id:
            logger.info('FamiPortRefundEntry(id=%ld) will be updated' % famiport_refund_entry.id)
            if famiport_refund_entry.refunded_at:
                raise FamiPortError('FamiPortRefundEntry(id=%ld) is already refunded at %s' % (
                    famiport_refund_entry.id,
                    famiport_refund_entry.refunded_at
                ))
            if famiport_refund_entry.ticket_payment != ticket_amount:
                logger.info(
                    'FamiPortRefundEntry(id=%ld).ticket_payment: %s => %s' % (
                        famiport_refund_entry.id,
                        famiport_refund_entry.ticket_payment,
                        ticket_amount
                    )
                )
            if famiport_refund_entry.ticketing_fee != per_ticket_fee:
                logger.info(
                    'FamiPortRefundEntry(id=%ld).ticketing_fee: %s => %s' % (
                        famiport_refund_entry.id,
                        famiport_refund_entry.ticketing_fee,
                        per_ticket_fee
                    )
                )
            if refund_ticket_cnt == 0 and famiport_refund_entry.other_fees != per_order_fee:
                logger.info(
                    'FamiPortRefundEntry(id=%ld).other_fees: %s => %s' % (
                        famiport_refund_entry.id,
                        famiport_refund_entry.ticketing_fee,
                        per_ticket_fee
                    )
                )
        else:
            logger.info(
                'FamiPortRefundEntry(famiport_ticket_id=%ld, ticket_payment=%s, ticketing_fee=%s, other_fees=%s, shop_code=%s) will be added' % (
                    famiport_ticket.id,
                    ticket_amount,
                    per_ticket_fee,
                    per_order_fee if refund_ticket_cnt == 0 else 0,
                    famiport_order.ticketing_famiport_receipt.shop_code
                ))
            serial += 1
            famiport_refund_entry.serial = serial

        famiport_refund_entry.famiport_refund = famiport_refund
        famiport_refund_entry.famiport_ticket = famiport_ticket
        famiport_refund_entry.ticket_payment = ticket_amount
        famiport_refund_entry.ticketing_fee = per_ticket_fee
        famiport_refund_entry.other_fees = per_order_fee if refund_ticket_cnt == 0 else 0
        famiport_refund_entry.shop_code=famiport_order.ticketing_famiport_receipt.shop_code

        # チケットデータの状態不正などにより払戻データの合計額が予約金額を超える場合はエラーにする
        total_amount_for_check += famiport_refund_entry.ticket_payment \
                                  + famiport_refund_entry.ticketing_fee \
                                  + famiport_refund_entry.other_fees

        if refund_total_amount < total_amount_for_check:
            logger.error(u'check over amount {0} < {1}'.format(refund_total_amount, total_amount_for_check))
            raise FamiPortError(
                u'refund total amount over: {0} < {1}'.format(refund_total_amount, total_amount_for_check))

        session.add(famiport_refund_entry)
        refund_ticket_cnt += 1

    if refund_ticket_cnt == 0:
        logger.warning(u'No refundable tickets found: %s' % famiport_order.order_no)

    famiport_refund.last_serial = serial
    session.commit()

def invalidate_famiport_event(session, userside_id, now):
    famiport_event = session.query(FamiPortEvent)\
        .filter(FamiPortEvent.userside_id == userside_id)\
        .filter(FamiPortEvent.invalidated_at == None)\
        .one()
    famiport_event.invalidated_at = now
