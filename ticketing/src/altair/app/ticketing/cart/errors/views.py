# coding: utf-8
import logging
import transaction
import venusian
from markupsafe import Markup
from pyramid.view import view_defaults
from pyramid.exceptions import NotFound
from pyramid.httpexceptions import HTTPFound
from altair.pyramid_dynamic_renderer import lbr_view_config

from altair.app.ticketing.payments.exceptions import PaymentDeliveryMethodPairNotFound, PaymentCartNotAvailable
from altair.app.ticketing.core.api import get_default_contact_url

from ..exceptions import (
    NoCartError,
    NoEventError,
    NoSalesSegment,
    NoPerformanceError,
    InvalidCSRFTokenException,
    QuantityOutOfBoundsError,
    ProductQuantityOutOfBoundsError,
    PerStockTypeQuantityOutOfBoundsError,
    PerStockTypeProductQuantityOutOfBoundsError,
    PerProductProductQuantityOutOfBoundsError,
    CartCreationException,
    InvalidCartStatusError,
    OverOrderLimitException,
    OverQuantityLimitException,
    PaymentMethodEmptyError,
    TooManyCartsCreated,
    PaymentError,
    CompletionPageNotRenderered,
)
from ..reserving import InvalidSeatSelectionException, NotEnoughAdjacencyException
from ..stocker import InvalidProductSelectionException, NotEnoughStockException
from .. import api
from ..rendering import selectable_renderer

logger = logging.getLogger(__name__)


@lbr_view_config(context=NotFound, renderer=selectable_renderer('errors/notfound.html'))
def notfound(request):
    event = getattr(request.context, 'event', None)
    if event is not None:
        logger.debug("404 on event_id=%s" % event.id)
    api.logout(request, request.response)
    request.response.status = 404
    return {}

@lbr_view_config(context=PaymentDeliveryMethodPairNotFound, renderer=selectable_renderer("errors/timeout.html"))
def handle_payment_delivery_method_pair_not_found(request):
    cart = api.get_cart(request)
    return HTTPFound(request.route_path('cart.payment', sales_segment_id=cart.sales_segment_id))


@lbr_view_config(context=PaymentCartNotAvailable, renderer=selectable_renderer("errors/timeout.html"))
def handle_payment_cart_not_found(request):
    return {}


@lbr_view_config(context=NoCartError, renderer=selectable_renderer("errors/timeout.html"))
def handle_nocarterror(request):
    api.disassociate_cart_from_session(request)
    return {}
    # return HTTPFound('/')

@lbr_view_config(context=NoEventError, renderer=selectable_renderer('errors/notfound.html'))
def handle_noeventerror(context, request):
    logger.debug(repr(context))
    request.response.status = 404
    api.logout(request)
    return {}

@lbr_view_config(context=NoSalesSegment, renderer=selectable_renderer('errors/notfound.html'))
def handle_nosalessegmenterror(request):
    request.response.status = 404
    api.logout(request)
    return {}

@lbr_view_config(context=NoPerformanceError, renderer=selectable_renderer('errors/notfound.html'))
def handle_noperformanceerror(request):
    request.response.status = 404
    api.logout(request)
    logger.debug("NoPerformance {0}".format(request.exception))
    return {}

@lbr_view_config(context=InvalidCSRFTokenException, renderer=selectable_renderer('errors/forbidden.html'))
def csrf(request):
    request.response.status = 403
    api.logout(request)
    return {}

@lbr_view_config(context=CompletionPageNotRenderered, renderer=selectable_renderer('errors/completion.html'))
def completion_page_not_rendered(request):
    request.response.status = 404
    api.get_temporary_store(request).clear(request)
    return {
        'default_contact_url': get_default_contact_url(
            request,
            api.get_organization(request),
            request.mobile_ua.carrier
            )
        }

@view_defaults(renderer=selectable_renderer('message.html'))
class CommonErrorView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @lbr_view_config(context=PaymentMethodEmptyError)
    def payment_method_is_empty(self):
        return dict(message=Markup(u'この商品は現在メンテナンス中のためご購入いただけません。'))

    @lbr_view_config(context=TooManyCartsCreated)
    def too_many_cart_exception(self):
        return dict(title=u'', message=u'誠に申し訳ございませんが、現在ご購入ができない状態になっております。しばらく経ってからお試しください')

    @lbr_view_config(context=OverOrderLimitException)
    def over_order_limit_exception(self):
        location = self.request.route_url('cart.index', event_id=self.context.event_id)
        msg = u'{performance.name} の購入は {limit} 回までとなっております。 <br><a href="{location}">{event.title}の購入ページに戻る</a>'
        return dict(title=u'',
                    message=Markup(msg.format(location=location,
                                              limit=self.context.order_limit,
                                              event=self.context.event,
                                              performance=self.context.performance)))

    @lbr_view_config(context=OverQuantityLimitException)
    def over_quantity_limit_exception(self):
        location = self.request.route_url('cart.index', event_id=self.context.event_id)
        msg = u'{performance.name} の購入は {limit} 枚までとなっております。 <br><a href="{location}">{event.title}の購入ページに戻る</a>'
        return dict(title=u'',
                    message=Markup(msg.format(location=location,
                                              limit=self.context.quantity_limit,
                                              event=self.context.event,
                                              performance=self.context.performance)))


    @lbr_view_config(context=InvalidCartStatusError)
    def invalid_cart_status_error(self):
        return dict(message=Markup(u'大変申し訳ございません。ブラウザの複数ウィンドウからの操作や、戻るボタン等の操作により、予約を継続することができません。<br>'
                                   u'ご予約の際は複数ウィンドウや戻るボタンを使わずにご予約ください。'))

    @lbr_view_config(context=PaymentError)
    def payment_delivery_exception(self):
        if hasattr(self.context, 'back_url') and self.context.back_url is not None:
            try:
                # カートの救済可能な場合
                api.recover_cart(self.request)
                transaction.commit()
            except Exception as e:
                import sys
                logger.info(e.message, exc_info=sys.exc_info())
            return HTTPFound(location=self.context.back_url)
        else:
            event_id = self.context.event_id
            if event_id is not None:
                location = self.request.route_url('cart.index', event_id=event_id)
            else:
                location = self.context.host_base_url
        return dict(title=u'決済エラー', message=Markup(u'決済中にエラーが発生しました。しばらく時間を置いてから<a href="%s">再度お試しください。</a>' % location))

    # ブースター、FCのみ
    @lbr_view_config(context=NotEnoughStockException)
    def not_enough_stock_exception(self):
        return dict(message=u"在庫がありません。\nご希望の座席を確保できませんでした。")

