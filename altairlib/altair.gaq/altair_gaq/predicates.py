import re
from zope.interface import implementer
from .interfaces import ITrackingInjectorPredicateFactory, ITrackingInterceptorPredicateFactory

@implementer(ITrackingInterceptorPredicateFactory, ITrackingInjectorPredicateFactory)
class ExcludePathPredicate(object):
    def __init__(self, registry, path_regexps):
        self.path_regexps = [re.compile(path_regexp) for path_regexp in re.split(r'\s+', path_regexps)]

    def should_inject(self, request, response):
        return self(request)

    def should_intercept(self, request):
        return self(request)
       
    def __call__(self, request):
        for path_regexp in self.path_regexps:
            if path_regexp.match(request.path):
                return False
        return True

def includeme(config):
    config.registry.registerUtility(ExcludePathPredicate, ITrackingInterceptorPredicateFactory, 'exclude_path')
    config.registry.registerUtility(ExcludePathPredicate, ITrackingInjectorPredicateFactory, 'exclude_path')

