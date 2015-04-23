# -*- coding: utf-8 -*-

from zope.interface import implementer
from .interfaces import IFamiPortResponseBuilderFactory, IFamiPortResponseBuilder, IXmlFamiPortResponseGenerator
from .utils import FamiPortRequestType, FamiPortCrypt, prettify
from .responses import FamiPortResponse

# from lxml.etree import ElementTree, Element, SubElement
from lxml import etree
from io import BytesIO
from inspect import ismethod

import logging
import hashlib
import base64

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
        encrypt_key_item = famiport_response.encrypt_key
        if encrypt_key_item:
            hash = hashlib.md5()
            hash.update(encrypt_key_item)
            str_digest = hash.hexdigest()
            key = bytes(str_digest)
            self.famiport_crypt = FamiPortCrypt(base64.urlsafe_b64encode(str_digest))

    def generate_xmlResponse(self, famiport_response, root_name = "FMIF"):
        """Generate XML text of famiport_response with encrypt_fields encrypted.
        Assume filed name in famiport_response is same as tag name in XML.
        List fields in famiport_response are repeated with same tag name in XML.

        :param famiport_response: FamiPortResponse object to generate XMl from.
        :param encrypt_fields: List of field names to encrypt.
        :return: Shift-JIS encoded string of generated XML
        """

        root = etree.Element(root_name)
        doc_root = self._build_xmlTree(root, famiport_response)
        return etree.tostring(doc_root, encoding='shift_jis', xml_declaration=True, pretty_print=True)
        # elementTree = ElementTree(doc_root)
        # bytesIO = BytesIO()
        # elementTree.write(bytesIO, encoding='Shift_JIS', xml_declaration=True, pretty_print=True)
        # xml_response = bytesIO.getvalue()
        # bytesIO.close()
        # return xml_response

    def _build_xmlTree(self, root, object):
        """
        Build XML tree from object.
        :param root: root of XML tree
        :param object: object to build XML tree from
        :return: root of the XML tree built
        """

        if object is None:
            return root

        attribute_names = object.__slots__ # Get attribute names of the object
        # Create an element for each attribute_name with element.text=attribute_value and put under root.
        for attribute_name in attribute_names:
            attribute_value = getattr(object, attribute_name)
            if attribute_value is not None:
                if isinstance(attribute_value, (list, tuple)): # In case of list or tuple attribute such as FamiPortPaymentTicketingResponse.ticket
                    for value in attribute_value:
                        element = etree.SubElement(root, attribute_name)
                        attr_names = [attribute for attribute in dir(value) if not ismethod(attribute) and not attribute.startswith("_")]
                        for attr_name in attr_names:
                            sub_element = etree.SubElement(element, attr_name)
                            attr_value = getattr(value, attr_name)
                            if attr_value is not None:
                                # TODO Take care of problematic chars in UTF-8 to SJIS conversion
                                sub_element.text = attr_value if attr_name not in object.encrypt_fields else self.famiport_crypt.encrypt(attr_value.encode('shift_jis'))
                                """
                                if isinstance(attr_value, unicode):
                                    sjis_attr_value = attr_value.encode('shift_jis')
                                    print "sjis_attr_value: ", sjis_attr_value
                                    sub_element.text = sjis_attr_value
                                else:
                                    sub_element.text = attr_value
                                """
                else:
                    element = etree.SubElement(root, attribute_name)
                    # TODO Take care of problematic chars in UTF-8 to SJIS conversion
                    # if isinstance(attribute_value, unicode):
                    #    attribute_value = attribute_value.encode('shift_jis') # Encode for encrypt
                    # print '(attribute_name, attribute_value)', (attribute_name, attribute_value)
                    # element.text = attribute_value.decode('shift_jis') if attribute_name not in object.encrypt_fields else self.famiport_crypt.encrypt(attribute_value)
                    element.text = attribute_value if attribute_name not in object.encrypt_fields else self.famiport_crypt.encrypt(attribute_value.encode('shift_jis'))
                    """
                    if isinstance(attribute_value, unicode):
                        sjis_attribute_value = attribute_value.encode('shift-jis')
                        element.text = sjis_attribute_value if attribute_name not in object.encrypt_fields else self.famiport_crypt.encrypt(sjis_attribute_value)
                    else:
                        element.text = attribute_value if attribute_name not in object.encrypt_fields else self.famiport_crypt.encrypt(attribute_value)
                    """

        return root