@view_defaults(xhr=True, renderer='json')
class XHROnlyExcView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @lbr_view_config(context=TooManyCartsCreated)
    def too_many_cart_exception_xhr(self):
        return dict(result='NG', reason='too many carts')

@view_defaults(renderer=selectable_renderer('message.html'), request_type='altair.mobile.interfaces.IMobileRequest')
class MobileOnlyExcView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @lbr_view_config(context=QuantityOutOfBoundsError)
    def quantity_out_of_bounds_error(self):
        if self.context.quantity_given < self.context.min_quantity:
            return dict(message=u"枚数は合計%d枚以上で選択してください" % self.context.min_quantity)
        else:
            return dict(message=u"枚数は合計%d枚以内で選択してください" % self.context.max_quantity)

    @lbr_view_config(context=ProductQuantityOutOfBoundsError)
    def product_quantity_out_of_bounds_error(self):
        if self.context.quantity_given < self.context.min_quantity:
            return dict(message=u"商品個数は合計%d個以上で選択してください" % self.context.min_quantity)
        else:
            return dict(message=u"商品個数は合計%d個以内で選択してください" % self.context.max_quantity)

    @lbr_view_config(context=PerStockTypeQuantityOutOfBoundsError)
    def per_stock_type_quantity_out_of_bounds_error(self):
        if self.context.max_quantity is not None:
            if self.context.min_quantity is not None:
                return dict(message=u"枚数は合計%d〜%d枚の範囲内で選択してください" % (self.context.min_quantity, self.context.max_quantity))
            else:
                return dict(message=u"枚数は合計%d枚以内で選択してください" % (self.context.max_quantity, ))
        else:
            return dict(message=u"枚数は合計%d枚以上で選択してください" % (self.context.min_quantity, ))

    @lbr_view_config(context=PerStockTypeProductQuantityOutOfBoundsError)
    def per_stock_type_product_quantity_out_of_bounds_error(self):
        if self.context.max_quantity is not None:
            if self.context.min_quantity is not None:
                return dict(message=u"商品個数は合計%d〜%d個の範囲内で選択してください" % (self.context.min_quantity, self.context.max_quantity))
            else:
                return dict(message=u"商品個数は合計%d個以内で選択してください" % (self.context.max_quantity, ))
        else:
            return dict(message=u"商品個数は合計%d個以上で選択してください" % (self.context.min_quantity, ))

    @lbr_view_config(context=PerProductProductQuantityOutOfBoundsError)
    def per_product_product_quantity_out_of_bounds_error(self):
        if self.context.max_quantity is not None:
            if self.context.min_quantity is not None:
                return dict(message=u"商品個数は合計%d〜%d個の範囲内で選択してください" % (self.context.min_quantity, self.context.max_quantity))
            else:
                return dict(message=u"商品個数は合計%d個以内で選択してください" % (self.context.max_quantity, ))
        else:
            return dict(message=u"商品個数は合計%d個以上で選択してください" % (self.context.min_quantity, ))

    @lbr_view_config(context=NotEnoughStockException)
    def not_enough_stock_exception(self):
        return dict(message=u"在庫がありません。\nご希望の座席を確保できませんでした。")

    @lbr_view_config(context=InvalidSeatSelectionException)
    def invalid_seat_selection_exception(self):
        return dict(message=u"座席選択に誤りがあります。\n座席を再度選択してください。")

    @lbr_view_config(context=InvalidProductSelectionException)
    def invalid_product_selection_exception(self):
        return dict(message=u"席種選択に誤りがあります。\n席種を再度選択してください。")

    @lbr_view_config(context=NotEnoughAdjacencyException)
    def not_enough_ajacency_exception(self):
        return dict(message=u"連席で座席を確保できません。個別に購入してください。")

    @lbr_view_config(context=CartCreationException)
    def cart_creation_exception(self):
        return dict(message=u"カートを作成できませんでした。しばらく時間を置いてから再度お試しください。")

    @lbr_view_config(context=InvalidCSRFTokenException)
    def invalid_csrf_token_exception(self):
        return dict(message=u"ウェブブラウザの戻るボタンは使用できません。画面上の戻るボタンから操作して下さい。")
