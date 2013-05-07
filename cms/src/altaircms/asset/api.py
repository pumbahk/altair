from ..tag.api import get_tagmanager

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

from .creation import get_asset_filesession

def get_asset_model_abspath(request, asset):
    filesession = get_asset_filesession(request)
    return filesession.abspath(asset.filename_with_version())

def get_asset_model_abspath_thumbnail(request, asset):
    filesession = get_asset_filesession(request)
    if asset.thumbnail_path is None:
        return None
    return filesession.abspath(asset.filename_with_version(asset.thumbnail_path))
