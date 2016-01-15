#! /usr/bin/env python
#-*- coding: utf-8 -*-
import sys
import argparse
import datetime
import logging

import transaction
import pyramid.paster
import pyramid.threadlocal

import altair.sqlahelper
from altair.sqlahelper import get_db_session
from sqlalchemy import (
    and_,
    or_,
)
import altair.multilock
from altair.app.ticketing.models import DBSession
from altair.app.ticketing.orders.api import get_order_by_order_no
from altair.app.ticketing.mails.api import get_mail_utility
from altair.app.ticketing.core.models import (
    Performance,
    MailTypeEnum,
    Organization,
    OrganizationSetting,
    DeliveryMethod,
    PaymentMethod,
    PaymentDeliveryMethodPair,
    )
from altair.app.ticketing.sej.models import SejOrder
from altair.app.ticketing.famiport.models import FamiPortOrder
from altair.app.ticketing.orders.models import (
    Order,
    OrderNotification,
    )
from altair.app.ticketing.payments.plugins import SEJ_DELIVERY_PLUGIN_ID, SEJ_PAYMENT_PLUGIN_ID,FAMIPORT_DELIVERY_PLUGIN_ID,FAMIPORT_PAYMENT_PLUGIN_ID

logger = logging.getLogger(__name__)


def get_target_order_nos(today, skip_already_notified=True):
    now = datetime.datetime.now()
    today = datetime.datetime.combine(today, datetime.time())
    # 今日の24時
    tomorrow = today + datetime.timedelta(1)
    # 明日の24時
    day_after_tomorrow = today + datetime.timedelta(2)
    # 明後日の24時
    # two_day_after_tomorrow = today + datetime.timedelta(3)

    sej_q = DBSession.query(SejOrder)\
        .filter(SejOrder.ticketing_start_at <= now)\
        .filter(SejOrder.ticketing_due_at > now)\
        .with_entities(SejOrder.order_no)
    sej_order_no = [o[0] for o in sej_q]

    session = get_db_session(pyramid.threadlocal.get_current_request(), 'famiport')
    famiport_q = session.query(FamiPortOrder)\
        .filter(FamiPortOrder.ticketing_start_at <= now)\
        .filter(FamiPortOrder.ticketing_end_at > now)\
        .with_entities(FamiPortOrder.order_no)
    famiport_order_no = [o[0] for o in famiport_q]

    q = DBSession.query(Order)\
        .join(Performance)\
        .join(Organization)\
        .join(OrganizationSetting)\
        .join(PaymentDeliveryMethodPair)\
        .join(DeliveryMethod, and_(PaymentDeliveryMethodPair.delivery_method_id==DeliveryMethod.id))\
        .join(PaymentMethod, and_(PaymentDeliveryMethodPair.payment_method_id==PaymentMethod.id))\
        .filter(Performance.start_on.between(tomorrow, day_after_tomorrow))\
        .filter(OrganizationSetting.notify_print_remind_mail == True)\
        .filter(Order.canceled_at == None)\
        .filter(Order.refunded_at == None)\
        .filter(Order.refund_id == None)\
        .filter(Order.paid_at != None)\
        .filter((Order.issued_at == None) | (Order.issued_at >= today))

    q1 = q.filter(and_(DeliveryMethod.delivery_plugin_id == SEJ_DELIVERY_PLUGIN_ID, Order.order_no.in_(sej_order_no)))\
        .filter(or_((PaymentMethod.payment_plugin_id != SEJ_PAYMENT_PLUGIN_ID),
                and_(PaymentMethod.payment_plugin_id == SEJ_PAYMENT_PLUGIN_ID,Order.issuing_start_at != Order.payment_start_at)))##代引きを除く

    q2 = q.filter(and_(DeliveryMethod.delivery_plugin_id == FAMIPORT_DELIVERY_PLUGIN_ID, Order.order_no.in_(famiport_order_no)))\
        .filter(or_((PaymentMethod.payment_plugin_id != FAMIPORT_PAYMENT_PLUGIN_ID),
                and_(PaymentMethod.payment_plugin_id == FAMIPORT_PAYMENT_PLUGIN_ID,Order.issuing_start_at != Order.payment_start_at)))##代引きを除く

    if skip_already_notified:
        q1 = q1.join(OrderNotification).filter(OrderNotification.print_remind_at == None)
        q2 = q2.join(OrderNotification).filter(OrderNotification.print_remind_at == None)

    q = q1.union(q2)
    return [order_no_named_tuple[0] for order_no_named_tuple in (q.with_entities(Order.order_no))]

def send_print_remind_mail(settings):
    request = pyramid.threadlocal.get_current_request()

    order_nos = get_target_order_nos(datetime.date.today())
    utility = get_mail_utility(request, MailTypeEnum.TicketPrintRemindMail)

    for order_no in order_nos:
        order = get_order_by_order_no(request, order_no)
        if order and order.order_notification:
            now = datetime.datetime.now()
            utility.send_mail(request, order)
            order_notification = order.order_notification
            order_notification.print_remind_at = now
            order_notification.save()
            transaction.commit()


def main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--conf')
    opts = parser.parse_args(argv)

    pyramid.paster.setup_logging(opts.conf)
    env = pyramid.paster.bootstrap(opts.conf)
    settings = env['registry'].settings

    try:
        with altair.multilock.MultiStartLock('send_print_remind_mail'):
            send_print_remind_mail(settings)
    except altair.multilock.AlreadyStartUpError as err:
        logger.warn('{}'.format(repr(err)))


if __name__ == '__main__':
    sys.exit(main())
