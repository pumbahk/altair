# -*- coding: utf-8 -*-

from zope.interface import implementer
from .interfaces import IFamiPortResponseBuilderFactory, IFamiPortResponseBuilder, IXmlFamiPortResponseGenerator
from .utils import FamiPortRequestType, FamiPortCrypt

from xml.etree import ElementTree as ElementTree
from io import BytesIO

import logging

logger = logging.getLogger(__name__)

@implementer(IFamiPortResponseBuilderFactory)
class FamiPortResponseBuilderFactory(object):
    def __init__(self, *args, **kwargs):
        pass

    def __call__(self, famiport_request):
        request_type = famiport_request.request_type()
        if request_type == FamiPortRequestType.ReservationInquiry:
            return  FamiPortReservationInquiryResponseBuilder()
        elif request_type == FamiPortRequestType.PaymentTicketing:
            return FamiPortPaymentTicketingResponseBuilder()
        elif request_type == FamiPortRequestType.PaymentTicketingCompletion:
            return FamiPortPaymentTicketingCompletionResponseBuilder()
        elif request_type == FamiPortRequestType.PaymentTicketingCancel:
            return FamiPortPaymentTicketingCancelResponseBuilder()
        elif request_type == FamiPortRequestType.Information:
            return FamiPortInformationResponseBuilder()
        else:
            pass

@implementer(IFamiPortResponseBuilder)
class FamiPortResponseBuilder(object):
    def __init__(self, *args, **kwargs):
        pass

    def build_response(famiport_request=None):
        pass

class FamiPortReservationInquiryResponseBuilder(FamiPortResponseBuilder):
    def build_response(famiport_request=None):
        pass

class FamiPortPaymentTicketingResponseBuilder(FamiPortResponseBuilder):
    def build_response(famiport_request=None):
        pass

class FamiPortPaymentTicketingCompletionResponseBuilder(FamiPortResponseBuilder):
    def build_response(famiport_request=None):
        pass

class FamiPortPaymentTicketingCancelResponseBuilder(FamiPortResponseBuilder):
    def build_response(famiport_request=None):
        pass

class FamiPortInformationResponseBuilder(FamiPortResponseBuilder):
    def build_response(famiport_request=None):
        pass

""" Commenting out since seems not necessary at this point.
@implementer(IXmlFamiPortResponseGeneratorFactory)
class XmlFamiPortResponseGeneratorFactory(object):
    def __init__(self, *args, **kwargs):
        pass

    def __call__(self, famiport_response):
        return XmlFamiPortResponseGenerator()
"""

@implementer(IXmlFamiPortResponseGenerator)
class XmlFamiPortResponseGenerator(object):
    def __init__(self, *args, **kwargs):
        pass

    def generate_xmlResponse(cls_obj, famiport_response, encrypt_fields = [], root_name = "FMIF"):
        """Generate XML text of famiport_response with encrypt_fields encrypted.
        Assume filed name in famiport_response is same as tag name in XML.
        List fields in famiport_response are repeated with same tag name in XML.

        :param famiport_response: FamiPortResponse object to generate XMl from.
        :param encrypt_fields: List of field names to encrypt.
        :return: Shift-JIS encoded string of generated XML
        """

        root = ElementTree.Element(root_name)

        encrypt_fields = []
        if famiport_response.response_type() == FamiPortRequestType.ReservationInquiry:
            encrypt_fields.append('name')
        else:
            pass

        doc_root = cls_obj._build_xmlTree(root, famiport_response, encrypt_fields)
        elementTree = ElementTree(doc_root)

        bytesIO = BytesIO()
        # TODO Take care of problematic chars in UTF-8 to SJIS conversion
        return elementTree.write(bytesIO, encoding='Shift_JIS')

    @classmethod
    def _build_xmlTree(cls_obj, root, object, encrypt_fields = []):
        attribute_names = object.__slots__
        for attribute_name in attribute_names:
            attribute_value = getattr(object, attribute_name)
            element = ElementTree.SubElement(root, attribute_name)
            if not isinstance(attribute_value, (list, tuple)):
                element.text = attribute_value if attribute_name not in encrypt_fields else FamiPortCrypt.encrypt(attribute_value)
                return root
            else:
                cls_obj._build_xmlTree(element, attribute_value)
