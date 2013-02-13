from zope.interface import Interface
from zope.interface import Attribute

class ITopicSearcher(Interface):
    type = Attribute("tag manger")
    tag_manager = Attribute("tag manger")
    def query_publishing(datetime, qs=None):
        pass

    def filter_by_tag(tag):
        pass

    def filter_by_genre(genre):
        pass
