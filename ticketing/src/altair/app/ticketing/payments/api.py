# encoding: utf-8

import logging
import transaction

from zope.interface import directlyProvides
from pyramid.interfaces import IRequest
from zope.deprecation import deprecation

from .interfaces import ICartInterface
from .exceptions import (
    PaymentDeliveryMethodPairNotFound,
    PaymentCartNotAvailable,
    OrderLikeValidationFailure,
    PointSecureApprovalFailureError
)
from .interfaces import IPaymentPreparerFactory, IPaymentPreparer, IPaymentDeliveryPlugin, IPaymentPlugin, IDeliveryPlugin
from .directives import Discriminator
from altair.app.ticketing.core.models import PaymentMethod, DeliveryMethod
from altair.app.ticketing.point import api as point_api
from altair.point import api as point_client
from altair.point.exceptions import PointAPIError

logger = logging.getLogger(__name__)

OBSOLETED_SUCCESS_URL_KEY = 'payment_confirm_url'

@deprecation.deprecate("this method should be removed after the code gets released")
def set_confirm_url(request, url):
    request.session[OBSOLETED_SUCCESS_URL_KEY] = url

def is_finished_payment(request, pdmp, order):
    if order is None:
        return False
    plugin = get_payment_plugin(request, pdmp.payment_method.payment_plugin_id)
    return plugin.finished(request, order)

def is_finished_delivery(request, pdmp, order):
    if order is None:
        return False
    plugin = get_delivery_plugin(request, pdmp.delivery_method.delivery_plugin_id)
    return plugin.finished(request, order)

def get_cart(request, retrieve_invalidated=False):
    cart_if = request.registry.getUtility(ICartInterface)
    cart = cart_if.get_cart(request, retrieve_invalidated=retrieve_invalidated)
    if cart is None:
        raise PaymentCartNotAvailable(u'cart is not available')
    if cart.payment_delivery_pair is None:
        raise PaymentDeliveryMethodPairNotFound(u'payment/delivery method not specified')
    return cart

def get_cart_by_order_no(request, order_no, retrieve_invalidated=False):
    cart_if = request.registry.getUtility(ICartInterface)
    return cart_if.get_cart_by_order_no(request, order_no, retrieve_invalidated=retrieve_invalidated)

def make_order_from_cart(request, context, cart):
    cart_if = request.registry.getUtility(ICartInterface)
    return cart_if.make_order_from_cart(request, context, cart)

def cont_complete_view(context, request, order_no, magazine_ids, word_ids):
    cart_if = request.registry.getUtility(ICartInterface)
    return cart_if.cont_complete_view(context, request, order_no, magazine_ids, word_ids)

def get_confirm_url(request):
    cart_if = request.registry.getUtility(ICartInterface)
    return cart_if.get_success_url(request)

def get_delivery_plugin(request_or_registry, plugin_id):
    if IRequest.providedBy(request_or_registry):
        registry = request_or_registry.registry
    else:
        registry = request_or_registry
    key = str(Discriminator(None, plugin_id))
    return registry.utilities.lookup([], IDeliveryPlugin, name=key)

def get_payment_plugin(request_or_registry, plugin_id):
    if IRequest.providedBy(request_or_registry):
        registry = request_or_registry.registry
    else:
        registry = request_or_registry
    key = str(Discriminator(plugin_id, None))
    return registry.utilities.lookup([], IPaymentPlugin, name=key)

def get_payment_delivery_plugin(request_or_registry, payment_plugin_id, delivery_plugin_id):
    if IRequest.providedBy(request_or_registry):
        registry = request_or_registry.registry
    else:
        registry = request_or_registry
    key = str(Discriminator(payment_plugin_id, delivery_plugin_id))
    return registry.utilities.lookup([], IPaymentDeliveryPlugin, key)

def get_preparer(request, payment_delivery_pair):
    if payment_delivery_pair is None:
        raise PaymentDeliveryMethodPairNotFound
    payment_delivery_plugin = get_payment_delivery_plugin(request,
        payment_delivery_pair.payment_method.payment_plugin_id,
        payment_delivery_pair.delivery_method.delivery_plugin_id,)

    if payment_delivery_plugin is not None:
        directlyProvides(payment_delivery_plugin, IPaymentPreparer)
        return payment_delivery_plugin
    else:
        payment_plugin = get_payment_plugin(request, payment_delivery_pair.payment_method.payment_plugin_id)
        if payment_plugin is not None:
            directlyProvides(payment_plugin, IPaymentPreparer)
            return payment_plugin

directlyProvides(get_preparer, IPaymentPreparerFactory)

def lookup_plugin(request, payment_delivery_pair):
    assert payment_delivery_pair is not None
    payment_delivery_plugin = get_payment_delivery_plugin(request,
        payment_delivery_pair.payment_method.payment_plugin_id,
        payment_delivery_pair.delivery_method.delivery_plugin_id,)
    if payment_delivery_plugin is None:
        payment_plugin = get_payment_plugin(request, payment_delivery_pair.payment_method.payment_plugin_id)
        delivery_plugin = get_delivery_plugin(request, payment_delivery_pair.delivery_method.delivery_plugin_id)
    else:
        payment_plugin = None
        delivery_plugin = None
    if payment_delivery_plugin is None and \
       (payment_plugin is None or delivery_plugin is None):
        raise PaymentDeliveryMethodPairNotFound(u"対応する決済プラグインか配送プラグインが見つかりませんでした")
    return payment_delivery_plugin, payment_plugin, delivery_plugin

