# -*- coding:utf-8 -*-
import logging
import argparse
import sqlahelper
from pyramid.paster import bootstrap, setup_logging
from altair.sqlahelper import get_db_session


def main():
    """
    数受けの在庫の勘定チェック
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
    LOCK_NAME = "stock_quantity_mismatch"
    LOCK_TIMEOUT = 10
    conn = sqlahelper.get_engine().connect()
    status = conn.scalar("select get_lock(%s,%s)", (LOCK_NAME, LOCK_TIMEOUT))

    if status != 1:
        logging.warn('lock timeout: already running process')
        return

    logger.info("Stock quantity mismatch start")

    sql = "SELECT Stock.id, StockStatus.quantity - COUNT(DISTINCT Seat.id) AS diff \
    FROM Stock JOIN StockStatus ON StockStatus.stock_id = Stock.id \
    JOIN Seat ON Seat.stock_id = Stock.id JOIN SeatStatus ON SeatStatus.seat_id = Seat.id \
    WHERE Stock.deleted_at IS NULL AND StockStatus.deleted_at IS NULL \
    AND Seat.deleted_at IS NULL AND SeatStatus.deleted_at IS NULL \
    AND SeatStatus.status NOT IN (2, 3) \
    GROUP BY Stock.id HAVING diff <> 0"
    results = session.execute(sql)

    for result in results:
        msg = "Stock quantity mismatch kazuuke Stock ID = {0}, Diff = {1}"
        logger.error(msg.format(result[0], result[1]))

    logger.info("Stock quantity mismatch end")
