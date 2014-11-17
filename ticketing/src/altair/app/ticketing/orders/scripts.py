# -*- coding:utf-8 -*-

import os
import sys
from datetime import datetime, timedelta
import logging
import transaction
import argparse

from pyramid.paster import bootstrap, setup_logging   
from pyramid.renderers import render_to_response
from sqlalchemy import orm
from sqlalchemy.sql.expression import and_, not_, or_
from sqlalchemy.sql import func
import sqlahelper

from altair.app.ticketing.models import DBSession
from altair.app.ticketing.core.models import SeatStatus, SeatStatusEnum
from altair.app.ticketing.core.models import PaymentDeliveryMethodPair, PaymentMethod, DeliveryMethod, ShippingAddress, Mailer
from altair.app.ticketing.core.models import Organization, Refund, RefundStatusEnum
from altair.app.ticketing.orders.models import (
    Order,
    OrderedProduct,
    OrderedProductItem,
    OrderImportTask,
    ImportStatusEnum,
    )
from altair.app.ticketing.orders.importer import OrderImporter
from altair.app.ticketing.orders.mail import send_refund_complete_mail, send_refund_error_mail
from altair.app.ticketing.payments import plugins

def update_seat_status():
    _keep_to_vacant()

def _keep_to_vacant():
    ''' 座席ステータスがKeepのままの座席をVacantに戻す
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument('config')
    args = parser.parse_args()

    setup_logging(args.config)
    env = bootstrap(args.config)
    registry = env['registry']

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

    now = datetime.now()

    refunds = Refund.query.filter(Refund.status==RefundStatusEnum.Waiting.v).order_by(Refund.id).with_lockmode('update').all()
    for refund in refunds:
        refund.status = RefundStatusEnum.Refunding.v
        refund.save()
    transaction.commit()

    try:
        for refund in refunds:
            status = True
            error_message = []
            refund = DBSession.merge(refund)
            for order in refund.orders:
                order = DBSession.merge(order)
                logging.info('try to refund order (%s)' % order.id)
                if order.call_refund(request):
                    logging.info('refund success')
                    transaction.commit()
                else:
                    message = 'failed to refund order (%s)' % order.order_no
                    logging.error(message)
                    error_message.append(message)
                    transaction.abort()
                    status = False

            refund = DBSession.merge(refund)
            if status:
                refund.status = RefundStatusEnum.Refunded.v
                refund.save()
                send_refund_complete_mail(request, refund)
            else:
                send_refund_error_mail(request, refund, error_message)
            transaction.commit()
    except Exception as e:
        logging.error('failed to refund orders', exc_info=True)
        transaction.abort()

    from altair.app.ticketing.sej.refund import stage_refund_zip_files
    try:
        stage_refund_zip_files(registry, now)
    except:
        logging.error('failed to create refund zip files', exc_info=True)
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
    settings = registry.settings

    now = datetime.now()
    period_from = args.f if args.f else (now - timedelta(days=2)).strftime('%Y-%m-%d %H:%M')
    period_to = args.t if args.t else now.strftime('%Y-%m-%d %H:%M')

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
    query = query.join(Order.items)
    query = query.join(OrderedProduct.elements)
    query = query.group_by(Order.performance_id, func.ifnull(Order.user_id, ShippingAddress.email_1))
    query = query.having(or_(
        func.sum(OrderedProductItem.quantity) >= 8,
        func.sum(OrderedProductItem.price * OrderedProductItem.quantity) >= 100000
    ))
    # インナー予約は除く
    query = query.filter(not_(Order.channel.in_(Order.inner_channels())))

    # {{{ XXX: 当面のあいだ乃木坂認証用のユーザも除外 (refs #10114)
    from altair.app.ticketing.users.models import UserCredential
    nogizaka46_auth_identifier = settings.get('altair.nogizaka46_auth.username', '::nogizaka46::') # manner in nogizaka46/auth.py
    nogizaka46_auth_user_ids = UserCredential.query\
        .filter(UserCredential.auth_identifier==nogizaka46_auth_identifier)\
        .with_entities(UserCredential.user_id).subquery()
    query = query.filter(not_(Order.user_id.in_(nogizaka46_auth_user_ids)))
    # }}}

    query = query.with_entities(Order.organization_id, Order.performance_id, func.ifnull(Order.user_id, ShippingAddress.email_1))
    orders = query.all()

    # 該当した予約を予約者ごとに全て取得
    frauds = dict()
    if len(orders) > 0:
        for order in orders:
            query = Order.query.filter(Order.canceled_at==None)
            query = query.join(Order.shipping_address)
            query = query.filter(func.ifnull(Order.user_id, ShippingAddress.email_1)==order[2])
            query = query.filter(period_from<=Order.created_at, Order.created_at<=period_to)
            rows = query.all()
            # 同一人物(user_idまたはメールアドレス)による同一公演の注文が2件以上存在
            if len(rows) >= 2:
                organization_id = order[0]
                if not frauds.has_key(organization_id):
                    frauds[organization_id] = []
                frauds[organization_id].append(rows)
                for row in rows:
                    row.fraud_suspect = True
                    row.save()

    sender = settings['mail.message.sender']
    for organization_id, fraud_list in frauds.items():
        organization = Organization.filter_by(id=organization_id).one()
        recipient = u'dev@ticketstar.jp,' + organization.contact_email
        subject = u'[alert] 不正予約'
        render_params = dict(frauds=fraud_list, period_from=period_from, period_to=period_to)
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
    session_for_task = orm.session.Session(bind=sqlahelper.get_engine())
    tasks = session_for_task.query(OrderImportTask).filter(
        OrderImportTask.status == ImportStatusEnum.Waiting.v,
        OrderImportTask.deleted_at == None
    ).order_by(OrderImportTask.id).with_lockmode('update').all()
    for task in tasks:
        task.status = ImportStatusEnum.Importing.v
    session_for_task.commit()

    from .importer import initiate_import_task

    for task in tasks:
        initiate_import_task(request, task, session_for_task)

    logging.info('end import_orders batch')
