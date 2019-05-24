# -*- coding:utf-8 -*-
import sys
import logging
import transaction
from zope.interface import implementer
from datetime import datetime
from sqlalchemy.orm.util import _is_mapped_class
from altair.app.ticketing.models import DBSession
from altair.app.ticketing.orders.models import Order
from .interfaces import IPayment, IPaymentCart

from .api import (
    get_error_result_code,
    authorize_point,
    fix_point,
    exec_point_rollback,
    get_preparer,
    lookup_plugin
)
from .exceptions import PointSecureApprovalFailureError, PaymentPluginException
from altair.app.ticketing.core.models import PointUseTypeEnum
from altair.app.ticketing.point import api as point_api
from altair.app.ticketing.point.exceptions import PointAPIResponseParseException

logger = logging.getLogger(__name__)

@implementer(IPayment)
class Payment(object):
    """ 決済
    """
    def __init__(self, cart, request, session=None, now=None, cancel_payment_on_failure=True, easy_id=None):
        if now is None:
            now = datetime.now()
        self.request = request
        self.cart = cart
        self.sales_segment = cart.sales_segment
        self.session = session or DBSession
        self.now = now
        self.get_preparer = get_preparer
        self.lookup_plugin = lookup_plugin
        self.cancel_payment_on_failure = cancel_payment_on_failure
        self.easy_id = easy_id

    def _bind_order(self, order):
        order.organization_id = order.performance.event.organization_id
        order.browserid = self.request.browserid
        self.cart.order = order

    def _get_plugins(self, payment_delivery_pair):
        return self.lookup_plugin(self.request, payment_delivery_pair)

    def call_prepare(self):
        """ 決済方法前呼び出し
        """
        preparer = self.get_preparer(self.request, self.cart.payment_delivery_pair)
        if preparer is None:
            raise Exception(u'get_preparer() returned None (payment_method_id=%d, delivery_method_id=%d)' % (self.cart.payment_delivery_pair.payment_method.id, self.cart.payment_delivery_pair.delivery_method.id))
        res = preparer.prepare(self.request, self.cart)
        return res

    def call_delegator(self):
        """ 確認後決済フロー
        """
        preparer = self.get_preparer(self.request, self.cart.payment_delivery_pair)
        if preparer is None:
            raise Exception
        if hasattr(preparer, 'delegator'):
            return preparer.delegator(self.request, self.cart)
        return None

    def call_validate(self):
        """ 決済処理前の状態チェック
        """
        preparer = self.get_preparer(self.request, self.cart.payment_delivery_pair)
        if preparer is None:
            raise Exception
        if hasattr(preparer, 'validate'):
            return preparer.validate(self.request, self.cart)
        return None

    def call_payment(self):
        """ 決済処理
        """
        self.call_validate()

        payment_delivery_plugin, payment_plugin, delivery_plugin = self._get_plugins(self.cart.payment_delivery_pair)

        unique_id = None
        # ポイント利用がある場合は Point API でポイントを確保して承認させ、PointRedeem にステータスを記録する
        if self.cart.point_use_type is not PointUseTypeEnum.NoUse:
            unique_id = self.secure_and_apply_point()
            
        try:
            if payment_delivery_plugin is not None:
                if IPaymentCart.providedBy(self.cart):
                    order = payment_delivery_plugin.finish(self.request, self.cart)
                    self._bind_order(order)
                else:
                    payment_delivery_plugin.finish2(self.request, self.cart)
                    order = self.cart
            else:
                # 決済と配送を別々に処理する
                if IPaymentCart.providedBy(self.cart):
                    order = payment_plugin.finish(self.request, self.cart)
                    self._bind_order(order)
                    try:
                        delivery_plugin.finish(self.request, self.cart)
                    except Exception as e:
                        exc_info = sys.exc_info()
                        order.deleted_at = self.now
                        if self.cancel_payment_on_failure:
                            payment_plugin.cancel(self.request, order)
                        raise exc_info[1], None, exc_info[2]
                else:
                    logger.info('cart is not a IPaymentCart')
                    payment_plugin.finish2(self.request, self.cart)
                    order = self.cart
                    delivery_plugin.finish2(self.request, self.cart)
            return order

        except Exception as e:
            # unique_id がある場合は承認したポイントをロールバックする
            if unique_id:
                exec_point_rollback(self.request, self.easy_id, unique_id, self.cart.order_no, self.session)
            if isinstance(e, PaymentPluginException) and e.ignorable:  # 無視できる例外の場合
                logger.warn(u'the ignorable error occurred during payment(order_no=%s). The reason: %s',
                            self.cart.order_no, e, exc_info=1)
            else:
                logger.error(u'[PMT0001]Failed to call payment(order_no=%s). The reason: %s',
                             self.cart.order_no, e, exc_info=1)
            raise e

    def call_payment2(self, order):
        payment_delivery_plugin, payment_plugin, delivery_plugin = self._get_plugins(self.cart.payment_delivery_pair)
        if payment_delivery_plugin is not None:
            payment_delivery_plugin.finish2(self.request, order)
        else:
            payment_plugin.finish2(self.request, order)
            try:
                delivery_plugin.finish2(self.request, self.cart)
            except Exception:
                exc_info = sys.exc_info()
                order.deleted_at = self.now
                if self.cancel_payment_on_failure:
                    payment_plugin.cancel(self.request, order)
                raise exc_info[1], None, exc_info[2]
        return order

    def call_delivery(self, order):
        payment_delivery_plugin, payment_plugin, delivery_plugin = self._get_plugins(self.cart.payment_delivery_pair)
        if delivery_plugin is not None:
            if IPaymentCart.providedBy(self.cart):
                self._bind_order(order)
                delivery_plugin.finish(self.request, self.cart)
            else:
                delivery_plugin.finish2(self.request, self.cart)
        else:
            logger.info(
                u'no delivery plugin for %s (plugin_id=%d)' % (
                    self.cart.payment_delivery_pair.delivery_method.name,
                    self.cart.payment_delivery_pair.delivery_method.delivery_plugin_id
                    )
                )

    def secure_and_apply_point(self):
        """
        ポイント確保＆承認処理
        Point API でポイントを確保して承認させ、PointRedeem にステータスを記録する。
        正常に処理されたとき unique_id を返却する。失敗した場合はロールバック処理を行う
        """
        request, cart, easy_id, session = self.request, self.cart, self.easy_id, self.session
        group_id = request.organization.setting.point_group_id
        reason_id = request.organization.setting.point_reason_id
        unique_id = None
        try:
            req_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # 使用ポイントを確保 (オーソリ)
            auth_response = authorize_point(request, easy_id, cart, group_id, reason_id, req_time)
            auth_error_result_code = get_error_result_code(request, auth_response)
            if auth_error_result_code:
                # 使用ポイントの確保に失敗
                raise PointSecureApprovalFailureError(message='point api auth-stdonly returned error response.',
                                                      result_code=auth_error_result_code)

            unique_id = point_api.get_unique_id(auth_response)
            logger.debug('Point API auth-stdonly called. Point has been secured: unique_id=%s', unique_id)

            # PointRedeem テーブルへオーソリのステータスで Insert
            point_redeem_id = point_api.insert_point_redeem(auth_response, unique_id, cart.order_no,
                                                            group_id, reason_id, req_time, session)
            logger.debug('PointRedeem (id=%s, unique_id=%s) added with auth status.', point_redeem_id, unique_id)

            # 確保したポイントを承認
            fix_response = fix_point(request, easy_id, cart, group_id, reason_id, req_time, unique_id)
            fix_error_result_code = get_error_result_code(request, fix_response)
            if fix_error_result_code:
                # 確保したポイントの承認に失敗
                raise PointSecureApprovalFailureError(message='point api fix returned error response.',
                                                      result_code=fix_error_result_code)

            logger.debug('Point API fix called. Secured point has been applied: unique_id=%s', unique_id)

            # PointRedeem テーブルをFixのステータスに更新
            point_api.update_point_redeem_for_fix(fix_response, unique_id, req_time, session)
            logger.debug('PointRedeem point_status changed to fix status')

            # ポイント承認まで成功の場合は unique_id を返却して終了
            return unique_id
        except (PointSecureApprovalFailureError, PointAPIResponseParseException) as e:  # Point API 起因のエラー
            logger.error(e.message)  # stack trace は出力されているので Error レベル
            result_code = getattr(e, 'result_code', list())
        except Exception as e:  # PointRedeem 更新でエラー・その他
            logger.exception('Unexpected Error occurred while securing and applying point. : %s', e)
            result_code = list()

        # unique_id がある場合はロールバックを行う
        if unique_id:
            try:
                exec_point_rollback(request, easy_id, unique_id, cart.order_no, session)
            except PointSecureApprovalFailureError as rollback_err:
                result_code.extend(rollback_err.result_code)
        raise PointSecureApprovalFailureError(result_code=result_code)
