from zope.interface import Interface

class IExceptionMessageBuilder(Interface):
    def __call__(request):
        pass

class IExceptionMessageBuilderFactory(Interface):
    def __call__(registry):
        pass

class IExceptionLogger(Interface):
    def __call__(exc_info, message):
        pass

class IExceptionLoggerFactory(Interface):
    def __call__(registry):
        pass

class IExceptionMessageRenderer(Interface):
    def __call__(request, exc_info, message):
        pass

class IExceptionMessageRendererFactory(Interface):
    def __call__(registry):
        pass
