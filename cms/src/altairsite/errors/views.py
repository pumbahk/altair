# coding: utf-8
from pyramid.view import view_config
from ..separation import selectable_renderer, tstar_mobile_or_not_renderer


@view_config(context="pyramid.exceptions.Forbidden", 
             request_type='altairsite.mobile.tweens.IMobileRequest', 
             renderer=tstar_mobile_or_not_renderer({"ticketstar": "altaircms:templates/mobile/notfound.html"}, 
                                                   default = "altaircms:templates/mobile/default_notfound.html"))
@view_config(context="pyramid.exceptions.Forbidden", 
             renderer=selectable_renderer("altaircms:templates/front/errors/%(prefix)s/forbidden.html"))
def forbidden(request):
    request.response.status = 401
    return {}

@view_config(context="pyramid.exceptions.NotFound", 
             request_type='altairsite.mobile.tweens.IMobileRequest', 
             renderer=tstar_mobile_or_not_renderer({"ticketstar": "altaircms:templates/mobile/notfound.html"}, 
                                                   default = "altaircms:templates/mobile/default_notfound.html"))
@view_config(context="pyramid.exceptions.NotFound", 
             renderer=selectable_renderer("altaircms:templates/front/errors/%(prefix)s/notfound.html"))
def notfound(request):
    request.response.status = 404 
    return {}
