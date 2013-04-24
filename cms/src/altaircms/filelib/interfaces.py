from zope.interface import Interface
from zope.interface import Attribute

__all__ = ["IS3UtilityFactory",
           "IUploadFile", 
           "IFileSession"]

class IUploadFile(Interface):
    name = Attribute("name")
    signature = Attribute("signature")
    handler = Attribute("handler")

class IFileSession(Interface):
    def add(uploadfile):
        pass
    def delete(deletefile):
        pass
    def commit():
        pass

class IS3UtilityFactory(Interface):
    def from_setting(settings):
        pass

    def __call__():
        pass
