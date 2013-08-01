from . import AFTER_REDIRECT_URL
from .interfaces import IPreviewSecret

def set_after_invalidate_url(request, url):
    request.session[AFTER_REDIRECT_URL] = url

def get_preview_secret(request):
    return request.registry.queryUtility(IPreviewSecret)


_force_request_type = "altair.preview.force.request_type"
class FORCE_REQUEST_TYPE:
    mobile = "mb"
    smartphone = "sp"

def set_force_request_type(request, req_type):
    if not req_type in (FORCE_REQUEST_TYPE.mobile, FORCE_REQUEST_TYPE.smartphone):
        raise ValueError(req_type)
    request.session[_force_request_type] = req_type

def get_force_request_type(request):
    return request.session.get(_force_request_type)

def pop_force_request_type(request):
    if _force_request_type in request.session:
        request.session.pop(_force_request_type)


##
from collections import namedtuple
RenderedTarget = namedtuple("RenderedTarget", "category target")

_k = "_rendered_target"
def set_rendered_target(request, category, target):
    if target:
        setattr(request, _k, RenderedTarget(category=category, target=target))

def get_rendered_target(request):
    return getattr(request, _k, None)
