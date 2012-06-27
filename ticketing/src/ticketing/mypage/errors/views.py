# coding: utf-8

from pyramid.view import view_config
from pyramid.exceptions import NotFound, Forbidden

@view_config(context=Forbidden, renderer='errors/forbidden.html')
def forbidden(request):
    request.response.status = 401
    return {}

@view_config(context=NotFound, renderer='errors/notfound.html')
def notfound(request):
    request.response.status = 404
    return {}
