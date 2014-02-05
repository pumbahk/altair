# encoding: utf-8

from altair.app.ticketing.sej.notification.builder import SejNotificationRequestParamBuilder
from altair.app.ticketing.sej import models as sej_models
from pyramid.paster import bootstrap
from sqlalchemy.sql.expression import desc
from altair.app.ticketing.models import DBSession
from altair.app.ticketing.core import models as c_models
from altair.app.ticketing.utils import uniurlencode
from urllib import urlencode
from datetime import datetime, timedelta
import argparse
import sys

def generate_process_number(order):
    """order.idから適当に12桁の数字を生成"""
    prev_notification = sej_models.SejNotification.query.filter_by(order_no=order.order_no).order_by(desc(sej_models.SejNotification.created_at)).first()
    if prev_notification is None:
        return "%010d%02d" % (order.id, order.branch_no)
    else:
        return "%012d" % (long(prev_notification.process_number) + 1)

def get_order(order_no):
    return DBSession.query(c_models.Order).filter_by(order_no=order_no).order_by(desc(c_models.Order.branch_no)).limit(1).one()

def get_sej_order(order_no, exchange_number=None, billing_number=None):
    q = DBSession.query(sej_models.SejOrder) \
        .filter_by(order_no=order_no) \
        .order_by(desc(sej_models.SejOrder.branch_no)).limit(1)
    if exchange_number is not None:
        q = q.filter_by(exchange_number=exchange_number)
    if billing_number is not None:
        q = q.filter_by(billing_number=billing_number)
    return q.one()

def create_expire_notification_from_order(order_no, exchange_number, billing_number):
    order = get_order(order_no)
    sej_order = get_sej_order(order.order_no, exchange_number=exchange_number, billing_number=billing_number)
    tenant = DBSession.query(sej_models.SejTenant).filter_by(organization_id=order.organization_id).one()
    return tenant, sej_models.SejNotification(
        notification_type=sej_models.SejNotificationType.TicketingExpire.v,
        process_number=generate_process_number(order),
        shop_id=tenant.shop_id,
        order_no=sej_order.order_no,
        payment_type=sej_order.payment_type,
        ticketing_due_at=sej_order.ticketing_due_at,
        billing_number=sej_order.billing_number,
        exchange_number=sej_order.exchange_number,
        processed_at=datetime.now()
        )

def create_payment_notification_from_order(order_no, exchange_number, billing_number):
    order = get_order(order_no)
    sej_order = get_sej_order(order.order_no, exchange_number=exchange_number, billing_number=billing_number)
    tenant = DBSession.query(sej_models.SejTenant).filter_by(organization_id=order.organization_id).one()
    return tenant, sej_models.SejNotification(
        notification_type=sej_models.SejNotificationType.PaymentComplete.v,
        process_number=generate_process_number(order),
        shop_id=tenant.shop_id,
        order_no=sej_order.order_no,
        payment_type=sej_order.payment_type,
        ticketing_due_at=sej_order.ticketing_due_at,
        billing_number=sej_order.billing_number,
        exchange_number=sej_order.exchange_number,
        total_price=sej_order.total_price,
        ticket_count=sej_order.ticket_count,
        total_ticket_count=sej_order.total_ticket_count,
        pay_store_name=u'テスト店舗',
        pay_store_number=u'000000',
        ticketing_store_name=u'テスト店舗',
        ticketing_store_number=u'000000',
        processed_at=datetime.now()
        )

def create_cancel_notification_from_order(order_no, exchange_number, billing_number):
    order = get_order(order_no)
    sej_order = get_sej_order(order.order_no, exchange_number=exchange_number, billing_number=billing_number)
    tenant = DBSession.query(sej_models.SejTenant).filter_by(organization_id=order.organization_id).one()
    return tenant, sej_models.SejNotification(
        notification_type=sej_models.SejNotificationType.CancelFromSVC.v,
        process_number=generate_process_number(order),
        shop_id=tenant.shop_id,
        order_no=sej_order.order_no,
        payment_type=sej_order.payment_type,
        ticketing_due_at=sej_order.ticketing_due_at,
        billing_number=sej_order.billing_number,
        exchange_number=sej_order.exchange_number,
        total_price=sej_order.total_price,
        ticket_count=sej_order.ticket_count,
        total_ticket_count=sej_order.total_ticket_count,
        pay_store_name=u'テスト店舗',
        pay_store_number=u'000000',
        ticketing_store_name=u'テスト店舗',
        ticketing_store_number=u'000000',
        cancel_reason=u'',
        return_ticket_count=0,
        processed_at=datetime.now()
        )

