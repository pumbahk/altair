# -*- coding: utf-8-*-
from .builders import XmlFamiPortResponseGenerator
from .interfaces import IFamiPortResponseBuilderRegistry, IFamiPortTicketPreviewAPI


def get_response_builder(request, famiport_request):
    """Get appropriate FamiPortResponseBuilder for the given FamiPortRequest.

    :param famiport_request: FamiPortRequest object to get FamiPortResponseBuilder for.
    :return: Instance object of appropriate FamiPortResponseBuilder for famiport_request.
    """
    builder_registry = request.registry.queryUtility(IFamiPortResponseBuilderRegistry)
    return builder_registry.lookup(famiport_request)


def get_xmlResponse_generator(famiport_response):
    """Get appropriate XmlFamiPortResponseGenerator for the given FamiPortResponse

    :param famiport_response: FamiPortResponse object to get XmlFamiPortResponseGenerator for.
    :return: XmlFamiPortResponseGenerator instance to generate XML of famiport_response.
    """
    return XmlFamiPortResponseGenerator(famiport_response)

def get_ticket_preview_api(request):
    preview_api = request.registry.queryUtility(IFamiPortTicketPreviewAPI)
    return preview_api

def get_ticket_preview_pictures(request, discrimination_code, client_code, order_id, barcode_no, name, member_id, address_1, address_2, identify_no, tickets, response_image_type):
    preview_api = get_ticket_preview_api(request)
    return preview_api(request, discrimination_code, client_code, order_id, barcode_no, name, member_id, address_1, address_2, identify_no, tickets, response_image_type)


