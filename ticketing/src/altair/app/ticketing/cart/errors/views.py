# coding: utf-8
from markupsafe import Markup
from pyramid.view import view_config
from pyramid.exceptions import NotFound
from pyramid.httpexceptions import HTTPFound
from ..exceptions import (
    NoCartError,
    NoEventError,
    NoSalesSegment,
    NoPerformanceError,
    InvalidCSRFTokenException,
    OverQuantityLimitError,
    ZeroQuantityError,
    CartCreationException,
    DeliveryFailedException,
    InvalidCartStatusError
)
from ..reserving import InvalidSeatSelectionException, NotEnoughAdjacencyException
from ..stocker import InvalidProductSelectionException, NotEnoughStockException
from .. import api
from altair.mobile import mobile_view_config
from altair.app.ticketing.cart.selectable_renderer import selectable_renderer
from altair.app.ticketing.payments.exceptions import PaymentPluginException
import logging
import transaction

logger = logging.getLogger(__name__)



@mobile_view_config(context=NotFound, renderer=selectable_renderer('altair.app.ticketing.cart:templates/%(membership)s/mobile/errors/notfound.html'))
@view_config(context=NotFound, renderer=selectable_renderer('altair.app.ticketing.cart:templates/%(membership)s/pc/errors/notfound.html'))
def notfound(request):
    event_id = getattr(request.context, 'event_id', None)
    if event_id is not None:
        logger.debug("404 on event_id=%s" % event_id)
    request.response.status = 404
    return {}

@mobile_view_config(context=NoCartError, renderer=selectable_renderer("altair.app.ticketing.cart:templates/%(membership)s/pc/timeout.html"))
@view_config(context=NoCartError, renderer=selectable_renderer("altair.app.ticketing.cart:templates/%(membership)s/pc/timeout.html"))
def handle_nocarterror(request):
    api.remove_cart(request)
    return {}
    # return HTTPFound('/')

@mobile_view_config(context=NoEventError, renderer=selectable_renderer('altair.app.ticketing.cart:templates/%(membership)s/mobile/errors/notfound.html'))
@view_config(context=NoEventError, renderer=selectable_renderer('altair.app.ticketing.cart:templates/%(membership)s/pc/errors/notfound.html'))
def handle_noeventerror(context, request):
    logger.debug(repr(context))
    request.response.status = 404
    api.logout(request)
    return {}

@mobile_view_config(context=NoSalesSegment, renderer=selectable_renderer('altair.app.ticketing.cart:templates/%(membership)s/mobile/errors/notfound.html'))
@view_config(context=NoSalesSegment, renderer=selectable_renderer('altair.app.ticketing.cart:templates/%(membership)s/pc/errors/notfound.html'))
def handle_nosalessegmenterror(request):
    request.response.status = 404
    api.logout(request)
    return {}

@mobile_view_config(context=NoPerformanceError, renderer=selectable_renderer('altair.app.ticketing.cart:templates/%(membership)s/mobile/errors/notfound.html'))
@view_config(context=NoPerformanceError, renderer=selectable_renderer('altair.app.ticketing.cart:templates/%(membership)s/pc/errors/notfound.html'))
def handle_noperformanceerror(request):
    request.response.status = 404
    api.logout(request)
    logger.debug("NoPerformance {0}".format(request.exception))
    return {}

@view_config(context=InvalidCSRFTokenException, renderer=selectable_renderer('altair.app.ticketing.cart:templates/%(membership)s/pc/errors/forbidden.html'))
def csrf(request):
    request.response.status = 403
    api.logout(request)
    return {}

class OverQuantityLimitErrorView(object):
    def __init__(self, context, request):
        self.request = request
        self.context = context

    @view_config(context=OverQuantityLimitError, renderer=selectable_renderer('altair.app.ticketing.cart:templates/%(membership)s/mobile/error.html'), request_type='altair.mobile.interfaces.IMobileRequest')
    def __call__(self):
        upper_limit = self.context.upper_limit
        return dict(message=u"枚数は合計%d枚以内で選択してください" % upper_limit)

@view_config(context=ZeroQuantityError, renderer=selectable_renderer('altair.app.ticketing.cart:templates/%(membership)s/mobile/error.html'), request_type='altair.mobile.interfaces.IMobileRequest')
def zero_quantity_error(request):
    return dict(message=u"枚数は1枚以上で選択してください")

