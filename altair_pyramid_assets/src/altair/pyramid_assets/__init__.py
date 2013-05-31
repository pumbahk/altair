from .file import FileSchemeAssetResolver
from .interfaces import IAssetResolver
from zope.interface import implementer, directlyProvides
from pyramid.threadlocal import get_current_registry
from pyramid.settings import aslist

@implementer(IAssetResolver)
class AssetResolverChain(object):
    def __init__(self, resolvers, registry=None):
        self.resolvers = list(resolvers)
        self.registry = registry

    def add_resolver(self, name):
        self.resolvers.append(name)

    def resolve(self, spec):
        if self.registry is None:
            registry = get_current_registry()
        else:
            registry = self.registry

        for name in self.resolvers:
            try:
                resolver = registry.getUtility(IAssetResolver, name)
                return resolver.resolve(spec)
            except ValueError:
                pass

def get_resolver(request_or_registry):
    registry = getattr(request_or_registry, 'registry', None)
    if registry is None:
        registry = request_or_registry
    return registry.queryUtility(IAssetResolver) 

def includeme(config):
    from pyramid.path import AssetResolver
    resolver = AssetResolver()
    directlyProvides(resolver, IAssetResolver)
    config.registry.registerUtility(resolver, IAssetResolver, '__default__')

    resolver = FileSchemeAssetResolver() 
    config.registry.registerUtility(resolver, IAssetResolver, 'file')

    resolvers = aslist(config.registry.settings.get('altair.pyramid_assets.resolvers', 'file __default__'))
    chain = AssetResolverChain(resolvers)
    config.registry.registerUtility(chain, IAssetResolver)
