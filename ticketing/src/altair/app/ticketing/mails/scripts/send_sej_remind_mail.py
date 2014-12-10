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
import altair.multilock
from altair.app.ticketing.models import DBSession
from altair.app.ticketing.orders.api import get_order_by_order_no
from altair.app.ticketing.mails.api import get_mail_utility
from altair.app.ticketing.core.models import (
    MailTypeEnum,
    Organization,
    OrganizationSetting,
    PaymentMethod,
    PaymentDeliveryMethodPair,
    )
from altair.app.ticketing.sej.models import SejOrder
from altair.app.ticketing.orders.models import (
    Order,
    OrderNotification,
    )
from altair.app.ticketing.payments.plugins import SEJ_PAYMENT_PLUGIN_ID

logger = logging.getLogger(__name__)


def get_target_order_nos(today, skip_already_notified=True):
    today = datetime.datetime.combine(today, datetime.time())
    tomorrow = today + datetime.timedelta(1)
    day_after_tomorrow = today + datetime.timedelta(2)

    subqs = DBSession.query(SejOrder)\
      .filter(SejOrder.payment_due_at.between(tomorrow, day_after_tomorrow))\
      .with_entities(SejOrder.order_no)

    q = DBSession.query(Order)\
        .join(Organization)\
        .join(OrganizationSetting)\
        .join(PaymentDeliveryMethodPair)\
        .join(PaymentMethod)\
        .filter(PaymentMethod.payment_plugin_id == SEJ_PAYMENT_PLUGIN_ID)\
        .filter(OrganizationSetting.notify_remind_mail == True)\
        .filter(Order.canceled_at == None)\
        .filter(Order.refunded_at == None)\
        .filter(Order.refund_id == None)\
        .filter(Order.paid_at == None)\
        .filter(Order.order_no.in_(subqs))

    if skip_already_notified:
        q = q.join(OrderNotification).filter(OrderNotification.sej_remind_at == None)

    return [order_no_named_tuple[0] for order_no_named_tuple in q.with_entities(Order.order_no)]


def send_sej_remind_mail(settings):
    request = pyramid.threadlocal.get_current_request()

    order_nos = get_target_order_nos(datetime.date.today())
    utility = get_mail_utility(request, MailTypeEnum.PurcacheSejRemindMail)

    for order_no in order_nos:
        order = get_order_by_order_no(request, order_no)
        if order and order.order_notification:
            now = datetime.datetime.now()
            utility.send_mail(request, order)
            order_notification = order.order_notification
            order_notification.sej_remind_at = now
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
        with altair.multilock.MultiStartLock('send_sej_remind_mail'):
            send_sej_remind_mail(settings)
    except altair.multilock.AlreadyStartUpError as err:
        logger.warn('{}'.format(repr(err)))


if __name__ == '__main__':
    sys.exit(main())
