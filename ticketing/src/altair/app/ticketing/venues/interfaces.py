from zope.interface import Interface, Attribute

class ITentativeVenueSite(Interface):
    _frontend_metadata_url = Attribute('''tentative attribute''') 
    _backend_metadata_url = Attribute('''tentative attribute''') 

class IVenueSiteDrawingProvider(Interface):
    def get_frontend_pages():
        pass

    def get_frontend_drawing(name):
        pass

    def get_frontend_drawings():
        pass

    def get_backend_pages():
        pass

    def get_backend_drawing(name):
        pass

    def get_backend_drawings():
        pass

    drawing_url = Attribute('''deprecated; switch to get_backend_drawings''')

    direct_drawing_url = Attribute('''deprecated; switch to get_backend_drawings''')

class IVenueSiteDrawingProviderAdapterFactory(Interface):
    def __call__(request):
        pass

class IVenueSiteDrawingHandler(Interface):
    def __call__(context, request):
        pass

class IVenueSiteDrawingHandlerFactory(Interface):
    def __call__(config):
        pass
