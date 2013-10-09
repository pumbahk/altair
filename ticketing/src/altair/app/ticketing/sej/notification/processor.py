# coding: utf-8

import logging

from zope.interface import implementer

from altair.app.ticketing.orders.events import notify_order_canceled
from altair.app.ticketing.models import DBSession

from .models import SejNotification, SejNotificationType

from .interfaces import ISejNotificationProcessor

logger = logging.getLogger(__name__)

__all__ = [
    'SejNotificationProcessorError',
    'SejNotificationProcessor',
    ]

class SejNotificationProcessorError(Exception):
    pass

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
        elif payment_type == SejPaymentType.Prepayment.v:
            # 前払後日発券
            if exchange_number is None:
                # 支払
                sej_order.mark_paid(notification.processed_at)
                order.mark_paid(notification.processed_at)
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

        sej_order.processed_at = notification.processed_at
        sej_order.process_id = notification.process_number
        sej_order.pay_store_number = notification.pay_store_number
        sej_order.pay_store_name = notification.pay_store_name
        sej_order.ticketing_store_number = notification.ticketing_store_number
        sej_order.ticketing_store_name = notification.ticketing_store_name

        notification.reflected_at = self.now

    @__order_required
    def reflect_cancel_from_svc(self, sej_order, order, notification):
        order.release()
        order.mark_canceled(notification.processed_at)
        order.updated_at = self.now
        sej_order.mark_canceled(notification.processed_at)
        sej_order.processed_at = notification.processed_at
        notification.reflected_at = self.now
        notify_order_canceled(self.request, order)

    def reflect_expire(self, sej_order, order, notification):
        from ..models import SejPaymentType
        if order is not None:
            # 対応するOrderがない場合はスキップする (see #5610)
            # 代済発券はキャンセルしない
            payment_type = int(notification.payment_type)
            if payment_type != SejPaymentType.Paid.v:
                order.release()
                order.mark_canceled(notification.processed_at)
                order.updated_at = self.now
                sej_order.canceled_at = notification.processed_at
                sej_order.mark_canceled(notification.processed_at)
                notify_order_canceled(self.request, order)
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
        branch = sej_order.new_branch(
            payment_type=notification.payment_type_new,
            exchange_number=notification.exchange_number_new,
            billing_number=notification.billing_number_new,
            ticketing_due_at=notification.ticketing_due_at,
            processed_at = notification.processed_at
            )
        DBSession.add(branch)
        # XXX: バーコード番号は無条件で更新してしまう (ごめんなさい)
        # やっぱり古い番号はキープしておいたほうがよいかもしれない
        for sej_ticket in SejTicket.query.filter_by(order_no=sej_order.order_no):
            code = notification.barcode_numbers.get(str(sej_ticket.ticket_idx))
            if code:
                sej_ticket.barcode_number = code
        notification.reflected_at = self.now

    actions = {
        SejNotificationType.PaymentComplete.v  : reflect_ticketing_and_payment,
        SejNotificationType.CancelFromSVC.v    : reflect_cancel_from_svc,
        SejNotificationType.ReGrant.v          : reflect_re_grant,
        SejNotificationType.TicketingExpire.v  : reflect_expire
        }

    def __init__(self, request, now):
        self.request = request     
        self.now = now

    def __call__(self, sej_order, order, notification):
        action = self.actions.get(int(notification.notification_type), None)
        if action is None:
            raise SejNotificationProcessorError('unsupported notification type: %s' % notification.notification_type)
        else:
            action(self, sej_order, order, notification)

