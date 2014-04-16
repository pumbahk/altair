from zope.interface import Interface

class ISessionHTTPBackendFactory(Interface):
    def __call__(request):
        pass

class ISessionPersistenceBackendFactory(Interface):
    def __call__(request):
        pass
