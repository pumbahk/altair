# -*- coding:utf-8 -*-

import os
import sys
from datetime import datetime, timedelta
import logging
import transaction
import argparse

from pyramid.paster import bootstrap, setup_logging   
from pyramid.renderers import render_to_response
from sqlalchemy import and_
from sqlalchemy.sql.expression import not_
from sqlalchemy.sql import func
import sqlahelper

from altair.app.ticketing.core.models import DBSession, SeatStatus, SeatStatusEnum, Order, OrderedProduct, OrderedProductItem
from altair.app.ticketing.core.models import PaymentDeliveryMethodPair, PaymentMethod, DeliveryMethod, ShippingAddress, Mailer
from altair.app.ticketing.payments import plugins
from altair.app.ticketing.events.sales_reports.reports import sendmail
from altair.app.ticketing.sej.refund import create_and_send_refund_file

def update_seat_status():
    _keep_to_vacant()

def _keep_to_vacant():
    ''' 座席ステータスがKeepのままの座席をVacantに戻す
    '''
    config_file = sys.argv[1]
    log_file = os.path.abspath(sys.argv[2])
    logging.config.fileConfig(log_file)
    app_env = bootstrap(config_file)
    registry = app_env['registry']

    logging.info('start update seat_status batch')

    try:
        DBSession.bind = DBSession.bind or sqlahelper.get_session().bind

        expire_minute = int(registry.settings['altair.inner_cart.expire_minute'])
        expire_to = datetime.now() - timedelta(minutes=expire_minute)
        expire_from = expire_to - timedelta(days=1)
        logging.info('expire_to : %s (now - %s minute)' % (expire_to, expire_minute))

        seats = SeatStatus.filter_by(status=int(SeatStatusEnum.Keep))\
                          .filter(SeatStatus.updated_at.between(expire_from, expire_to))\
                          .with_entities(SeatStatus.seat_id).all()
        logging.info('target seat_id : %s' % seats)

        if seats:
            query = SeatStatus.__table__.update().values(
                {'status': int(SeatStatusEnum.Vacant)}
            ).where(and_(SeatStatus.status==int(SeatStatusEnum.Keep), SeatStatus.updated_at.between(expire_from, expire_to)))
            DBSession.bind.execute(query)
    except Exception as e:
        logging.error('failed to update SeatStatus (%s)' % e.message)
    else:
        logging.info('success')

    logging.info('end update seat_status batch')

def refund_order():
    ''' 払戻処理
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument('config')
    args = parser.parse_args()

    setup_logging(args.config)
    env = bootstrap(args.config)
    request = env['request']
    registry = env['registry']

    logging.info('start refund_order batch')

    # 1件ずつ払戻処理
    orders_to_skip = set()
    while True:
        query = Order.query.filter(Order.refund_id!=None, Order.refunded_at==None)
        if orders_to_skip:
            query = query.filter(not_(Order.id.in_(orders_to_skip)))
        order = query.first()

        if not order:
            logging.info('target order not found')
            break

        try:
            logging.info('try to refund order (%s)' % order.id)
            if order.call_refund(request):
                logging.info('refund success')
                transaction.commit()
            else:
                logging.error('failed to refund order (%s)' % order.order_no)
                transaction.abort()
                orders_to_skip.add(order.id)
        except Exception as e:
            logging.error('failed to refund orders (%s)' % e.message)
            break

    # SEJ払戻ファイル送信
    create_and_send_refund_file(registry.settings)

    logging.info('end refund_order batch')

def detect_fraud():
    ''' 不正予約の監視
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument('config')
    parser.add_argument('-f')
    parser.add_argument('-t')
    args = parser.parse_args()

    setup_logging(args.config)
    env = bootstrap(args.config)
    request = env['request']
    registry = env['registry']

    now = datetime.now()
    period_from = args.f if args.f else now.strftime('%Y-%m-%d %H:%M')
    period_to = args.t if args.t else (now - timedelta(days=1)).strftime('%Y-%m-%d %H:%M')

    logging.info('start detect_fraud batch')

    # クレジットカード決済 x セブンイレブン発券
    query = Order.query.filter(Order.canceled_at==None)
    query = query.join(Order.payment_delivery_pair)
    query = query.join(PaymentDeliveryMethodPair.payment_method)
    query = query.filter(PaymentMethod.payment_plugin_id==plugins.MULTICHECKOUT_PAYMENT_PLUGIN_ID)
    query = query.join(PaymentDeliveryMethodPair.delivery_method)
    query = query.filter(DeliveryMethod.delivery_plugin_id==plugins.SEJ_DELIVERY_PLUGIN_ID)
    # 1件の注文で7枚以上
    query = query.join(Order.ordered_products)
    query = query.join(OrderedProduct.ordered_product_items)
    query = query.group_by(Order.id).having(func.sum(OrderedProductItem.quantity) > 7)
    query = query.with_entities(Order.id)
    # 指定期間
    query = query.filter(period_from<=Order.created_at, Order.created_at<=period_to)
    orders = query.all()

    # 同一人物(user_idまたはメールアドレス)による同一公演の注文が2件以上存在
    if len(orders) > 0:
        query = Order.query.filter(Order.id.in_([o[0] for o in orders]))
        query = query.join(Order.shipping_address)
        query = query.group_by(Order.performance_id, func.ifnull(Order.user_id, ShippingAddress.email_1))
        query = query.having(func.count(Order.id) >= 2)
        orders = query.all()

    if len(orders) > 0:
        settings = registry.settings
        sender = settings['mail.message.sender']
        recipient = settings['mail.alert.recipient']
        subject = u'[alert] 不正予約'
        render_params = dict(orders=orders, period_from=period_from, period_to=period_to)
        html = render_to_response('altair.app.ticketing:templates/orders/_fraud_alert_mail.html', render_params, request=None)

        mailer = Mailer(settings)
        mailer.create_message(
            sender=sender,
            recipient=recipient,
            subject=subject,
            body='',
            html=html.text
        )
        try:
            mailer.send(sender, recipient.split(','))
            logging.info('sendmail success')
        except Exception:
            logging.warn('sendmail fail')

    logging.info('end detect_fraud batch')
