from zope.interface import Interface
from zope.interface import Attribute

class IAfterFormInitialize(Interface):
    request = Attribute("request")
    form = Attribute("form")
    rendering_val = Attribute("rendering_val")
    
