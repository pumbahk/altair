# -*- coding:utf-8 -*-
import logging
import argparse
import sqlahelper
from pyramid.paster import bootstrap, setup_logging
from altair.sqlahelper import get_db_session


def main():
    """
    座席がある在庫で、在庫総数と座席総数、在庫残数と座席残数がそれぞれ一致しているかチェックする。
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
SELECT SQL_NO_CACHE
    Stock.id AS stock_id,
    Stock.quantity AS stock_total,
    StockStatus.quantity AS stock_rest,
    COUNT(DISTINCT Seat.id) AS seat_total,
    SUM(SeatStatus.status NOT IN (2, 3)) AS seat_rest,
    Performance.name AS performance_name
FROM Stock
JOIN Performance ON Performance.id = Stock.performance_id
JOIN StockStatus ON StockStatus.stock_id = Stock.id
JOIN Seat ON Seat.stock_id = Stock.id
JOIN SeatStatus ON SeatStatus.seat_id = Seat.id
WHERE 1
    AND Stock.deleted_at IS NULL
    AND StockStatus.deleted_at IS NULL
    AND Seat.deleted_at IS NULL
    AND SeatStatus.deleted_at IS NULL
GROUP BY Stock.id
HAVING stock_total <> seat_total OR stock_rest <> seat_rest
"""
    results = session.execute(sql)

    for result in results:
        msg = u"Stock quantity mismatch for seat: stock_id={0}, stock_total={1}, stock_rest={2}, seat_total={3}, seat_rest={4}, performance={5}"
        logger.error(msg.format(result[0], result[1], result[2], result[3], result[4], result[5]))

    session.execute("select release_lock('{0}')".format(LOCK_NAME)).first()
    logger.info("{} end".format(__name__))
