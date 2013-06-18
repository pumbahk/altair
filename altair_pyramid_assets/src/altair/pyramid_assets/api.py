from .interfaces import IAssetResolver

def get_asset_resolver(request):
    return request.registry.queryUtility(IAssetResolver)

