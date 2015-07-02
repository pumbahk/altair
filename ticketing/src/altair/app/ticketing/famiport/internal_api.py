# -*- coding: utf-8 -*-
import sys
import logging
from datetime import datetime
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from altair.sqlahelper import get_db_session
import functools
from .models import (
    FamiPortOrder,
    FamiPortOrderType,
    FamiPortTicket,
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
    )
from .exc import FamiPortError, FamiPortAPIError, FamiPortAPINotFoundError, FamiPortAlreadyPaidError, FamiPortAlreadyIssuedError, FamiPortAlreadyCanceledError
from .communication.api import (  # noqa
    get_response_builder,  # noqa B/W compatibility
    get_xmlResponse_generator,  # noqa B/W compatibility
    )

logger = logging.getLogger(__name__)

def get_famiport_sales_segment_by_code(session, event_code_1, event_code_2, performance_code, code):
    retval = session.query(FamiPortSalesSegment) \
                    .join(FamiPortSalesSegment.famiport_performance) \
                    .join(FamiPortPerformance.famiport_event) \
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

def get_famiport_performance_by_userside_id(session, client_code, userside_id):
    retval = session.query(FamiPortPerformance) \
                    .join(FamiPortPerformance.famiport_event) \
                    .filter(FamiPortEvent.client_code == client_code,
                            FamiPortPerformance.userside_id == userside_id) \
                    .filter(FamiPortEvent.invalidated_at == None) \
                    .filter(FamiPortPerformance.invalidated_at == None) \
                    .one()
    return retval

def get_famiport_event_by_userside_id(session, client_code, userside_id):
    retval = session.query(FamiPortEvent) \
                    .filter(FamiPortEvent.client_code == client_code,
                            FamiPortEvent.userside_id == userside_id) \
                    .filter(FamiPortEvent.invalidated_at == None) \
                    .one()
    return retval

def get_famiport_order(session, order_no=None, famiport_order_identifier=None):
    if order_no is None:
        if famiport_order_identifier is None:
            raise FamiPortError('order_no and famiport_order_identifier cannot be None at the same time')
        try:
            retval = session.query(FamiPortOrder) \
                .filter_by(FamiPortOrder.famiport_order_identifier == famiport_order_identifier) \
                .filter(FamiPortOrder.invalidated_at == None) \
                .one()
        except NoResultFound:
            raise FamiPortError('no corresponding order found for famiport_order_identifier=%s' % famiport_order_identifier)
    else:
        try:
            retval = session.query(FamiPortOrder) \
                .filter(FamiPortOrder.order_no == order_no) \
                .filter(FamiPortOrder.invalidated_at == None) \
                .one()
        except MultipleResultsFound:
            raise FamiPortError('multiple order exist for order_no=%s. use famiport_order_identifier to be more specific' % order_no)
        except NoResultFound:
            raise FamiPortError('no corresponding order found for order_no=%s' % order_no)
        if famiport_order_identifier is not None and retval.famiport_order_identifier != famiport_order_identifier:
            raise FamiPortError('famiport_order_identifier differs (%s != %s)' % famiport_order_identifier, retval.famiport_order_identifier)
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
            raise FamiPortError('payment_start_at is None while type=CashOnDelivery|Payment|PaymentOnly')
        if payment_due_at is None:
            raise FamiPortError('payment_due_at is None while type=CashOnDelivery|Payment|PaymentOnly')
        if payment_start_at > payment_due_at:
            raise FamiPortError('payment_due_at is later than payment_start_at')
    if type_ in (FamiPortOrderType.CashOnDelivery.value, FamiPortOrderType.Payment.value, FamiPortOrderType.Ticketing.value):
        if ticketing_start_at is None:
            raise FamiPortError('ticketing_start_at is None while type=Payment|Ticketing')
        if ticketing_end_at is None:
            raise FamiPortError('payment_start_at is None while type=Payment|Ticketing')
        if ticketing_start_at > ticketing_end_at:
            raise FamiPortError('ticketing_end_at is later than ticketing_start_at')
    if ticket_payment + ticketing_fee + system_fee != total_amount:
        raise FamiPortError('ticketing_payment + ticketing_fee + system_fee != total_amount')

def create_famiport_order(
        session, 
        client_code,
        type_,
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
        created_at=now,
        updated_at=now
        )
    session.add(famiport_order)
    session.flush()
    famiport_order.add_receipts()
    session.commit()
    return famiport_order

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
    famiport_order = get_famiport_order(session, order_no)
    famiport_order.mark_canceled(now, request)


def mark_order_reissueable_by_order_no(
        session, 
        client_code,
        order_no,
        now=None
        ):
    """FamiPortOrderに再発券許可"""
    if now is None:
        now = datetime.now()
    famiport_order = get_famiport_order(session, order_no)
    famiport_order.make_reissueable(now)


def make_suborder_by_order_no(
        request,
        session,
        order_no,
        reason=None,
        cancel_reason_code=None,
        cancel_reason_text=None,
        client_code=None,
        now=None
        ):
    """FamiPortOrderを同席番再予約"""
    if now is None:
        now = datetime.now()
    famiport_order = get_famiport_order(session, order_no)
    famiport_order.make_suborder(now, request, reason, cancel_reason_code, cancel_reason_text)

