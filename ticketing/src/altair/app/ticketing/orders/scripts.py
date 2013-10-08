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
from sqlalchemy.sql.expression import not_, or_
from sqlalchemy.sql import func
import sqlahelper

from altair.app.ticketing.core.models import DBSession, SeatStatus, SeatStatusEnum, Order, OrderedProduct, OrderedProductItem
from altair.app.ticketing.core.models import PaymentDeliveryMethodPair, PaymentMethod, DeliveryMethod, ShippingAddress, Mailer
from altair.app.ticketing.core.models import OrderImportTask, ImportStatusEnum
from altair.app.ticketing.orders.importer import OrderImporter
from altair.app.ticketing.payments import plugins
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
    period_from = args.f if args.f else (now - timedelta(days=2)).strftime('%Y-%m-%d %H:%M')
    period_to = args.t if args.t else now.strftime('%Y-%m-%d %H:%M')
    frauds = []

    logging.info('start detect_fraud batch')

    # クレジットカード決済 x セブンイレブン発券
    query = Order.query.filter(Order.canceled_at==None, Order.fraud_suspect==None)
    query = query.join(Order.payment_delivery_pair)
    query = query.join(PaymentDeliveryMethodPair.payment_method)
    query = query.filter(PaymentMethod.payment_plugin_id==plugins.MULTICHECKOUT_PAYMENT_PLUGIN_ID)
    query = query.join(PaymentDeliveryMethodPair.delivery_method)
    query = query.filter(DeliveryMethod.delivery_plugin_id==plugins.SEJ_DELIVERY_PLUGIN_ID)
    # 指定期間
    query = query.filter(period_from<=Order.created_at, Order.created_at<=period_to)
    # 同一人物(user_idまたはメールアドレス)による同一公演の予約枚数が8枚以上、または合計金額が10万以上
    query = query.join(Order.shipping_address)
    query = query.join(Order.ordered_products)
    query = query.join(OrderedProduct.ordered_product_items)
    query = query.group_by(Order.performance_id, func.ifnull(Order.user_id, ShippingAddress.email_1))
    query = query.having(or_(
        func.sum(OrderedProductItem.quantity) >= 8,
        func.sum(OrderedProductItem.price * OrderedProductItem.quantity) >= 100000
    ))
    query = query.with_entities(Order.performance_id, func.ifnull(Order.user_id, ShippingAddress.email_1))
    orders = query.all()

    # 該当した予約を予約者ごとに全て取得
    if len(orders) > 0:
        for order in orders:
            query = Order.query.filter(Order.canceled_at==None)
            query = query.join(Order.shipping_address)
            query = query.filter(func.ifnull(Order.user_id, ShippingAddress.email_1)==order[1])
            query = query.filter(period_from<=Order.created_at, Order.created_at<=period_to)
            rows = query.all()
            # 同一人物(user_idまたはメールアドレス)による同一公演の注文が2件以上存在
            if len(rows) >= 2:
                frauds.append(rows)
                for row in rows:
                    row.fraud_suspect = True
                    row.save()

    if len(frauds) > 0:
        settings = registry.settings
        sender = settings['mail.message.sender']
        recipient = 'dev@ticketstar.jp,op@ticketstar.jp'
        subject = u'[alert] 不正予約'
        render_params = dict(frauds=frauds, period_from=period_from, period_to=period_to)
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

    transaction.commit()
    logging.info('end detect_fraud batch')


def import_orders():
    ''' 予約の一括登録
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument('config')
    args = parser.parse_args()

    setup_logging(args.config)
    env = bootstrap(args.config)

    request = env['request']
    request.browserid = u''

    # 多重起動防止
    LOCK_NAME = import_orders.__name__
    LOCK_TIMEOUT = 10
    conn = sqlahelper.get_engine().connect()
    status = conn.scalar("select get_lock(%s,%s)", (LOCK_NAME, LOCK_TIMEOUT))
    if status != 1:
        logging.warn('lock timeout: already running process')
        return

    logging.info('start import_orders batch')

    tasks = OrderImportTask.query.filter(
        OrderImportTask.status == ImportStatusEnum.Waiting.v[0]
    ).order_by(OrderImportTask.id).all()

    for task in tasks:
        try:
            task = DBSession.merge(task)
            logging.info('order_import_task(%s) importing..' % task.id)
            importer = OrderImporter.load_task(task)
            importer.execute()
            transaction.commit()
        except Exception, e:
            transaction.abort()
            logging.error('orders import error: %s' % e, exc_info=sys.exc_info())

    logging.info('end import_orders batch')
