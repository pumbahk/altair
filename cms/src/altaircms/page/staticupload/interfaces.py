from zope.interface import Interface
from zope.interface import Attribute

class IStaticPageDataFetcher(Interface):
    request = Attribute("request")
    static_page = Attribute("static_page")
    utility = Attribute("utility")

    def fetch(url, path):
        pass

class IStaticPageDataFetcherFactory(Interface):
    def __call__(request, static_page, utility):
        pass
