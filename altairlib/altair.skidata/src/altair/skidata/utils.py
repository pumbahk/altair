import inspect

from lxml import etree

ALLOWED_ITERABLE_TYPES = (list, tuple, set)  # python types to handle multiple XML elements in the same node


def is_skidata_xml_context(member):
    """A member is a function wrapped by a SkidataXmlContext object"""
    from altair.skidata.decorators import SKIDATA_XML_CONTEXT_FUNC
    return hasattr(member, '__call__') and member.__name__ == SKIDATA_XML_CONTEXT_FUNC


def get_skidata_contexts(model):
    """
    Return a list of functions wrapped by SkidataXmlContext object
    in order designated by SkidataXmlElementOrder
    """
    element_order = getattr(model, '__skidata_xml_element_order__', None)
    members = element_order() if inspect.ismethod(element_order) else []
    # Append other functions
    for _, skidata_xml_context in inspect.getmembers(model, is_skidata_xml_context):
        if skidata_xml_context not in members:
            members.append(skidata_xml_context)
    return members


def make_xml_element(model):
    """
    Make an XML Element object (represented by lxml.etree.Element) from a given model
    """
    default_element = etree.Element(model.__class__.__name__)

    # __marshaller__ method exists when a given model is wrapped by SkidataXmlElement
    marshaller = getattr(model, '__marshal__', None)
    if not inspect.ismethod(marshaller):
        return default_element

    xml = marshaller()
    return xml if etree.iselement(xml) else default_element


def marshal_skidata_xml_model(model, xml, strict=False):
    """Marshal model to an XML data"""
    marshalling = '__marshalling__'  # marshalling attribute is a sign of marshalling
    setattr(model, marshalling, 'strict' if strict else 'normal')
    try:
        for skidata_xml_context in get_skidata_contexts(model):
            marshaled = skidata_xml_context()

            # Append an XML element or set an XML attribute
            if etree.iselement(marshaled):
                xml.append(marshaled)
            elif isinstance(marshaled, list):
                xml.extend(marshaled)
            elif isinstance(marshaled, dict):
                xml.set(**marshaled)
    finally:
        if hasattr(model, marshalling):
            delattr(model, marshalling)
    return xml


def unmarshal_skidata_xml(xml, model):
    """Unmarshal an XML Element object to model"""
    unmarshalling = '__unmarshalling__'  # unmarshalling attribute is a sign of unmarshalling
    setattr(model, unmarshalling, xml)
    try:
        for _, skidata_xml_context in inspect.getmembers(model, is_skidata_xml_context):
            # Set an XML attribute to model
            if xml.items():
                setattr(model, unmarshalling, xml)
                skidata_xml_context()

            # Set children in an XML element to model
            for child in xml:
                setattr(model, unmarshalling, child)
                skidata_xml_context()
    finally:
        if hasattr(model, unmarshalling):
            delattr(model, unmarshalling)
