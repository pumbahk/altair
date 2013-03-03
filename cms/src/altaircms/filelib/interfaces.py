from zope.interface import Interface
from zope.interface import Attribute

class IUploadFile(Interface):
    name = Attribute("name")
    signature = Attribute("signature")
    handler = Attribute("handler")

class IFileSession(Interface):
    def add(uploadfile):
        pass
