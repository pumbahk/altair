# coding: utf-8

from pyramid.view import view_config
from pyramid.exceptions import NotFound, Forbidden, HTTPFound
from ..exceptions import *
import logging

logger = logging.getLogger(__name__)

@view_config(context=Forbidden, renderer='ticketing.cart:templates/errors/forbidden.html')
def forbidden(request):
    request.response.status = 401
    return {}

@view_config(context=NotFound, renderer='ticketing.cart:templates/errors/notfound.html')
def notfound(request):
    request.response.status = 404
    return {}

@view_config(context=NoCartError)
def handle_nocarterror(request):
    logger.error(request.context, exc_info=request.exc_info)
    return HTTPFound('/')

@view_config(context=NoEventError, renderer='ticketing.cart:templates/errors/notfound.html')
def handle_noeventerror(request):
    logger.error(request.context, exc_info=request.exc_info)
    request.response.status = 404
    return {}

