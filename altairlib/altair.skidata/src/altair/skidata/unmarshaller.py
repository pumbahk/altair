import inspect
import logging

from lxml import etree

from altair.skidata.exceptions import SkidataUnmarshalFailed
from altair.skidata.utils import unmarshal_skidata_xml, make_xml_element

logger = logging.getLogger(__name__)


class SkidataXmlUnmarshaller(object):

    @staticmethod
    def unmarshal(xml_source, model_or_cls):
        """
        Unmarshal an XML data to a given object.
        :param xml_source: an XML string
        :param model_or_cls: a class or a class object with function(s)
               wrapped by SkidataXmlElement or SkidataXmlAttribute
        :return a given object to which an XML data is unmarshaled
        :exceptions
            - TypeError: raised if model_or_cls is a class type but doesn't have __init__ function
            - SkidataUnmarshalFailed: raised if failed to unmarshal an XML data
        """
        if inspect.isclass(model_or_cls):
            init_func = getattr(model_or_cls, '__init__', None)
            if not inspect.ismethod(init_func):
                raise TypeError(u'model_or_cls ({}) is not a class type with __init__ function'
                                .format(model_or_cls))

            init_args = (None,) * (len(inspect.getargspec(init_func).args) - 1)
            model = model_or_cls(*init_args)
        else:
            model = model_or_cls

        try:
            xml = etree.fromstring(xml_source)

            # model name is same as the root Element name
            xml_from_model = make_xml_element(model)
            if etree.QName(xml).localname != etree.QName(xml_from_model).localname:
                return model

            unmarshal_skidata_xml(xml, model)
            return model
        except Exception as e:
            raise SkidataUnmarshalFailed(u'Failed to unmarshal an XML data to {}, reason: {}'.format(model, e))
