from zope.interface import Interface
from zope.interface import Attribute

class IStaticPageDataFetcher(Interface):
    request = Attribute("request")
    static_page = Attribute("static_page")
    utility = Attribute("utility")

    def fetch(url, path):
        pass

class IStaticPageCache(Interface):
    cache = Attribute("beacker.cache.Cache")
