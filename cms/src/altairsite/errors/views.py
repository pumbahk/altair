# coding: utf-8

from pyramid.view import view_config
from pyramid.exceptions import NotFound, Forbidden

@view_config(context=Forbidden, renderer='altaircms:templates/front/errors/forbidden.mako')
def forbidden(request):
    request.response.status = 401
    return {}

@view_config(context=NotFound, renderer='altaircms:templates/front/errors/notfound.mako')
def notfound(request):
    request.response.status = 404 
    return {}
