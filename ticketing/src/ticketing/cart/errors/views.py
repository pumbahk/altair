# coding: utf-8

from pyramid.view import view_config
from pyramid.exceptions import NotFound, Forbidden
from pyramid.httpexceptions import HTTPFound
from ..exceptions import *
from ..reserving import InvalidSeatSelectionException, NotEnoughAdjacencyException
from ..stocker import NotEnoughStockException
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

@view_config(context=NoCartError, renderer="ticketing.cart:templates/carts/timeout.html")
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

@view_config(context=NotEnoughStockException, renderer='ticketing.cart:templates/carts_mobile/error.html', request_type="..interfaces.IMobileRequest")
def not_enough_stock_exception(request):
    return dict(message=u"在庫がありません。\nご希望の座席を確保できませんでした。")

@view_config(context=InvalidSeatSelectionException, renderer='ticketing.cart:templates/carts_mobile/error.html', request_type="..interfaces.IMobileRequest")
def invalid_seat_selection_exception(request):
    return dict(message=u"座席選択に誤りがあります。\n座席を再度選択してください。")

@view_config(context=NotEnoughAdjacencyException, renderer='ticketing.cart:templates/carts_mobile/error.html', request_type="..interfaces.IMobileRequest")
def not_enough_ajacency_exception(request):
    return dict(message=u"連席で座席を確保できません。個別に購入してください。")

@view_config(context=CartCreationExceptoion, renderer='ticketing.cart:templates/carts_mobile/error.html', request_type="..interfaces.IMobileRequest")
def cart_creation_exception(request):
    return dict(message=u"カートを作成できませんでした。しばらく時間を置いてから再度お試しください。")

@view_config(context=InvalidCSRFTokenException, renderer='ticketing.cart:templates/carts_mobile/error.html', request_type="..interfaces.IMobileRequest")
def cart_creation_exception(request):
    return dict(message=u"ウェブブラウザの戻るボタンは使用できません。画面上の戻るボタンから操作して下さい。")
