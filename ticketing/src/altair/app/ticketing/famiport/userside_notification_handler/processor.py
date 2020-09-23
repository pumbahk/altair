# coding: utf-8

import sys
import logging
import traceback

from sqlalchemy.orm.session import object_session
from datetime import datetime

from altair.point.api import cancel as point_api_cancel
from altair.app.ticketing.orders.events import notify_order_canceled
from altair.app.ticketing.orders.api import get_order_by_order_no
from altair.app.ticketing.point.api import update_point_redeem_for_cancel
from altair.app.ticketing.rakuten_tv.api import rakuten_tv_sales_data_to_order_paid_at, rakuten_tv_sales_data_to_order_canceled_at

from ..userside_models import AltairFamiPortNotificationType

logger = logging.getLogger(__name__)

__all__ = [
    'AltairFamiPortNotificationProcessorError',
    'AltairFamiPortNotificationProcessor',
    ]

class AltairFamiPortNotificationProcessorError(Exception):
    def __init__(self, message, nested_exc_info=None):
        super(AltairFamiPortNotificationProcessorError, self).__init__(message, nested_exc_info)

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
        buf.append(u'AltairFamiPortNotificationProcessorError: %s\n' % self.message)
        if self.nested_exc_info:
            buf.append('\n  -- nested exception --\n')
            for line in traceback.format_exception(*self.nested_exc_info):
                for _line in line.rstrip().split('\n'):
                    buf.append('  ')
                    buf.append(_line)
                    buf.append('\n')
        return ''.join(buf)


class AltairFamiPortNotificationProcessor(object):
    def __init__(self, request, registry):
        self.request = request
        self.registry = registry

    def handle_completed(self, order, notification, now):
        if notification.type in (AltairFamiPortNotificationType.PaymentCompleted.value,
                                 AltairFamiPortNotificationType.PaymentAndTicketingCompleted.value):
            order.mark_paid(now=now)
            # rakutenTVと連携されたオーダーを払済にする
            rakuten_tv_sales_data_to_order_paid_at(order)
        if notification.type in (AltairFamiPortNotificationType.TicketingCompleted.value,
                                 AltairFamiPortNotificationType.PaymentAndTicketingCompleted.value):
            order.mark_issued_or_printed(issued=True, printed=True, now=now)

    def handle_canceled(self, order, notification, now):
        if notification.type in (AltairFamiPortNotificationType.PaymentCanceled.value,
                                 AltairFamiPortNotificationType.PaymentAndTicketingCanceled.value):
            order.paid_at = None
        if notification.type in (AltairFamiPortNotificationType.TicketingCanceled.value,
                                 AltairFamiPortNotificationType.PaymentAndTicketingCanceled.value):
            order.issued_at = None
            order.printed_at = None

    def handle_expired(self, order, notification, now):
        pass

    def handle_order_canceled(self, order, notification, now):
        if order.paid_at is None:
            order.release()
            order.mark_canceled(now)
            order.updated_at = now
            notify_order_canceled(self.request, order)

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
        else:
            logger.info("Order(order_no=%s) is already marked paid; do nothing" % order.order_no)

    def handle_refunded(self, order):
        logger.info("not implemented")

    actions = {
        AltairFamiPortNotificationType.PaymentCompleted.value: handle_completed,
        AltairFamiPortNotificationType.TicketingCompleted.value: handle_completed,
        AltairFamiPortNotificationType.PaymentAndTicketingCompleted.value: handle_completed,
        AltairFamiPortNotificationType.PaymentCanceled.value: handle_canceled,
        AltairFamiPortNotificationType.TicketingCanceled.value: handle_canceled,
        AltairFamiPortNotificationType.PaymentAndTicketingCanceled.value: handle_canceled,
        AltairFamiPortNotificationType.OrderCanceled.value: handle_order_canceled,
        AltairFamiPortNotificationType.Refunded.value: handle_refunded,
        AltairFamiPortNotificationType.OrderExpired.value: handle_expired,
        }

    def __call__(self, notification, now):
        action = self.actions.get(notification.type, None)
        if action is None:
            raise AltairFamiPortNotificationProcessorError('unsupported notification type: %s' % notification.notification_type)
        else:
            sys.exc_clear()
            try:
                order = get_order_by_order_no(self.request, notification.order_no)
                if order is None:
                    raise AltairFamiPortNotificationProcessorError('Order does not exist: %s' % notification.order_no)
                action(self, order, notification, now)
                notification.reflected_at = now
            except:
                raise AltairFamiPortNotificationProcessorError('error occurred during processing notification (id: %s, type: %s, order_no: %s)' %
                                                              (notification.id, notification.type, notification.order_no), nested_exc_info=sys.exc_info())
