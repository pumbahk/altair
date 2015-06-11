# -*- coding: utf-8 -*-
from altair.sqlahelper import get_db_session
from .models import (
    FamiPortOrder,
    FamiPortTicket,
    FamiPortClient,
    FamiPortSalesSegment,
    FamiPortBarcodeNoSequence,
    FamiPortReserveNumberSequence,
    FamiPortOrderTicketNoSequence,
    FamiPortOrderIdentifierSequence,
    FamiPortExchangeTicketNoSequence,
    )
from .communication.api import (  # noqa
    get_response_builder,  # noqa B/W compatibility
    get_xmlResponse_generator,  # noqa B/W compatibility
    )


def get_famiport_order(request, order_no, session=None):
    if session is None:
        session = get_db_session(request, 'famiport')
    retval = session.query(FamiPortOrder) \
                    .filter(FamiPortOrder.order_no == order_no) \
                    .filter(FamiPortOrder.invalidated_at == None) \
                    .one()
    return retval


def get_famiport_client(request, client_code, session=None):
    if session is None:
        session = get_db_session(request, 'famiport')
    retval = session.query(FamiPortClient) \
                    .filter_by(code=client_code) \
                    .one()
    return retval


def get_famiport_sales_segment_by_userside_id(request, userside_id, session=None):
    if session is None:
        session = get_db_session(request, 'famiport')
    retval = session.query(FamiPortSalesSegment) \
                    .filter_by(userside_id=userside_id) \
                    .one()
    return retval


def create_famiport_ticket(request, ticket_dict, session=None):
    if session is None:
        session = get_db_session(request, 'famiport')
    return FamiPortTicket(
        type=ticket_dict['type'],
        barcode_number=FamiPortBarcodeNoSequence.get_next_value(session),
        template_code=ticket_dict['template'],
        data=ticket_dict['data']
        )


def create_famiport_order(
        request,
        client_code,
        type_,
        userside_sales_segment_id,
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
        session=None):
    """FamiPortOrderを作成する"""
    if session is None:
        session = get_db_session(request, 'famiport')
    famiport_client = get_famiport_client(request, client_code, session=session)
    famiport_order_identifier = FamiPortOrderIdentifierSequence.get_next_value(famiport_client.prefix, session),
    famiport_sales_segment = get_famiport_sales_segment_by_userside_id(request, userside_sales_segment_id, session=session)
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
        famiport_tickets=[
            create_famiport_ticket(request, ticket_dict, session)
            for ticket_dict in tickets
            ]
        )
    session.add(famiport_order)
    session.commit()
    return famiport_order


def do_order(*args, **kwds):
    return create_famiport_order(*args, **kwds)
