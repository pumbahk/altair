# -*- coding:utf-8 -*-
from ..utils import sensible_alnum_encode
from .models import (
    _session,
    FamiPortOrder,
    FamiPortOrderNoSequence,
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


def get_next_barcode_no(request, organization, name='famiport'):
    base_id = FamiPortOrderNoSequence.get_next_value(name)
    return organization.code + sensible_alnum_encode(base_id).zfill(11)


def get_reserve_number(request, organization, name=''):
    return FamiPortReserveNumberSequence.get_next_value()


def get_order_ticket_no(request, organization, name='famiport'):
    return FamiPortOrderTicketNoSequence.get_next_value()


def get_famiport_order_identifier(request, organization, name='famiport'):
    return FamiPortOrderIdentifierSequence.get_next_value()


def get_exchange_ticket_no(request, organization, name='famiport'):
    return FamiPortExchangeTicketNoSequence.get_next_value()


def create_famiport_order(request, order_like, in_payment, name='famiport'):
    """FamiPortOrderを作成する

    クレカ決済などで決済をFamiPortで実施しないケースはin_paymentにFalseを指定する。
    """
    famiport_order = FamiPortOrder()
    famiport_order.order_no = order_like.order_no
    famiport_order.barcode_no = get_next_barcode_no(request, order_like.organization, name)
    famiport_order.reserve_number = get_reserve_number(request, order_like.organization, name)
    famiport_order.order_ticket_no = get_order_ticket_no(request, order_like.organization, name)
    famiport_order.famiport_order_identifier = get_famiport_order_identifier(request, order_like.organization, name)
    famiport_order.exchange_ticket_no = get_exchange_ticket_no(request, order_like.organization, name)

    famiport_order.address_1 = order_like.shipping_address.prefecture + order_like.shipping_address.city + order_like.shipping_address.address_1
    famiport_order.address_2 = order_like.shipping_address.address_2

    if in_payment:
        famiport_order.total_amount = order_like.total_amount
        famiport_order.system_fee = order_like.transaction_fee + order_like.system_fee + order_like.special_fee
        famiport_order.ticketing_fee = order_like.delivery_fee
        famiport_order.ticket_payment = order_like.total_amount - \
            (order_like.system_fee + order_like.transaction_fee + order_like.delivery_fee + order_like.special_fee)
    else:  # FamiPortで決済しない場合は0をセットする
        famiport_order.total_amount = 0
        famiport_order.system_fee = 0
        famiport_order.ticketing_fee = 0
        famiport_order.ticket_payment = 0
    famiport_order.name = order_like.shipping_address.last_name + order_like.shipping_address.first_name
    famiport_order.phone_number = (order_like.shipping_address.tel_1 or order_like.shipping_address.tel_2).replace('-', '')
    famiport_order.koen_date = order_like.sales_segment.performance.start_on
    famiport_order.kogyo_name = order_like.sales_segment.event.title
    famiport_order.ticket_count = len([item for product in order_like.items for item in product.items])
    famiport_order.ticket_total_count = len([item for product in order_like.items for item in product.items])
    _session.add(famiport_order)
    _session.flush()
    return famiport_order
