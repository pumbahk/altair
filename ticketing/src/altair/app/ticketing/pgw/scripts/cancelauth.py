# -*- coding:utf-8 -*-
import argparse
import logging

import sqlahelper
from altair.app.ticketing.pgw import models as m
from pyramid.paster import bootstrap, setup_logging

from ..api import cancel_or_refund

""" PGWオーソリキャンセルバッチ

"""

logger = logging.getLogger(__name__)


class Canceller(object):
    def __init__(self, request, now=None):
        self.request = request

    @staticmethod
    def get_cancel_auth_pgw_order_statuses():
        return m.PGWOrderStatus.query.filter(
            m.PGWOrderStatus.payment_status == m.PaymentStatusEnum.auth_cancel.v).all()

    def run(self):
        # 全ORG共通で、PGWOrderStatusが、オーソリ済（キャンセル対象）のものをキャンセルする
        # エラーが起きた場合は、そこで処理を止める
        for pgw_order_status in self.get_cancel_auth_pgw_order_statuses():

            try:
                logger.info("process pgw_order_status.payment_id = %s.", pgw_order_status.payment_id)
                cancel_or_refund(self.request, pgw_order_status.payment_id)
            except Exception as e:
                logging.exception('PGW cancel auth error occured: %s', e.message)
                return False
        return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('config')
    args = parser.parse_args()

    setup_logging(args.config)
    env = bootstrap(args.config)
    request = env['request']
    request.environ['PATH_INFO'] = "/pgw_cancelauth"
    logger.info("start offline as {request.url}".format(request=request))

    # 多重起動防止
    LOCK_NAME = 'pgw_cancelauth'
    LOCK_TIMEOUT = 10
    conn = sqlahelper.get_engine().connect()
    status = conn.scalar("select get_lock(%s,%s)", (LOCK_NAME, LOCK_TIMEOUT))
    if status == 1:
        Canceller(request).run()
        return
    else:
        logger.warn('lock timeout: already running process')
        return


if __name__ == '__main__':
    main()