def create_regrant_notification_from_order(order_no, exchange_number, billing_number):
    order = get_order(order_no)
    sej_order = get_sej_order(order.order_no, exchange_number=exchange_number, billing_number=billing_number)
    tenant = DBSession.query(sej_models.SejTenant).filter_by(organization_id=order.organization_id).one()
    billing_number_new = sej_order.billing_number and '%d' % (int(sej_order.billing_number) + 1)
    exchange_number_new = sej_order.exchange_number and '%d' % (int(sej_order.exchange_number) + 1)
    ticketing_due_at = sej_order.ticketing_due_at or datetime.now()
    ticketing_due_at_new = ticketing_due_at.replace(year=(ticketing_due_at.year + 1))
    return tenant, sej_models.SejNotification(
        notification_type=sej_models.SejNotificationType.ReGrant.v,
        process_number=generate_process_number(order),
        shop_id=tenant.shop_id,
        order_no=sej_order.order_no,
        payment_type=sej_order.payment_type,
        payment_type_new=sej_order.payment_type,
        ticketing_due_at=sej_order.ticketing_due_at,
        billing_number=sej_order.billing_number,
        exchange_number=sej_order.exchange_number,
        billing_number_new=billing_number_new,
        exchange_number_new=exchange_number_new,
        ticketing_due_at_new=ticketing_due_at_new,
        total_price=sej_order.total_price,
        ticket_count=sej_order.ticket_count,
        total_ticket_count=sej_order.total_ticket_count,
        pay_store_name=u'テスト店舗',
        pay_store_number=u'000000',
        ticketing_store_name=u'テスト店舗',
        ticketing_store_number=u'000000',
        barcode_numbers=dict(
            (sej_ticket.ticket_idx, str(int(sej_ticket.barcode_number) + 1))
            for sej_ticket in sej_order.tickets
            ),
        processed_at=datetime.now()
        )


actions = {
    sej_models.SejNotificationType.PaymentComplete.v: create_payment_notification_from_order,
    sej_models.SejNotificationType.CancelFromSVC.v:   create_cancel_notification_from_order,
    sej_models.SejNotificationType.TicketingExpire.v: create_expire_notification_from_order,
    sej_models.SejNotificationType.ReGrant.v:         create_regrant_notification_from_order,
    }

class ApplicationError(Exception):
    pass

def main(env, args):
    parser = argparse.ArgumentParser()
    parser.add_argument('-E', '--exchange-number', metavar='enumber', type=str, help='exchange number')
    parser.add_argument('-B', '--billing-number', metavar='bnumber', type=str, help='billing number')
    parser.add_argument('action', metavar='action', type=str, help='action')
    parser.add_argument('order_no', metavar='orderno', type=str, help='order number')
    _args = parser.parse_args(args)
    settings = env['registry'].settings
    try:
        action = None
        enum_ = getattr(sej_models.SejNotificationType, _args.action, None)
        if enum_ is not None:
            action = actions.get(int(enum_))
        if action is None:
            raise ApplicationError('unknown action: possible actions are %s' % ', '.join(en.k for en in sej_models.SejNotificationType._values))
        order_no = _args.order_no
        exchange_number = _args.exchange_number
        billing_number = _args.billing_number
        tenant, notification = action(order_no, exchange_number=exchange_number, billing_number=billing_number)
        builder = SejNotificationRequestParamBuilder(tenant.api_key or settings['sej.api_key'])
        params = builder(notification)
        sys.stdout.write(uniurlencode(params, method='raw', encoding='CP932'))
    except ApplicationError as e:
        sys.stderr.write(e.message + "\n")
        sys.stderr.flush()

if __name__ == '__main__':
    import sys
    config_file = sys.argv[1]
    env = bootstrap(config_file)
    main(env, sys.argv[2:])
