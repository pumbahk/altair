# -*- coding:utf-8 -*-

#
# SEJとの外部結合の為に使ったスクリプト
#

import optparse
import sys
import sqlahelper

from pyramid.paster import bootstrap

from datetime import datetime
from dateutil import parser as date_parser
from os.path import abspath, dirname

from ticketing.sej.models import SejNotification, SejOrder, SejTicket
from ticketing.orders.models import Order
from ticketing.orders.events import notify_order_canceled

sys.path.append(abspath(dirname(dirname(__file__))))

from paste.deploy import loadapp

import logging

logging.basicConfig()
log = logging.getLogger(__file__)

from sqlalchemy import and_

def get_sej_order(notification):
    return SejOrder.filter(
        and_(
            SejOrder.order_id       == notification.order_id,
            SejOrder.exchange_number== notification.exchange_number,
            SejOrder.billing_number == notification.billing_number
        )
    ).first()

def get_order(sej_order):
    return Order.filter(
        and_(
            Order.order_id == SejOrder.order_id
        )
    ).one()

def reflect_ticketing_and_payment(request, sej_order, order, notification):
    order.paid_at = sej_order.processed_at

    sej_order.process_id = notification.process_id
    sej_order.pay_store_number = notification.pay_store_number
    sej_order.pay_store_name = notification.pay_store_name
    sej_order.ticketing_store_number = notification.ticketing_store_number
    sej_order.ticketing_store_name = notification.ticketing_store_name

    sej_order.reflected_at = datetime.now()

def reflect_cancel_from_svc(request, sej_order, order, notification):
    notify_order_canceled(request, order)
    sej_order.reflected_at = datetime.now()

def reflect_expire(request, sej_order, order, notification):
    notify_order_canceled(request, order)
    sej_order.reflected_at = datetime.now()

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
    list = SejNotification.filter_by(reflected_at=None).limit(500).all()
    for notification in list:
        sej_order = get_sej_order(notification)
        if sej_order:
            order = get_order(sej_order)
            if order:
                yield sej_order, order, notification
            else:
                logging.error("Order Not found: %s,%s,%s" % (notification.order_id, notification.exchange_number,notification.billing_number))
        else:
            logging.error("SejOrder Not found: %s,%s,%s" % (notification.order_id, notification.exchange_number,notification.billing_number))

def process_notification(request):
    reflected_at = datetime.now()
    actions = {
        '1'  : reflect_ticketing_and_payment,
        '31' : reflect_cancel_from_svc,
        '72' : reflect_re_grant,
        '73' : reflect_expire
    }
    for sej_order, order, notification in process_notifications():
        actions.get(sej_order.notification_type, dummy)(request, sej_order, order, notification)

def main(argv=sys.argv):

    if len(sys.argv) < 2:
        print "usage: python sej_notification.py development.ini"
        sys.exit()
    ini_file = sys.argv[1]
    env = bootstrap(ini_file)
    request = env['request']
    registry = env['registry']
    settings = registry.settings

    hostname = settings['sej.inticket_api_url']
    shop_id = settings['sej.shop_id']
    secret_key = settings['sej.api_key']

    import transaction

    tran = transaction.begin()
    process_notification(request)
    tran.commit()

if __name__ == u"__main__":
    main(sys.argv)