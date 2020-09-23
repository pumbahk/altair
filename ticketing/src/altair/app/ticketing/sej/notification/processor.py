# coding: utf-8

import sys
import logging
import traceback

from zope.interface import implementer
from sqlalchemy.orm.session import object_session
from datetime import datetime

from altair.point.api import cancel as point_api_cancel
from altair.app.ticketing.orders.events import notify_order_canceled
from altair.app.ticketing.point.api import update_point_redeem_for_cancel
from altair.app.ticketing.rakuten_tv.api import rakuten_tv_sales_data_to_order_paid_at, rakuten_tv_sales_data_to_order_canceled_at

from ..api import get_sej_orders
from .models import SejNotification, SejNotificationType

from .interfaces import ISejNotificationProcessor

logger = logging.getLogger(__name__)

__all__ = [
    'SejNotificationProcessorError',
    'SejNotificationProcessor',
    ]

class SejNotificationProcessorError(Exception):
    def __init__(self, message, nested_exc_info=None):
        super(SejNotificationProcessorError, self).__init__(message, nested_exc_info)

    @property
    def message(self):
        return self.args[0]

    @property
    def nested_exc_info(self):
        return self.args[1]

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        buf = []
        buf.append(u'SejNotificationProcessorError: %s\n' % self.message)
        if self.nested_exc_info:
            buf.append('\n  -- nested exception --\n')
            for line in traceback.format_exception(*self.nested_exc_info):
                for _line in line.rstrip().split('\n'):
                    buf.append('  ')
                    buf.append(_line)
                    buf.append('\n')
        return ''.join(buf)


