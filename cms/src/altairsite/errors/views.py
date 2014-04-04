# coding: utf-8
from pyramid.view import view_config
from ..separation import selectable_renderer, tstar_mobile_or_not_renderer
from altair.exclog.api import build_exception_message, log_exception_message
from ..separation import enable_smartphone

@view_config(context="pyramid.exceptions.Forbidden", 
             request_type='altairsite.tweens.ISmartphoneRequest', 
             custom_predicates=(enable_smartphone, ), 
             renderer=selectable_renderer("altairsite.smartphone:templates/%(prefix)s/errors/notfound.html"))
@view_config(context="pyramid.exceptions.Forbidden", 
             request_type='altairsite.tweens.IMobileRequest', 
             renderer=tstar_mobile_or_not_renderer({"RT": "altaircms:templates/mobile/notfound.html"}, 
                                                   default = "altaircms:templates/mobile/default_notfound.html"))
@view_config(context="pyramid.exceptions.Forbidden", 
             renderer=selectable_renderer("altaircms:templates/usersite/errors/%(prefix)s/forbidden.html"))
def forbidden(request):
    request.body_id = "error"
    request.response.status = 401
    return {}

@view_config(context="pyramid.exceptions.NotFound", 
             request_type='altairsite.tweens.ISmartphoneRequest', 
             custom_predicates=(enable_smartphone, ), 
             renderer=selectable_renderer("altairsite.smartphone:templates/%(prefix)s/errors/notfound.html"))
@view_config(context="pyramid.exceptions.NotFound", 
             request_type='altairsite.tweens.IMobileRequest', 
             renderer=tstar_mobile_or_not_renderer({"RT": "altaircms:templates/mobile/notfound.html"}, 
                                                   default = "altaircms:templates/mobile/default_notfound.html"))
@view_config(context="pyramid.exceptions.NotFound", 
             renderer=selectable_renderer("altaircms:templates/usersite/errors/%(prefix)s/notfound.html"))
@view_config(context="altaircms.page.api.StaticPageNotFound", 
             request_type='altairsite.tweens.IMobileRequest', 
             renderer=tstar_mobile_or_not_renderer({"RT": "altaircms:templates/mobile/notfound.html"}, 
                                                   default = "altaircms:templates/mobile/default_notfound.html"))
@view_config(context="altaircms.page.api.StaticPageNotFound", 
             renderer=selectable_renderer("altaircms:templates/usersite/errors/%(prefix)s/notfound.html"))
def notfound(request):
    request.body_id = "error"
    request.response.status = 404 
    return {}

@view_config(context="altairsite.exceptions.UsersiteException", 
             request_type='altairsite.tweens.ISmartphoneRequest', 
             custom_predicates=(enable_smartphone, ), 
             renderer=selectable_renderer("altairsite.smartphone:templates/%(prefix)s/errors/notfound.html"))
@view_config(context="altairsite.exceptions.UsersiteException", 
             request_type='altairsite.tweens.IMobileRequest', 
             renderer=tstar_mobile_or_not_renderer(
               {"RT": "altaircms:templates/mobile/notfound.html"}, 
               default = "altaircms:templates/mobile/default_notfound.html"))
@view_config(context="altairsite.exceptions.UsersiteException", 
             renderer=selectable_renderer("altaircms:templates/usersite/errors/%(prefix)s/notfound.html"))
def usersite_exc(context, request):
    exception_message = build_exception_message(request)
    if exception_message:
        log_exception_message(request, *exception_message)
    request.body_id = "error"
    request.response.status = 500
    request.response.text = u'test'
    return {}
