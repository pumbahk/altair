from zope.interface import Interface
from zope.interface import Attribute

class IHasWidgetPageFinder(Interface):
    def __call__(request):
        pass
    widget = Attribute("model of widget")

def add_has_widget_pages_finder(config, finder, name=""):
    finder = config.maybe_dotted(finder)
    config.registry.registerUtility(finder, IHasWidgetPageFinder, name=name)

def get_has_widget_pages_finder(request, name=""):
    return request.registry.getUtility(IHasWidgetPageFinder, name=name)


## parse config
if __name__ == "__main__":
    import doctest
    doctest.testmod()
