# -*- coding:utf-8 -*-
import logging
import argparse
import sqlahelper
from altair.sqlahelper import get_db_session
from pyramid.paster import bootstrap, setup_logging


def main():
    """
    座席指定の在庫の勘定チェック
    """
    logger = logging.getLogger(__name__)

    parser = argparse.ArgumentParser()
    parser.add_argument('config')
    args = parser.parse_args()

    setup_logging(args.config)
    env = bootstrap(args.config)
    request = env['request']
    session = get_db_session(request, 'standby')

    # 多重起動防止
    LOCK_NAME = "stock_quantity_mismatch_with_seat"
    LOCK_TIMEOUT = 10
    results = session.execute("select get_lock('{0}', {1})".format(LOCK_NAME, LOCK_TIMEOUT)).first()

    if results[0] == 0:
        logging.warn('lock timeout: already running process')
        return

    logger.info("Stock quantity mismatch with seat start")

    sql = "SELECT Stock.id, StockStatus.quantity - COUNT(DISTINCT Seat.id) AS diff \
    FROM Stock JOIN StockStatus ON StockStatus.stock_id = Stock.id \
    JOIN Seat ON Seat.stock_id = Stock.id JOIN SeatStatus ON SeatStatus.seat_id = Seat.id \
    WHERE Stock.deleted_at IS NULL AND StockStatus.deleted_at IS NULL \
    AND Seat.deleted_at IS NULL AND SeatStatus.deleted_at IS NULL \
    AND SeatStatus.status NOT IN (2, 3) \
    GROUP BY Stock.id HAVING diff <> 0"
    results = session.execute(sql)

    for result in results:
        msg = u"Stock quantity mismatch with seat Stock ID = {0}, Diff = {1}"
        logger.error(msg.format(result[0], result[1]))

    session.execute("select release_lock('{0}')".format(LOCK_NAME)).first()
    logger.info("Stock quantity mismatch with seat end")
