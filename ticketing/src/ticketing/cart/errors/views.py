# coding: utf-8

from pyramid.view import view_config
from pyramid.exceptions import NotFound, Forbidden
from pyramid.httpexceptions import HTTPFound
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

@view_config(context=NoCartError, renderer="ticketing.cart:templates/errors/timeout.html")
def handle_nocarterror(request):
    logger.error(request.context, exc_info=request.exc_info)
    return {}
    # return HTTPFound('/')

@view_config(context=NoEventError, renderer='ticketing.cart:templates/errors/notfound.html')
def handle_noeventerror(request):
    logger.error(request.context, exc_info=request.exc_info)
    request.response.status = 404
    return {}

@view_config(context=InvalidCSRFTokenException, renderer='ticketing.cart:templates/errors/forbidden.html')
def csrf(request):
    logger.error(request.context, exc_info=request.exc_info)
    request.response.status = 403
    return {}

class OverQuantityLimitErrorView(object):
    def __init__(self, context, request):
        self.request = request
        self.context = context

    @view_config(context=OverQuantityLimitError, renderer='ticketing.cart:templates/carts_mobile/error.html', request_type="..interfaces.IMobileRequest")
    def __call__(self):
        logger.error(self.context, exc_info=self.request.exc_info)
        upper_limit = self.context.upper_limit
        return dict(message=u"枚数は合計%d枚以内で選択してください" % upper_limit)

@view_config(context=ZeroQuantityError, renderer='ticketing.cart:templates/carts_mobile/error.html', request_type="..interfaces.IMobileRequest")
def zero_quantity_error(request):
    return dict(message=u"枚数は1枚以上で選択してください")
