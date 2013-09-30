# coding: utf-8

import optparse
import sys
from datetime import datetime
from sqlalchemy import and_

from altair.app.ticketing.core.models import Order
from altair.app.ticketing.orders.events import notify_order_canceled

from .models import (
    SejNotification,
    SejOrder,
    SejTicket,
    SejNotificationType,
    SejPaymentType
    )

import logging

log = logging.getLogger(__name__)

__all__ = [
    'process_notification'
    ]

def get_sej_order(notification):
    if notification.exchange_number and notification.billing_number:
        return SejOrder.filter(
            and_(
                SejOrder.order_id        == notification.order_id,
                SejOrder.exchange_number == (notification.exchange_number or None),
                SejOrder.billing_number  == (notification.billing_number or None)
                )
            ).first()
    elif notification.exchange_number:
        return SejOrder.filter(and_(SejOrder.order_id       == notification.order_id, SejOrder.exchange_number== notification.exchange_number)).first()
    elif notification.billing_number:
        return SejOrder.filter(and_(SejOrder.order_id       == notification.order_id, SejOrder.billing_number == notification.billing_number)).first()

def get_order(sej_order):
    return Order.filter_by(order_no = sej_order.order_id).first()

def reflect_ticketing_and_payment(request, sej_order, order, notification):
    now = datetime.now()
    sej_order.processed_at = notification.processed_at
    payment_type = int(notification.payment_type)
    exchange_number = notification.exchange_number

    log.info(" payment_type=%s", payment_type)
    if payment_type == SejPaymentType.CashOnDelivery.v:
        # 代引
        sej_order.mark_paid(sej_order.processed_at)
        sej_order.mark_issued(sej_order.processed_at)
        order.mark_paid(sej_order.processed_at)
        order.mark_issued_or_printed(issued=True, printed=True, now=sej_order.processed_at)
    elif payment_type == SejPaymentType.Prepayment.v:
        # 前払後日発券
        if exchange_number is None:
            # 支払
            sej_order.mark_paid(sej_order.processed_at)
            order.mark_paid(sej_order.processed_at)
        else:
            # 発券
            sej_order.mark_issued(sej_order.processed_at)
            order.mark_issued_or_printed(issued=True, printed=True, now=sej_order.processed_at)
    elif payment_type == SejPaymentType.Paid.v:
        # 代済発券
        if order.paid_at is None:
            log.warning("Order #%s: ticketing notification received, but the corresponding order was not marked 'paid'" % (order.order_no))
        sej_order.mark_issued(sej_order.processed_at)
        order.mark_issued_or_printed(issued=True, printed=True, now=sej_order.processed_at)
    elif payment_type == SejPaymentType.PrepaymentOnly.v:
        # 前払のみ
        sej_order.mark_paid(sej_order.processed_at)
        order.mark_paid(sej_order.processed_at)

    sej_order.process_id = notification.process_number
    sej_order.pay_store_number = notification.pay_store_number
    sej_order.pay_store_name = notification.pay_store_name
    sej_order.ticketing_store_number = notification.ticketing_store_number
    sej_order.ticketing_store_name = notification.ticketing_store_name

    notification.reflected_at = datetime.now() # SAFE TO USE datetime.now() HERE

def reflect_cancel_from_svc(request, sej_order, order, notification):
    now = notification.processed_at
    order.release()
    order.mark_canceled(now)
    order.save()
    sej_order.mark_canceled(now)
    sej_order.processed_at = notification.processed_at
    notification.reflected_at = datetime.now() # SAFE TO USE datetime.now() HERE
    notify_order_canceled(request, order)

def reflect_expire(request, sej_order, order, notification):
    now = notification.processed_at
    # 代済発券はキャンセルしない
    payment_type = int(notification.payment_type)
    if payment_type != SejPaymentType.Paid.v:
        order.release()
        order.mark_canceled(now)
        order.save()
        sej_order.mark_canceled(now)
        notify_order_canceled(request, order)
    sej_order.processed_at = notification.processed_at
    notification.reflected_at = datetime.now() # SAFE TO USE datetime.now() HERE

def reflect_re_grant(request, sej_order, order, notification):
    sej_order.exchange_number         = notification.exchange_number_new
    sej_order.billing_number          = notification.billing_number_new
    for sej_ticket in sej_order.tickets:
        code = notification.barcode_numbers.get('X_barcode_no_%02d' % sej_ticket.ticket_idx)
        if code:
            sej_ticket.barcode_number = code
    sej_order.processed_at = notification.processed_at

def dummy(request, sej_order, order, notification):
    pass

actions = {
    SejNotificationType.PaymentComplete.v  : reflect_ticketing_and_payment,
    SejNotificationType.CancelFromSVC.v    : reflect_cancel_from_svc,
    SejNotificationType.ReGrant.v          : reflect_re_grant,
    SejNotificationType.TicketingExpire.v  : reflect_expire
    }

def fetch_notifications():
    for notification in SejNotification.filter_by(reflected_at=None):
        sej_order = get_sej_order(notification)
        if sej_order:
            order = get_order(sej_order)
            if order:
                yield sej_order, order, notification
            else:
                logging.error("Order Not found: order_no=%s, exchange_number=%s, billing_number=%s" % (notification.order_id, notification.exchange_number,notification.billing_number))
        else:
            logging.error("SejOrder Not found: order_no=%s, exchange_number=%s, billing_number=%s" % (notification.order_id, notification.exchange_number,notification.billing_number))

def process_notification(request):
    reflected_at = datetime.now()
    for sej_order, order, notification in fetch_notifications():
        action = actions.get(int(notification.notification_type), dummy)
        log.info("Processing notification: process_number=%s, order_no=%s, exchange_number=%s, billing_number=%s, action=%s", notification.process_number, sej_order.order_id, notification.exchange_number, notification.billing_number, action.__name__)
        action(request, sej_order, order, notification)
