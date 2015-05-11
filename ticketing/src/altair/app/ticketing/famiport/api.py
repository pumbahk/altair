# -*- coding:utf-8 -*-
from ..utils import sensible_alnum_encode
from .models import (
    FamiPortOrder,
    FamiPortOrderNoSequence,
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


def create_famiport_order(request, order_like, name='famiport'):
    famiport_order = FamiPortOrder()
    famiport_order.order_no = order_like.order_no
    famiport_order.barcode_no = get_next_barcode_no(request, order_like.organization, name)
    famiport_order.save()
    return famiport_order
