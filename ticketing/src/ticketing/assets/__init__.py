from ..pyramid_boto.interfaces import IS3ConnectionFactory
from .s3 import S3AssetResolver, IS3RetrieverFactory, newDefaultS3RetrieverFactory
from .file import FileSchemeAssetResolver
from .interfaces import IAssetResolver
from zope.interface import directlyProvides

def register_default_implementations(config):
    factory = config.registry.queryUtility(IS3ConnectionFactory)
    if factory is not None:
        resolver = S3AssetResolver(
            connection=factory(),
            retriever_factory=newDefaultS3RetrieverFactory(config)
            )
    else:
        from pyramid.path import AssetResolver
        resolver = AssetResolver()
        directlyProvides(resolver, IAssetResolver)

    resolver = FileSchemeAssetResolver(resolver) 
    config.registry.registerUtility(resolver, IAssetResolver)