@view_config(context=NotEnoughStockException, renderer=selectable_renderer('altair.app.ticketing.cart:templates/%(membership)s/mobile/error.html'), request_type='altair.mobile.interfaces.IMobileRequest')
def not_enough_stock_exception(request):
    return dict(message=u"在庫がありません。\nご希望の座席を確保できませんでした。")

@view_config(context=InvalidSeatSelectionException, renderer=selectable_renderer('altair.app.ticketing.cart:templates/%(membership)s/mobile/error.html'), request_type='altair.mobile.interfaces.IMobileRequest')
def invalid_seat_selection_exception(request):
    return dict(message=u"座席選択に誤りがあります。\n座席を再度選択してください。")

@view_config(context=InvalidProductSelectionException, renderer=selectable_renderer('altair.app.ticketing.cart:templates/%(membership)s/mobile/error.html'), request_type='altair.mobile.interfaces.IMobileRequest')
def invalid_product_selection_exception(request):
    return dict(message=u"席種選択に誤りがあります。\n席種を再度選択してください。")

@view_config(context=NotEnoughAdjacencyException, renderer=selectable_renderer('altair.app.ticketing.cart:templates/%(membership)s/mobile/error.html'), request_type='altair.mobile.interfaces.IMobileRequest')
def not_enough_ajacency_exception(request):
    return dict(message=u"連席で座席を確保できません。個別に購入してください。")

@view_config(context=CartCreationException, renderer=selectable_renderer('altair.app.ticketing.cart:templates/%(membership)s/mobile/error.html'), request_type='altair.mobile.interfaces.IMobileRequest')
def cart_creation_exception(request):
    return dict(message=u"カートを作成できませんでした。しばらく時間を置いてから再度お試しください。")

@view_config(context=InvalidCSRFTokenException, renderer=selectable_renderer('altair.app.ticketing.cart:templates/%(membership)s/mobile/error.html'), request_type='altair.mobile.interfaces.IMobileRequest')
def invalid_csrf_token_exception(request):
    return dict(message=u"ウェブブラウザの戻るボタンは使用できません。画面上の戻るボタンから操作して下さい。")

@view_config(context=DeliveryFailedException, renderer=selectable_renderer('altair.app.ticketing.cart:templates/%(membership)s/pc/message.html'))
@view_config(context=DeliveryFailedException, renderer=selectable_renderer('altair.app.ticketing.cart:templates/%(membership)s/mobile/error.html'), request_type='altair.mobile.interfaces.IMobileRequest')
def delivery_failed_exception(context, request):
    event_id = context.event_id
    location = request.route_url('cart.index', event_id=event_id)
    return dict(title=u'決済エラー', message=Markup(u'決済中にエラーが発生しました。しばらく時間を置いてから<a href="%s">再度お試しください。</a>' % location))

@view_config(context=PaymentPluginException, renderer=selectable_renderer('altair.app.ticketing.cart:templates/%(membership)s/pc/message.html'))
@view_config(context=PaymentPluginException, renderer=selectable_renderer('altair.app.ticketing.cart:templates/%(membership)s/mobile/error.html'), request_type='altair.mobile.interfaces.IMobileRequest')
def payment_plugin_exception(context, request):
    if context.back_url is not None:
        # カートの救済可能な場合
        api.recover_cart(request) 
        transaction.commit()
        return HTTPFound(location=context.back_url)
    else:
        # カートの救済不可能
        # if cart is not None:
        #     location = request.route_url('cart.index', event_id=cart.performance.event_id)
        # else:
        #    location = request.context.host_base_url
        location = request.context.host_base_url
    return dict(title=u'決済エラー', message=Markup(u'決済中にエラーが発生しました。しばらく時間を置いてから<a href="%s">再度お試しください。</a>' % location))

@view_config(context=InvalidCartStatusError, renderer=selectable_renderer('altair.app.ticketing.cart:templates/%(membership)s/pc/message.html'))
@view_config(context=InvalidCartStatusError, renderer=selectable_renderer('altair.app.ticketing.cart:templates/%(membership)s/mobile/error.html'), request_type='altair.mobile.interfaces.IMobileRequest')
def invalid_cart_status_error(request):
    return dict(message=Markup(u'大変申し訳ございません。ブラウザの複数ウィンドウからの操作や、戻るボタン等の操作により、予約を継続することができません。<br>'
                               u'ご予約の際は複数ウィンドウや戻るボタンを使わずにご予約ください。'))
