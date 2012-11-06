# coding: utf-8
from pyramid.view import view_config
from ..separation import selectable_renderer

@view_config(context="pyramid.exceptions.Forbidden", 
             renderer=selectable_renderer("altaircms:templates/front/errors/%(prefix)s/forbidden.mako"),
             decorator="altaircms.lib.fanstatic_decorator.with_bootstrap")
def forbidden(request):
    request.response.status = 401
    return {}

@view_config(context="pyramid.exceptions.NotFound", 
             renderer=selectable_renderer("altaircms:templates/front/errors/%(prefix)s/notfound.mako"),
             decorator="altaircms.lib.fanstatic_decorator.with_bootstrap")
def notfound(request):
    request.response.status = 404 
    return {}
