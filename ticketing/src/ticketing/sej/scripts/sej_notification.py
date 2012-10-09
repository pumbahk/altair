# coding: utf-8

import optparse
import sys
import sqlahelper

from pyramid.paster import bootstrap

from datetime import datetime
from dateutil import parser as date_parser
from os.path import abspath, dirname

from ticketing.sej.models import SejNotification, SejOrder, SejTicket
from ticketing.core.models import Order
from ticketing.orders.events import notify_order_canceled

sys.path.append(abspath(dirname(dirname(__file__))))

from paste.deploy import loadapp

import logging
import logging.config
import sqlahelper

log = logging.getLogger(__name__)

from sqlalchemy import and_

def get_sej_order(notification):
    if notification.exchange_number and notification.billing_number:
        return SejOrder.filter(
            and_(
                SejOrder.order_id       == notification.order_id,
                SejOrder.exchange_number== notification.exchange_number,
                SejOrder.billing_number == notification.billing_number
                )
            ).first()
    elif notification.exchange_number:
        return SejOrder.filter(and_(SejOrder.order_id       == notification.order_id, SejOrder.exchange_number== notification.exchange_number)).first()
    elif notification.billing_number:
        return SejOrder.filter(and_(SejOrder.order_id       == notification.order_id, SejOrder.billing_number == notification.billing_number)).first()

def get_order(sej_order):
    return Order.filter_by(order_no = sej_order.order_id).first()

def reflect_ticketing_and_payment(request, sej_order, order, notification):
    sej_order.processed_at = notification.processed_at
    payment_type = int(notification.payment_type)
    exchange_number = notification.exchange_number

    log.info(" payment_type=%s", payment_type)
    if payment_type == 1:
        # 代引
        order.paid_at = sej_order.processed_at
        order.issued_at = order.printed_at = sej_order.processed_at
    elif payment_type == 2:
        # 前払後日発券
        if exchange_number is None:
            # 支払
            order.paid_at = sej_order.processed_at
        else:
            # 発券
            order.issued_at = order.printed_at = sej_order.processed_at
    elif payment_type == 3:
        # 代済発券
        if order.paid_at is None:
            log.warning("Order #%s: ticketing notification received, but the corresponding order was not marked 'paid'" % (order.order_no))
        order.issued_at = order.printed_at = sej_order.processed_at
    elif payment_type == 4:
        # 前払のみ
        order.paid_at = sej_order.processed_at

    sej_order.process_id = notification.process_number
    sej_order.pay_store_number = notification.pay_store_number
    sej_order.pay_store_name = notification.pay_store_name
    sej_order.ticketing_store_number = notification.ticketing_store_number
    sej_order.ticketing_store_name = notification.ticketing_store_name

    notification.reflected_at = datetime.now()
    sej_order.reflected_at = datetime.now()

def reflect_cancel_from_svc(request, sej_order, order, notification):
    order.release()
    order.canceled_at = datetime.now()
    order.save()
    sej_order.reflected_at = datetime.now()
    sej_order.canceled_at = datetime.now()
    notification.reflected_at = datetime.now()
    notify_order_canceled(request, order)

def reflect_expire(request, sej_order, order, notification):
    order.release()
    order.canceled_at = datetime.now()
    order.save()
    sej_order.reflected_at = datetime.now()
    sej_order.canceld_at = datetime.now()
    notification.reflected_at = datetime.now()
    notify_order_canceled(request, order)

def reflect_re_grant(request, sej_order, order, notification):
    sej_order.exchange_number         = notification.exchange_number_new
    sej_order.billing_number          = notification.billing_number_new
    for sej_ticket in sej_order.tickets:
        code = notification.barcode_numbers.get('X_barcode_no_%02d' % sej_ticket.ticket_idx)
        if code:
            sej_ticket.barcode_number = code

    sej_order.reflected_at = datetime.now()

def dummy(request, sej_order, order, notification):
    pass

def process_notifications():
    nlist = SejNotification.filter_by(reflected_at=None).limit(500).all()
    for notification in nlist:
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
    actions = {
        '1'  : reflect_ticketing_and_payment,
        '31' : reflect_cancel_from_svc,
        '72' : reflect_re_grant,
        '73' : reflect_expire
    }
    for sej_order, order, notification in process_notifications():
        action = actions.get(notification.notification_type, dummy)
        log.info("Processing notification: process_number=%s, order_no=%s, exchange_number=%s, billing_number=%s, action=%s", notification.process_number, sej_order.order_id, notification.exchange_number, notification.billing_number, action.__name__)
        action(request, sej_order, order, notification)

def main(argv=sys.argv):

    if len(sys.argv) < 2:
        print "usage: python sej_notification.py development.ini"
        sys.exit()
    ini_file = sys.argv[1]
    env = bootstrap(ini_file)
    logging.config.fileConfig(ini_file)
    request = env['request']
    registry = env['registry']
    settings = registry.settings

    import transaction
    trans = transaction.begin()
    process_notification(request)
    trans.commit()

if __name__ == u"__main__":
    main(sys.argv)