@implementer(ISejNotificationProcessor)
class SejNotificationProcessor(object):
    def __order_required(fn):
        def _(self, sej_order, order, notification):
            if order is None:
                raise SejNotificationProcessorError("Order Not found: order_no=%s, exchange_number=%s, billing_number=%s" % (
                    notification.order_no,
                    notification.exchange_number,
                    notification.billing_number))
            return fn(self, sej_order, order, notification)
        return _

    @__order_required
    def reflect_ticketing_and_payment(self, sej_order, order, notification):
        from ..models import SejPaymentType
        payment_type = int(notification.payment_type)
        exchange_number = notification.exchange_number

        logger.info(" payment_type=%s", payment_type)
        if payment_type == SejPaymentType.CashOnDelivery.v:
            # 代引
            sej_order.mark_paid(notification.processed_at)
            sej_order.mark_issued(notification.processed_at)
            order.mark_paid(notification.processed_at)
            order.mark_issued_or_printed(issued=True, printed=True, now=notification.processed_at)
            # rakutenTVと連携されたオーダーを払済にする
            rakuten_tv_sales_data_to_order_paid_at(order)
        elif payment_type == SejPaymentType.Prepayment.v:
            # 前払後日発券
            if not exchange_number: # None もしくは空文字 (多分空文字)
                # 支払
                sej_order.mark_paid(notification.processed_at)
                order.mark_paid(notification.processed_at)
                # rakutenTVと連携されたオーダーを払済にする
                rakuten_tv_sales_data_to_order_paid_at(order)
            else:
                # 発券
                sej_order.mark_issued(notification.processed_at)
                order.mark_issued_or_printed(issued=True, printed=True, now=notification.processed_at)
        elif payment_type == SejPaymentType.Paid.v:
            # 代済発券
            if order.paid_at is None:
                logger.warning("Order #%s: ticketing notification received, but the corresponding order was not marked 'paid'" % (order.order_no))
            sej_order.mark_issued(notification.processed_at)
            order.mark_issued_or_printed(issued=True, printed=True, now=notification.processed_at)
        elif payment_type == SejPaymentType.PrepaymentOnly.v:
            # 前払のみ
            sej_order.mark_paid(notification.processed_at)
            order.mark_paid(notification.processed_at)
            # rakutenTVと連携されたオーダーを払済にする
            rakuten_tv_sales_data_to_order_paid_at(order)

        sej_order.processed_at = notification.processed_at
        sej_order.process_id = notification.process_number
        sej_order.pay_store_number = notification.pay_store_number
        sej_order.pay_store_name = notification.pay_store_name
        sej_order.ticketing_store_number = notification.ticketing_store_number
        sej_order.ticketing_store_name = notification.ticketing_store_name

        notification.reflected_at = self.now

    @__order_required
    def reflect_cancel_from_svc(self, sej_order, order, notification):
        _session = object_session(sej_order)
        sej_order.mark_canceled(notification.processed_at)
        sej_order.processed_at = notification.processed_at
        notification.reflected_at = self.now
        self.cancel_order_if_necessary(order, notification.processed_at, _session)

    def reflect_expire(self, sej_order, order, notification):
        from ..models import SejPaymentType
        _session = object_session(sej_order)
        # 対応するOrderがない場合はスキップする (see #5610)
        if order is not None:
            # 代済発券および前払後日発券でかつ支払済の場合はキャンセル状態にしない refs #9838
            if int(notification.payment_type) != int(SejPaymentType.Paid) and \
               (int(notification.payment_type) != int(SejPaymentType.Prepayment) or sej_order.pay_at is None):
                sej_order.canceled_at = notification.processed_at
                sej_order.mark_canceled(notification.processed_at)
                self.cancel_order_if_necessary(order, notification.processed_at, _session)
            sej_order.processed_at = notification.processed_at
        else:
            logger.warning("Order Not found: order_no=%s, exchange_number=%s, billing_number=%s" % (
                notification.order_no,
                notification.exchange_number,
                notification.billing_number))
        notification.reflected_at = self.now

    @__order_required
    def reflect_re_grant(self, sej_order, order, notification):
        from ..models import SejTicket
        _session = object_session(sej_order)
        branch = sej_order.new_branch(
            payment_type=notification.payment_type_new,
            exchange_number=notification.exchange_number_new,
            billing_number=notification.billing_number_new,
            ticketing_due_at=notification.ticketing_due_at,
            processed_at = notification.processed_at
            )
        _session.add(branch)
        for sej_ticket in _session.query(SejTicket).filter_by(order_no=sej_order.order_no):
            barcode_number = notification.barcode_numbers.get(str(sej_ticket.ticket_idx), sej_ticket.barcode_number)
            _session.add(sej_ticket.new_branch(order=branch, barcode_number=barcode_number))

        notification.reflected_at = self.now

    actions = {
        SejNotificationType.PaymentComplete.v  : reflect_ticketing_and_payment,
        SejNotificationType.CancelFromSVC.v    : reflect_cancel_from_svc,
        SejNotificationType.ReGrant.v          : reflect_re_grant,
        SejNotificationType.TicketingExpire.v  : reflect_expire
        }

    def cancel_order_if_necessary(self, order, processed_at, _session):
        sej_orders = get_sej_orders(order.order_no, fetch_canceled=False, session=_session)
        # もしすべての枝番がキャンセルされているようであれば、本注文をキャンセルする refs #6525
        if len(sej_orders) == 0:
            order.release()
            order.mark_canceled(processed_at)
            order.updated_at = self.now
            notify_order_canceled(self.request, order)

            # シリアルコード開放
            # ExternalSerialCodeOrderの削除、ExternalSerialCodeのused_atを削除
            for token in order.items[0].elements[0].tokens:
                for external_serial_code_order in token.external_serial_code_orders:
                    external_serial_code_order.deleted_at = self.now
                    external_serial_code_order.external_serial_code.used_at = None

            # rakutenTVと連携されたオーダーをキャンセルする
            rakuten_tv_sales_data_to_order_canceled_at(order)

            # ポイント利用している場合は充当をキャンセルする
            if order.point_redeem is not None:
                # ポイントキャンセルAPIリクエスト
                req_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                point_api_response = point_api_cancel(request=self.registry,
                                                      easy_id=order.point_redeem.easy_id,
                                                      unique_id=order.point_redeem.unique_id,
                                                      fix_id=order.point_redeem.order_no,
                                                      group_id=order.point_redeem.group_id,
                                                      reason_id=order.point_redeem.reason_id,
                                                      req_time=req_time)

                # PointRedeemテーブル更新
                update_point_redeem_for_cancel(point_api_response,
                                               req_time,
                                               order.point_redeem.unique_id)

    def __init__(self, request, registry, now):
        self.request = request
        self.registry = registry
        self.now = now

    def __call__(self, sej_order, order, notification):
        action = self.actions.get(int(notification.notification_type), None)
        if action is None:
            raise SejNotificationProcessorError('unsupported notification type: %s' % notification.notification_type)
        else:
            _session = object_session(sej_order)
            sys.exc_clear()
            try:
                action(self, sej_order, order, notification)
            except:
                raise SejNotificationProcessorError('error occurred during processing notification %s' % notification.process_number, nested_exc_info=sys.exc_info())
            finally:
                _session.commit()
