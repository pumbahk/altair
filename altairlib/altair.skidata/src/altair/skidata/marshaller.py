import logging

from lxml import etree

from altair.skidata.exceptions import SkidataMarshalFailed
from altair.skidata.utils import marshal_skidata_xml_model, make_xml_element

logger = logging.getLogger(__name__)


class SkidataXmlMarshaller(object):

    @staticmethod
    def marshal(model, encoding='utf-8', xml_declaration=False, pretty_print=False, strict=False):
        """
        Marshal a class object to an XML string.
        :param model: a class object with function(s)
               wrapped by SkidataXmlElement or SkidataXmlAttribute
        :param encoding: XML encoding name
        :param xml_declaration: boolean to enable an XML declaration by default
        :param pretty_print: boolean to enable formatted XML
        :param strict: boolean to marshal with `strict` mode which cuts off XML-Data value at the maximum length.
        :return: an XML string
        :exceptions
            - TypeError: raised if model is None or doesn't have __class__ attribute
            - SkidataMarshalFailed: raised if failed to marshal a class object
        """
        if model is None or not hasattr(model, '__class__'):
            raise TypeError(u'model ({}) is not a class object'.format(model))

        xml = make_xml_element(model)
        try:
            element = marshal_skidata_xml_model(model, xml, strict=strict)
            return etree.tostring(element, encoding=encoding,
                                  xml_declaration=xml_declaration, pretty_print=pretty_print)
        except Exception as e:
            raise SkidataMarshalFailed(u'Failed to marshal {}. reason: {}'.format(model, e))
