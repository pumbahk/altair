# encoding: utf-8

from altair.app.ticketing.sej.api import create_sej_notification_data_from_record
from altair.app.ticketing.sej import models as sej_models, resources as sej_resources
from pyramid.paster import bootstrap
from altair.app.ticketing.models import DBSession
from altair.app.ticketing.core import models as c_models
from altair.app.ticketing.utils import uniurlencode
from urllib import urlencode
from datetime import datetime
import sys

def generate_process_number(order):
    """order.idから適当に12桁の数字を生成"""
    return "%012d" % order.id 

def create_expire_notification_from_order(shop_id, order):
    sej_order = DBSession.query(sej_models.SejOrder).filter_by(order_id=order.order_no).one()
    return sej_models.SejNotification(
        # XXX: なんでこれ resources の中にあんだよ...
        notification_type=sej_resources.SejNotificationType.TicketingExpire.v,
        process_number=generate_process_number(order),
        shop_id=shop_id,
        order_id=sej_order.order_id,
        payment_type=sej_order.payment_type,
        ticketing_due_at=sej_order.ticketing_due_at,
        billing_number=sej_order.billing_number,
        exchange_number=sej_order.exchange_number,
        processed_at=datetime.now()
        )

def create_payment_notification_from_order(shop_id, order):
    sej_order = DBSession.query(sej_models.SejOrder).filter_by(order_id=order.order_no).one()
    return sej_models.SejNotification(
        # XXX: なんでこれ resources の中にあんだよ...
        notification_type=sej_resources.SejNotificationType.PaymentComplete.v,
        process_number=generate_process_number(order),
        shop_id=shop_id,
        order_id=sej_order.order_id,
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

actions = {
    sej_resources.SejNotificationType.PaymentComplete.v: create_payment_notification_from_order,
    sej_resources.SejNotificationType.TicketingExpire.v: create_expire_notification_from_order,
    }

class ApplicationError(Exception):
    pass

def main(env, args):
    settings = env['registry'].settings
    try:
        action = actions.get(int(getattr(sej_resources.SejNotificationType, args[0], None)))
        if action is None:
            raise ApplicationError('unknown action')
        order = DBSession.query(c_models.Order).filter_by(order_no=args[1]).one()
        tenant = DBSession.query(sej_models.SejTenant).filter_by(organization_id=order.organization_id).one()
        params = create_sej_notification_data_from_record(
            action(tenant.shop_id, order),
            tenant.api_key or settings['sej.api_key'])
        sys.stdout.write(uniurlencode(params, method='raw', encoding='CP932'))
    except ApplicationError as e:
        sys.stderr.write(e.message + "\n")
        sys.stderr.flush()

if __name__ == '__main__':
    import sys
    config_file = sys.argv[1]
    env = bootstrap(config_file)
    main(env, sys.argv[2:])
