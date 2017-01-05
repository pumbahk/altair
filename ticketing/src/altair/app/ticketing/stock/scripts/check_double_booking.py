# -*- coding:utf-8 -*-
import logging
import argparse
import sqlahelper
from pyramid.paster import bootstrap, setup_logging
from altair.sqlahelper import get_db_session


def main():
    """
    ダブルブッキングとなる予約があるかチェックする。
    """
    logger = logging.getLogger(__name__)

    parser = argparse.ArgumentParser()
    parser.add_argument('config')
    args = parser.parse_args()

    setup_logging(args.config)
    env = bootstrap(args.config)
    request = env['request']
    session = get_db_session(request, 'standby')

    LOCK_NAME = __name__.split('.')[-1]
    LOCK_TIMEOUT = 10
    results = session.execute("select get_lock('{0}', {1})".format(LOCK_NAME, LOCK_TIMEOUT)).first()

    if results[0] == 0:
        logging.warn('lock timeout: already running process')
        return

    logger.info("{} start".format(__name__))

    sql = """\
SELECT
    seat_id,
    GROUP_CONCAT(DISTINCT order_no ORDER BY order_no)
FROM ticketing.Order AS o
JOIN OrderedProduct AS op ON op.order_id = o.id
JOIN OrderedProductItem AS opi ON opi.ordered_product_id = op.id
JOIN OrderedProductItemToken AS opit ON opit.ordered_product_item_id = opi.id
WHERE 1
    AND o.canceled_at IS NULL
    AND o.deleted_at IS NULL
    AND o.refunded_at IS NULL
    AND op.deleted_at IS NULL
    AND opi.deleted_at IS NULL
    AND opit.deleted_at IS NULL
    AND opit.seat_id IS NOT NULL
GROUP BY seat_id
HAVING COUNT(DISTINCT order_no) > 1
"""
    results = session.execute(sql)

    for result in results:
        msg = u"Double Booking: seat_id={0}, order_no={1}"
        logger.error(msg.format(result[0], result[1]))

    session.execute("select release_lock('{0}')".format(LOCK_NAME)).first()
    logger.info("{} end".format(__name__))
