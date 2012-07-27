from zope.interface import Interface, Attribute

class ICommunicationApi(Interface):
    baseurl = Attribute("base url of external resource")
    def create_connection(request, *args, **kwargs):
        """ create validated connection(usually, urllib2.Request object)"""
        pass
