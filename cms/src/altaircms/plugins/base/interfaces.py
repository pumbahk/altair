from zope.interface import Interface
from zope.interface import Attribute

class IWidgetAggregatorFactory(Interface):
    pass

class IWidgetAggregator(Interface):
    request = Attribute("request")
    widgets = Attribute("list of candidate widget")

    def get_widgets():
        pass

    def get_jscode():
        pass

    def get_csscode():
        pass

class IWidgetRenderer(Interface):
    ## adapter
    request = Attribute("request")
    widget = Attribute("widget model")

    def rendering_function(*args, **kwargs):
        pass
