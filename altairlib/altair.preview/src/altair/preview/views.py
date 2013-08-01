from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from altair.now import set_now
from . import AFTER_REDIRECT_URL
from .api import pop_force_request_type

@view_config(route_name="__altair.preview.invalidate")
def preview_invalidate_view(context, request):
    set_now(request, None)
    pop_force_request_type(request)
    request.session["redirect_to"] = request.referrer
    return HTTPFound(request.session.get(AFTER_REDIRECT_URL) or "/")
