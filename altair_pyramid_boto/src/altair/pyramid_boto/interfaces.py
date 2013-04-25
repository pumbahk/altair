from zope.interface import Interface
from zope.interface import Attribute

class IS3ConnectionFactory(Interface):
    def __call__():
        pass

class IS3ContentsUploader(Interface):
    connection = Attribute("connection")
    def upload(content, name):
        pass

    def delete(content, name):
        pass

