# -*- coding: utf-8 -*-
import sys
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
    FamiPortSalesSegment,
    FamiPortGenre1,
    FamiPortGenre2,
    FamiPortSalesChannel,
    FamiPortBarcodeNoSequence,
    FamiPortReserveNumberSequence,
    FamiPortOrderTicketNoSequence,
    FamiPortOrderIdentifierSequence,
    FamiPortExchangeTicketNoSequence,
    )
from .exc import FamiPortError, FamiPortAPIError, FamiPortAPINotFoundError
from .communication.api import (  # noqa
    get_response_builder,  # noqa B/W compatibility
    get_xmlResponse_generator,  # noqa B/W compatibility
    )

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

def get_famiport_order(session, order_no):
    retval = session.query(FamiPortOrder) \
                    .filter(FamiPortOrder.order_no == order_no) \
                    .filter(FamiPortOrder.invalidated_at == None) \
                    .one()
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

def create_famiport_ticket(session, ticket_dict):
    return FamiPortTicket(
        type=ticket_dict['type'],
        barcode_number=FamiPortBarcodeNoSequence.get_next_value(session),
        template_code=ticket_dict['template'],
        data=ticket_dict['data']
        )

def create_famiport_receipt(session, **kwds):
    return FamiPortReceipt(
        barcode_no=FamiPortBarcodeNoSequence.get_next_value(session),
        **kwds
        )

def validate_sales_channel(sales_channel):
    if sales_channel not in (FamiPortSalesChannel.FamiPortOnly.value, FamiPortSalesChannel.WebOnly.value, FamiPortSalesChannel.FamiPortAndWeb.value):
        raise FamiPortAPIError('invalid sales_channel: %d' % sales_channel)

def validate_prefecture(prefecture):
    if not FamiPortPrefecture.is_valid_id(prefecture):
        raise FamiPortAPIError('invalid prefecture: %d' % prefecture)

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
        ticketing_end_at=None
        ):
    """FamiPortOrderを作成する"""
    famiport_client = get_famiport_client(session, client_code)
    famiport_order_identifier = FamiPortOrderIdentifierSequence.get_next_value(famiport_client.prefix, session),
    if type in (FamiPortOrderType.CashOnDelivery.value, FamiPortOrderType.Payment.value, FamiPortOrderType.PaymentOnly.value):
        if payment_start_at is None:
            raise FamiPortError('payment_start_at is None while type=CashOnDelivery|Payment|PaymentOnly')
        if payment_due_at is None:
            raise FamiPortError('payment_due_at is None while type=CashOnDelivery|Payment|PaymentOnly')
    if type in (FamiPortOrderType.CashOnDelivery.value, FamiPortOrderType.Payment.value, FamiPortOrderType.Ticketing.value):
        if ticketing_start_at is None:
            raise FamiPortError('ticketing_start_at is None while type=CashOnDelivery|Payment|Ticketing')
        if ticketing_end_at is None:
            raise FamiPortError('payment_start_at is None while type=CashOnDelivery|Payment|Ticketing')
    famiport_order = FamiPortOrder(
        client_code=client_code,
        type=type_,
        order_no=order_no,
        famiport_sales_segment=famiport_sales_segment,
        famiport_order_identifier=famiport_order_identifier,
        reserve_number=FamiPortReserveNumberSequence.get_next_value(session),
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
            create_famiport_ticket(session, ticket_dict)
            for ticket_dict in tickets
            ]
        )
    session.add(famiport_order)
    session.commit()
    return famiport_order


