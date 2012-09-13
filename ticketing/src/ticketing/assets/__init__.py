from ..pyramid_boto.interfaces import IS3ConnectionFactory
from .s3 import S3AssetResolver, IS3RetrieverFactory, newDefaultS3RetrieverFactory
from .interfaces import IAssetResolver

def register_default_implementations(config):
    config.registry.registerUtility(
        S3AssetResolver(
            connection=config.registry.queryUtility(IS3ConnectionFactory)(),
            retriever_factory=newDefaultS3RetrieverFactory(config)
            ),
        IAssetResolver
        )
