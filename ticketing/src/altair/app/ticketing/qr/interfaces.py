from zope.interface import Interface, Attribute

class IQRDataBuilder(Interface):
    key = Attribute("seed")