def update_famiport_order_by_order_no(
        session,
        client_code,
        order_no,
        famiport_order_identifier,
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
        ticketing_end_at
        ):
    famiport_order = get_famiport_order(session, order_no=order_no, famiport_order_identifier=famiport_order_identifier)

    if famiport_order.canceled_at is not None:
        raise FamiPortAlreadyCanceledError('FamiPortOrder(id=%ld) is already canceled' % famiport_order.id)

    def check_updatable(payment_related=False, ticketing_related=False):
        if famiport_order.type in (FamiPortOrderType.CashOnDelivery.value, FamiPortOrderType.Payment.value, FamiPortOrderType.PaymentOnly.value):
            if payment_related and famiport_order.paid_at is not None:
                raise FamiPortAlreadyPaidError('FamiPortOrder(id=%ld) is already paid' % famiport_order.id)
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

    if total_amount is not None and total_amount != _total_amount:
        check_updatable(payment_related=True, ticketing_related=False)
        _total_amount = total_amount
    if system_fee is not None and system_fee != _system_fee:
        check_updatable(payment_related=True, ticketing_related=False)
        _system_fee = system_fee
    if ticketing_fee is not None and ticketing_fee != _ticketing_fee:
        check_updatable(payment_related=True, ticketing_related=False)
        _ticketing_fee = ticketing_fee
    if ticket_payment is not None and ticket_payment != _ticket_payment:
        check_updatable(payment_related=True, ticketing_related=False)
        _ticket_payment = ticket_payment
    if payment_start_at is not None and payment_start_at != _payment_start_at:
        check_updatable(payment_related=True, ticketing_related=False)
        _payment_start_at = payment_start_at
    if payment_due_at is not None and payment_due_at != _payment_due_at:
        check_updatable(payment_related=True, ticketing_related=False)
        _payment_due_at = payment_due_at
    if ticketing_start_at is not None and ticketing_start_at != _ticketing_start_at:
        if famiport_order.type == FamiPortOrderType.CashOnDelivery:
            ticketing_start_at = _payment_start_at
        check_updatable(payment_related=False, ticketing_related=True)
        _ticketing_start_at = ticketing_start_at
    if ticketing_end_at is not None and ticketing_end_at != _ticketing_end_at:
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

    famiport_tickets = None
    if tickets is not None:
        check_updatable(payment_related=False, ticketing_related=True)
        famiport_tickets = []
        ticket_map = {
            famiport_ticket.barcode_number: famiport_ticket
            for famiport_ticket in famiport_order.famiport_tickets
            }
        for ticket_dict in tickets:
            famiport_ticket = ticket_map.get(ticket_dict['barcode_number'])
            if famiport_ticket is not None:
                famiport_ticket.type = ticket_dict['type']
                famiport_ticket.template_code = ticket_dict['template']
                famiport_ticket.data = ticket_dict['data']
                famiport_ticket.logically_subticket = ticket_dict['logically_subticket']
            else:
                famiport_ticket = create_famiport_ticket(session, famiport_order.famiport_client.playguide, ticket_dict)
            famiport_tickets.append(famiport_ticket)

    if customer_name is not None:
        logger.info('updating FamiPortOrder(id=%ld).customer_name' % famiport_order.id)
        famiport_order.customer_name = customer_name
    if customer_phone_number is not None:
        logger.info('updating FamiPortOrder(id=%ld).customer_phone_number' % famiport_order.id)
        famiport_order.customer_phone_number = customer_phone_number
    if customer_address_1 is not None:
        logger.info('updating FamiPortOrder(id=%ld).customer_address_1' % famiport_order.id)
        famiport_order.customer_address_1 = customer_address_1
    if customer_address_2 is not None:
        logger.info('updating FamiPortOrder(id=%ld).customer_address_2' % famiport_order.id)
        famiport_order.customer_address_2 = customer_address_2
    if total_amount is not None:
        logger.info('updating FamiPortOrder(id=%ld).total_amount' % famiport_order.id)
        famiport_order.total_amount = total_amount
    if system_fee is not None:
        logger.info('updating FamiPortOrder(id=%ld).system_fee' % famiport_order.id)
        famiport_order.system_fee = system_fee
    if ticketing_fee is not None:
        logger.info('updating FamiPortOrder(id=%ld).ticketing_fee' % famiport_order.id)
        famiport_order.ticketing_fee = ticketing_fee
    if ticket_payment is not None:
        logger.info('updating FamiPortOrder(id=%ld).ticket_payment' % famiport_order.id)
        famiport_order.ticket_payment = ticket_payment
    if famiport_tickets is not None:
        logger.info('updating FamiPortOrder(id=%ld).famiport_tickets' % famiport_order.id)
        famiport_order.famiport_tickets = famiport_tickets
    if payment_start_at is not None:
        logger.info('updating FamiPortOrder(id=%ld).payment_start_at' % famiport_order.id)
        famiport_order.payment_start_at = payment_start_at
    if payment_due_at is not None:
        logger.info('updating FamiPortOrder(id=%ld).payment_due_at' % famiport_order.id)
        famiport_order.payment_due_at = payment_due_at
    if ticketing_start_at is not None:
        logger.info('updating FamiPortOrder(id=%ld).ticketing_start_at' % famiport_order.id)
        famiport_order.ticketing_start_at = ticketing_start_at
    if ticketing_end_at is not None:
        logger.info('updating FamiPortOrder(id=%ld).ticketing_end_at' % famiport_order.id)
        famiport_order.ticketing_end_at = ticketing_end_at
    
