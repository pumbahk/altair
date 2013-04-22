from .file import FileSchemeAssetResolver
from .interfaces import IAssetResolver
from zope.interface import directlyProvides

def register_default_implementations(config):
    from pyramid.path import AssetResolver
    resolver = AssetResolver()
    directlyProvides(resolver, IAssetResolver)

    resolver = FileSchemeAssetResolver(resolver) 
    config.registry.registerUtility(resolver, IAssetResolver)
