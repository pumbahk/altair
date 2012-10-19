# -*- coding:utf-8 -*-
import os
import sys
from datetime import datetime, timedelta
import logging

from pyramid.paster import bootstrap
from sqlalchemy import and_
import sqlahelper

from ticketing.core.models import DBSession, SeatStatus, SeatStatusEnum

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
