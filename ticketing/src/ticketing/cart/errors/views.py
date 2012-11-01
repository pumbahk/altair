# coding: utf-8
from markupsafe import Markup
from pyramid.view import view_config
from pyramid.exceptions import NotFound, Forbidden
from pyramid.httpexceptions import HTTPFound
from ..exceptions import *
from ..reserving import InvalidSeatSelectionException, NotEnoughAdjacencyException
from ..stocker import NotEnoughStockException
from .. import api
from ticketing.mobile import mobile_view_config
from ticketing.cart.selectable_renderer import selectable_renderer
import logging

logger = logging.getLogger(__name__)



@mobile_view_config(context=Forbidden, renderer=selectable_renderer('ticketing.cart:templates/errors_mobile/%(membership)s/forbidden.html'))
@view_config(context=Forbidden, renderer=selectable_renderer('ticketing.cart:templates/errors/%(membership)s/forbidden.html'))
def forbidden(request):
    request.response.status = 401
    return {}

@mobile_view_config(context=NotFound, renderer=selectable_renderer('ticketing.cart:templates/errors_mobile/%(membership)s/notfound.html'))
@view_config(context=NotFound, renderer=selectable_renderer('ticketing.cart:templates/errors/%(membership)s/notfound.html'))
def notfound(request):
    event_id = getattr(request.context, 'event_id', None)
    if event_id is not None:
        logger.debug("404 on event_id=%s" % event_id)
    request.response.status = 404
    api.logout(request)
    return {}

@mobile_view_config(context=NoCartError, renderer=selectable_renderer("ticketing.cart:templates/carts/%(membership)s/timeout.html"))
@view_config(context=NoCartError, renderer=selectable_renderer("ticketing.cart:templates/carts/%(membership)s/timeout.html"))
def handle_nocarterror(request):
    api.remove_cart(request)
    return {}
    # return HTTPFound('/')

@mobile_view_config(context=NoEventError, renderer=selectable_renderer('ticketing.cart:templates/errors_mobile/%(membership)s/notfound.html'))
@view_config(context=NoEventError, renderer=selectable_renderer('ticketing.cart:templates/errors/%(membership)s/notfound.html'))
def handle_noeventerror(request):
    request.response.status = 404
    api.logout(request)
    return {}

@mobile_view_config(context=NoSalesSegment, renderer=selectable_renderer('ticketing.cart:templates/errors_mobile/%(membership)s/notfound.html'))
@view_config(context=NoSalesSegment, renderer=selectable_renderer('ticketing.cart:templates/errors/%(membership)s/notfound.html'))
def handle_nosalessegmenterror(request):
    request.response.status = 404
    api.logout(request)
    return {}

@mobile_view_config(context=NoPerformanceError, renderer=selectable_renderer('ticketing.cart:templates/errors_mobile/%(membership)s/notfound.html'))
@view_config(context=NoPerformanceError, renderer=selectable_renderer('ticketing.cart:templates/errors/%(membership)s/notfound.html'))
def handle_noperformanceerror(request):
    request.response.status = 404
    api.logout(request)
    return {}

@view_config(context=InvalidCSRFTokenException, renderer=selectable_renderer('ticketing.cart:templates/errors/%(membership)s/forbidden.html'))
def csrf(request):
    request.response.status = 403
    api.logout(request)
    return {}

class OverQuantityLimitErrorView(object):
    def __init__(self, context, request):
        self.request = request
        self.context = context

    @view_config(context=OverQuantityLimitError, renderer=selectable_renderer('ticketing.cart:templates/carts_mobile/%(membership)s/error.html'), request_type="..interfaces.IMobileRequest")
    def __call__(self):
        logger.info(str(e))
        upper_limit = self.context.upper_limit
        return dict(message=u"枚数は合計%d枚以内で選択してください" % upper_limit)

@view_config(context=ZeroQuantityError, renderer=selectable_renderer('ticketing.cart:templates/carts_mobile/%(membership)s/error.html'), request_type="..interfaces.IMobileRequest")
def zero_quantity_error(request):
    return dict(message=u"枚数は1枚以上で選択してください")

@view_config(context=NotEnoughStockException, renderer=selectable_renderer('ticketing.cart:templates/carts_mobile/%(membership)s/error.html'), request_type="..interfaces.IMobileRequest")
def not_enough_stock_exception(request):
    return dict(message=u"在庫がありません。\nご希望の座席を確保できませんでした。")

@view_config(context=InvalidSeatSelectionException, renderer=selectable_renderer('ticketing.cart:templates/carts_mobile/%(membership)s/error.html'), request_type="..interfaces.IMobileRequest")
def invalid_seat_selection_exception(request):
    return dict(message=u"座席選択に誤りがあります。\n座席を再度選択してください。")

@view_config(context=NotEnoughAdjacencyException, renderer=selectable_renderer('ticketing.cart:templates/carts_mobile/%(membership)s/error.html'), request_type="..interfaces.IMobileRequest")
def not_enough_ajacency_exception(request):
    return dict(message=u"連席で座席を確保できません。個別に購入してください。")

@view_config(context=CartCreationExceptoion, renderer=selectable_renderer('ticketing.cart:templates/carts_mobile/%(membership)s/error.html'), request_type="..interfaces.IMobileRequest")
def cart_creation_exception(request):
    return dict(message=u"カートを作成できませんでした。しばらく時間を置いてから再度お試しください。")

@view_config(context=InvalidCSRFTokenException, renderer=selectable_renderer('ticketing.cart:templates/carts_mobile/%(membership)s/error.html'), request_type="..interfaces.IMobileRequest")
def cart_creation_exception(request):
    return dict(message=u"ウェブブラウザの戻るボタンは使用できません。画面上の戻るボタンから操作して下さい。")

@view_config(context=DeliveryFailedException, renderer=selectable_renderer('ticketing.cart:templates/carts/%(membership)s/message.html'))
@view_config(context=DeliveryFailedException, renderer=selectable_renderer('ticketing.cart:templates/carts_mobile/%(membership)s/error.html'), request_type="..interfaces.IMobileRequest")
def cart_creation_exception(context, request):
    event_id = context.event_id
    location = request.route_url('cart.index', event_id=event_id)
    return dict(message=Markup(u'決済中にエラーが発生しました。しばらく時間を於いてから<a href="%s">再度お試しください。</a>' % location))
