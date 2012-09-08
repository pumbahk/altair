# encoding: utf-8

from ticketing.sej.api import create_sej_notification_data_from_record
from ticketing.sej import models as sej_models, resources as sej_resources
from pyramid.paster import bootstrap
from ticketing.models import DBSession
from ticketing.core import models as c_models
from urllib import urlencode
from datetime import datetime

def generate_process_number(order):
    """order.idから適当に12桁の数字を生成"""
    return "%012d" % order.id 

def create_expire_sej_notification_from_order(shop_id, order):
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

def main(env, args):
    settings = env['registry'].settings
    order = DBSession.query(c_models.Order).filter_by(order_no=args[0]).one()
    tenant = DBSession.query(sej_models.SejTenant).filter_by(organization_id=order.organization_id).one()
    params = create_sej_notification_data_from_record(
        create_expire_sej_notification_from_order(tenant.shop_id, order),
        tenant.api_key or settings['sej.api_key'])
    sys.stdout.write(urlencode(params).encode('CP932'))

if __name__ == '__main__':
    import sys
    config_file = sys.argv[1]
    env = bootstrap(config_file)
    main(env, sys.argv[2:])