def validate_order_like(request, order_like, update=False):
    payment_delivery_plugin, payment_plugin, delivery_plugin = lookup_plugin(request, order_like.payment_delivery_pair)
    if payment_delivery_plugin is not None:
        payment_delivery_plugin.validate_order(request, order_like, update=update)
    else:
        payment_plugin.validate_order(request, order_like, update=update)
        delivery_plugin.validate_order(request, order_like, update=update)

def get_payment_delivery_plugin_ids(payment_method_id, delivery_method_id):
    """支払と引取タイプIDを返す

    引数：
        payment_method_id (int): 支払方法ID
        delivery_method_id (int): 取引方法ID

    戻り値：
        payment_plugin_id
        delivery_plugin_id
    """
    payment_plugin_id = PaymentMethod.filter_by(id=payment_method_id).one().payment_plugin_id
    delivery_plugin_id = DeliveryMethod.filter_by(id=delivery_method_id).one().delivery_plugin_id

    return payment_plugin_id, delivery_plugin_id

def validate_length_dict(encoding_method, order_dict, target_dict):
    keys = target_dict.keys()
    for key in keys:
        if order_dict.has_key(key):
            try:
                if(len(order_dict.get(key).encode(encoding_method)) > target_dict.get(key)):
                    raise OrderLikeValidationFailure(u'too long', 'shipping_address.{0}'.format(key))
            except UnicodeEncodeError:
                raise OrderLikeValidationFailure('shipping_address.{0} contains a character that is not encodable as {1}'.format(key, encoding_method), 'shipping_address.{0}'.format(key))


def get_error_result_code(request, point_api_response):
    """
    Point API レスポンスのエラー result_code をリストで返却する。
    """
    result_code = point_api.get_result_code(point_api_response)
    return list(filter(lambda c: c != request.registry.settings['point_api.successful.result_code'], result_code))


def authorize_point(request, easy_id, point_amount, group_id, reason_id, req_time):
    """
    使用ポイントを確保 (オーソリ) して Point API auth-stdonly レスポンスを返却する。
    """
    try:
        return point_client.auth_stdonly(request, easy_id, int(point_amount), req_time, group_id, reason_id)
    except PointAPIError as e:
        # Point API のコール失敗。stack trace は altair.point で出力されている
        logger.error(e.message)
        raise PointSecureApprovalFailureError('Failed to call Point API auth-stdonly.')


def fix_point(request, easy_id, point_amount, group_id, reason_id, req_time, unique_id, order_no):
    """
    確保したポイントを承認して Point API fix レスポンスを返却する。
    """
    try:
        return point_client.fix(request, easy_id, int(point_amount), unique_id, order_no, group_id, reason_id, req_time)
    except PointAPIError as e:
        # Point API のコール失敗。stack trace は altair.point で出力されている
        logger.error(e.message)
        raise PointSecureApprovalFailureError('Failed to call Point API fix.')


def exec_point_rollback(request, easy_id, unique_id, order_no):
    """
    ロールバック処理を行う。
    確保もしくは承認されたポイントを Point API でロールバックし、PointRedeem からレコードを削除する。
    """
    group_id = request.organization.setting.point_group_id
    reason_id = request.organization.setting.point_reason_id
    rollback_error_result_code = list()
    exc_info = None
    try:
        rollback_response = point_client.rollback(request, easy_id, unique_id, group_id, reason_id)
        rollback_error_result_code = get_error_result_code(request, rollback_response)
    except PointAPIError as e:
        # Point API のコール失敗。stack trace は altair.point で出力されている
        logger.error(e.message)
        exc_info = e
    except Exception as e:
        # Point API レスポンスの Parse 失敗, もしくはその他のエラー
        logger.exception('Unexpected Error occurred while executing point rollback. : %s', e)
        exc_info = e

    # PointRedeem テーブルから対象のレコード削除
    # Point API rollback 失敗でも PointRedeem から削除することで, Point付き合わせバッチでステータスが異なり, エラーを判明することができる
    del_result = _delete_from_point_redeem(unique_id, order_no)

    if exc_info is not None:
        # Point API rollback コールもしくはレスポンスのパース失敗
        logger.error('Failed to call Point API rollback. : unique_id= %s', unique_id)
        raise PointSecureApprovalFailureError(result_code=rollback_error_result_code)
    elif not del_result:
        # PointRedeemからレコード削除失敗
        raise PointSecureApprovalFailureError('Failed to delete record from PointRedeem. : '
                                              'unique_id={}'.format(unique_id))
    else:
        logger.debug('Point rollback done successfully.')


def _delete_from_point_redeem(unique_id, order_no):
    """
    PointRedeem テーブルから対象のレコード削除する。
    """
    result = True
    try:
        point_api.update_point_redeem_for_rollback(unique_id, order_no)
        logger.debug('Deleted record from PointRedeem.')
    except Exception as e:
        logger.exception('Failed to delete record from PointRedeem: %s', e)
        result = False
    return result
