# -*- coding:utf-8 -*-

import os
import sys
from datetime import datetime, timedelta
import logging
import transaction
import argparse

from pyramid.paster import bootstrap, setup_logging   
from sqlalchemy import and_
from sqlalchemy.sql.expression import not_
import sqlahelper

from ticketing.core.models import DBSession, SeatStatus, SeatStatusEnum, Order

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
        expire_time = datetime.now() - timedelta(minutes=expire_minute)
        logging.info('expire_time : %s (now - %s minute)' % (expire_time, expire_minute))

        seats = SeatStatus.filter_by(status=int(SeatStatusEnum.Keep))\
                          .filter(SeatStatus.updated_at < expire_time)\
                          .with_entities(SeatStatus.seat_id).all()
        logging.info('target seat_id : %s' % seats)

        if seats:
            query = SeatStatus.__table__.update().values(
                {'status': int(SeatStatusEnum.Vacant)}
            ).where(and_(SeatStatus.status==int(SeatStatusEnum.Keep), SeatStatus.updated_at < expire_time))
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

    logging.info('start refund_order batch')

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

    logging.info('end refund_order batch')
