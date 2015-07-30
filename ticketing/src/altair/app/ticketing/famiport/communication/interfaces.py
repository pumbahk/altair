# -*- coding: utf-8 -*-

from zope.interface import Interface


class IFamiPortResponseBuilderRegistry(Interface):
    def add(corresponding_request_type, builder):
        pass

    def lookup(famiport_request):
        pass


class IFamiPortResponseBuilder(Interface):
    # Build FamiPortResponse from FamiPortRequest
    def build_response(famiport_request=None):
        pass


class IXmlFamiPortResponseGenerator(Interface):
    # Generate XML text from famiport_response with encrypted_fields encrypted
    def generate_xmlResponse(famiport_response=None, encrypted_fields=[]):
        pass


class IFamiPortTicketPreviewAPI(Interface):
    def __call__(request, discrimination_code, client_code, order_id, barcode_no, name, member_id, address_1, address_2, identify_no, tickets, response_image_type):
        pass

