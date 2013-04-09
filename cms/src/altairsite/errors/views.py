# coding: utf-8
from pyramid.view import view_config
from ..separation import selectable_renderer, tstar_mobile_or_not_renderer
from altair.exclog.interfaces import IExceptionLogger, IExceptionMessageBuilder


@view_config(context="pyramid.exceptions.Forbidden", 
             request_type='altairsite.mobile.tweens.IMobileRequest', 
             renderer=tstar_mobile_or_not_renderer({"ticketstar": "altaircms:templates/mobile/notfound.html"}, 
                                                   default = "altaircms:templates/mobile/default_notfound.html"))
@view_config(context="pyramid.exceptions.Forbidden", 
             renderer=selectable_renderer("altaircms:templates/usersite/errors/%(prefix)s/forbidden.html"))
def forbidden(request):
    request.body_id = "error"
    request.response.status = 401
    return {}

@view_config(context="pyramid.exceptions.NotFound", 
             request_type='altairsite.mobile.tweens.IMobileRequest', 
             renderer=tstar_mobile_or_not_renderer({"ticketstar": "altaircms:templates/mobile/notfound.html"}, 
                                                   default = "altaircms:templates/mobile/default_notfound.html"))
@view_config(context="pyramid.exceptions.NotFound", 
             renderer=selectable_renderer("altaircms:templates/usersite/errors/%(prefix)s/notfound.html"))
@view_config(context="altaircms.page.api.StaticPageNotFound", 
             request_type='altairsite.mobile.tweens.IMobileRequest', 
             renderer=tstar_mobile_or_not_renderer({"ticketstar": "altaircms:templates/mobile/notfound.html"}, 
                                                   default = "altaircms:templates/mobile/default_notfound.html"))
@view_config(context="altaircms.page.api.StaticPageNotFound", 
             renderer=selectable_renderer("altaircms:templates/usersite/errors/%(prefix)s/notfound.html"))
def notfound(request):
    request.body_id = "error"
    request.response.status = 404 
    return {}

@view_config(context="altairsite.exceptions.UsersiteException", 
             request_type='altairsite.mobile.tweens.IMobileRequest', 
             renderer=tstar_mobile_or_not_renderer(
               {"ticketstar": "altaircms:templates/mobile/notfound.html"}, 
               default = "altaircms:templates/mobile/default_notfound.html"))
@view_config(context="altairsite.exceptions.UsersiteException", 
             renderer=selectable_renderer("altaircms:templates/usersite/errors/%(prefix)s/notfound.html"))
def usersite_exc(context, request):
    message_builder = request.registry.queryUtility(IExceptionMessageBuilder)
    if message_builder is not None:
        exc_info, message = message_builder(request)
        exc_logger = request.registry.queryUtility(IExceptionLogger)
        if exc_logger:
            exc_logger(exc_info, message)
    request.body_id = "error"
    request.response.status = 500
    request.response.text = u'test'
    return {}
