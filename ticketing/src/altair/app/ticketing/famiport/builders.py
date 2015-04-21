# -*- coding: utf-8 -*-

from zope.interface import implementer
from .interfaces import IFamiPortResponseBuilderFactory, IFamiPortResponseBuilder, IXmlFamiPortResponseGenerator
from .utils import FamiPortRequestType, FamiPortCrypt, prettify
from .responses import FamiPortResponse

from xml.etree.ElementTree import ElementTree, Element, SubElement
from io import BytesIO
from inspect import ismethod

import logging
import hashlib

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
    def __init__(self, famiport_response):
        # TODO Make sure this process is good
        encrypt_key_item = famiport_response.encrypt_key
        digest = hashlib.md5(encrypt_key_item).digest()
        self.famiport_crypt = FamiPortCrypt(digest)

    def generate_xmlResponse(cls_obj, famiport_response, root_name = "FMIF"):
        """Generate XML text of famiport_response with encrypt_fields encrypted.
        Assume filed name in famiport_response is same as tag name in XML.
        List fields in famiport_response are repeated with same tag name in XML.

        :param famiport_response: FamiPortResponse object to generate XMl from.
        :param encrypt_fields: List of field names to encrypt.
        :return: Shift-JIS encoded string of generated XML
        """

        root = Element(root_name)
        doc_root = cls_obj._build_xmlTree(root, famiport_response)
        elementTree = ElementTree(doc_root)
        bytesIO = BytesIO()
        # TODO Take care of problematic chars in UTF-8 to SJIS conversion
        elementTree.write(bytesIO, encoding='Shift_JIS', xml_declaration=True)
        xml_response = bytesIO.getvalue()
        bytesIO.close()
        return xml_response

    def _build_xmlTree(self, root, object):
        """
        Build XML tree from object.
        :param root: root of XML tree
        :param object: object to build XML tree from
        :return: root of the XML tree built
        """

        if object is None:
            return root

        # List of attribute names of the object
        attribute_names = [attribute for attribute in dir(object) if not ismethod(attribute) and not attribute.startswith("_") and attribute not in ['response_type', 'encrypt_fields', 'encrypt_key']]
        # Create an element for each attribute_name with element.text=attribute_value and put under root.
        for attribute_name in attribute_names:
            attribute_value = getattr(object, attribute_name)
            if attribute_value is not None:
                element = SubElement(root, attribute_name)
                if isinstance(object, FamiPortResponse):
                    element.text = attribute_value if attribute_name not in object.encrypt_fields else self.famiport_crypt.encrypt(attribute_value)
                elif isinstance(attribute_value, (list, tuple)):
                    for attr_value in attribute_value:
                        self._build_xmlTree(element, attr_value)
                else:
                    element.text = attribute_value

        return root
