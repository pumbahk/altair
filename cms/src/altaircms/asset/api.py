from ..tag.api import get_tagmanager
from ..modelmanager.interfaces import IVirtualProxyFactory
from . import PROXY_FACTORY_NAME

ENDPOINT = "_asset_endpoint"
TAGLABEL = "_asset_taglabel"

def set_endpoint(request, endpoint=None):
    endpoint = endpoint or request.refferer ## refferer?
    request.session[ENDPOINT] = endpoint
def get_endpoint(request):
    return request.session.get(ENDPOINT, "/")

def set_taglabel(request, taglabel):
    request.session[TAGLABEL] = taglabel
def get_taglabel(request):
    return request.session.get(TAGLABEL)

def after_create_add_tag(request, asset):
    taglabel = get_taglabel(request)
    manager = get_tagmanager("asset", request)
    manager.add_tags(asset, [taglabel], False)

def get_virtual_asset_factory(request):
    return request.registry.queryUtility(IVirtualProxyFactory, name=PROXY_FACTORY_NAME)
