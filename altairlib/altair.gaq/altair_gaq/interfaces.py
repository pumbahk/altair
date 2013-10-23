from zope.interface import Interface

class ITrackingCodeInjector(Interface):
    def __call__(request, response):
        pass

class ITrackingCodeInjectorFactory(Interface):
    def __call__(type_, **kwargs):
        pass

class ITrackingInterceptorFactory(Interface):
    def __call__(handler, type_, **kwargs):
        pass

class ITrackingInterceptor(Interface):
    def __call__(request):
        pass

class ITrackingInterceptorPredicateFactory(Interface):
    def __call__(registry, **kwargs):
        pass

class ITrackingInjectorPredicateFactory(Interface):
    def __call__(registry, **kwargs):
        pass

class ITrackingInterceptorPredicate(Interface):
    def should_intercept(request):
        pass

class ITrackingInjectorPredicate(Interface):
    def should_inject(request, response):
        pass
