from zope.interface import Interface
from zope.interface import Attribute

class IPublishingModelSearcher(Interface):
    type = Attribute("type of tag manger")
    tag_manager = Attribute("tag manger")
    system_tag_manager = Attribute("system_tag manger")
    TargetModel = Attribute("a model class of search target.")

    def query_publishing_no_filtered(datetime, qs=None):
        pass

    def query_publishing(datetime, tag):
        pass

    def filter_by_tag(tag):
        pass

    def filter_by_genre(genre):
        pass

class IVirtualProxyFactory(Interface):
    env = Attribute("env")
    def create(*args, **kwargs):
        pass
