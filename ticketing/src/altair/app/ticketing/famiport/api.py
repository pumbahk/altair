# -*- coding:utf-8 -*-
from ..utils import sensible_alnum_encode
from .models import (
    _session,
    FamiPortOrder,
    FamiPortTicket,
    FamiPortBarcodeNoSequence,
    FamiPortReserveNumberSequence,
    FamiPortOrderTicketNoSequence,
    FamiPortOrderIdentifierSequence,
    FamiPortExchangeTicketNoSequence,
    )
from .builders import FamiPortResponseBuilderFactory, XmlFamiPortResponseGenerator


def get_response_builder(famiport_request):
    """Get appropriate FamiPortResponseBuilder for the given FamiPortRequest.

    :param famiport_request: FamiPortRequest object to get FamiPortResponseBuilder for.
    :return: Instance object of appropriate FamiPortResponseBuilder for famiport_request.
    """
    famiport_response_builder_factory = FamiPortResponseBuilderFactory()
    return famiport_response_builder_factory(famiport_request)


def get_xmlResponse_generator(famiport_response):
    """Get appropriate XmlFamiPortResponseGenerator for the given FamiPortResponse

    :param famiport_response: FamiPortResponse object to get XmlFamiPortResponseGenerator for.
    :return: XmlFamiPortResponseGenerator instance to generate XML of famiport_response.
    """
    return XmlFamiPortResponseGenerator(famiport_response)


def get_famiport_order(order_no, session=None):
    if session is None:
        session = _session
    retval = session.query(FamiPortOrder) \
                    .filter(FamiPortOrder.order_no == order_no) \
                    .filter(FamiPortOrder.invalidated_at == None) \
                    .one()
    return retval

def get_famiport_client(client_code, session=None):
    if session is None:
        session = _session
    retval = session.query(FamiPortClient) \
                    .filter_by(code=client_code) \
                    .one()
    return retval

def create_famiport_ticket(ticket_dict, session=None):
    if session is None:
        session = _session
    return FamiPortTicket(
        type=ticket_dict['type'],
        barcode_number=FamiPortBarcodeNoSequence.get_next_value(session),
        template_code=ticket_dict['template'],
        data=ticket_dict['data']
        )

def create_famiport_order(
        client_code,
        order_no,
        customer_name,
        customer_phone_number,
        customer_address_1,
        customer_address_2,
        total_amount,
        sytem_fee,
        ticketing_fee,
        ticket_payment,
        tickets,
        session=None):
    """FamiPortOrderを作成する"""
    if session is None:
        session = _session
    famiport_client = get_famiport_client(client_code, session=session)
    famiport_order = FamiPortOrder(
        order_no=order_no,
        barcode_no=famiport_client.prefix + FamiPortOrderIdentifierSequence.get_next_value(session),
        reserve_number=FamiPortReserveNumberSequence.get_next_value(session),
        order_ticket_no=famiport_order.barcode_no,
        famiport_order_identifier=FamiPortOrderIdentifierSequence.get_next_value(session),
        exchange_ticket_no=FamiPortExchangeTicketNoSequence.get_next_value(session),
        customer_name=customer_name,
        customer_phone_number=customer_phone_number,
        customer_address_1=customer_address_1,
        customer_address_2=customer_address_2,
        total_amount=total_amount,
        system_fee=system_fee,
        ticketing_fee=ticketing_fee,
        ticket_payment=ticket_payment,
        famiport_tickets=[
            create_famiport_ticket(ticket_dict, session)
            for ticket_dict in tickets
            ]
        )
    session.add(famiport_order)
    return famiport_order


def do_order(request, playguide, famiport_order, now=None, session=None):
    pass
