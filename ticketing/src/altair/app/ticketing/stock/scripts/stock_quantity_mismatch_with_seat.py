# -*- coding:utf-8 -*-
import logging
import argparse
import sqlahelper
from pyramid.paster import bootstrap, setup_logging
import pymysql


def main():
    """
    座席指定の在庫の勘定チェック
    """
    logger = logging.getLogger(__name__)

    parser = argparse.ArgumentParser()
    parser.add_argument('config')
    args = parser.parse_args()

    setup_logging(args.config)
    bootstrap(args.config)

    logger.info("Stock quantity mismatch with seat start")

    url = sqlahelper.get_engine("standby").url
    client = pymysql.connect(host=url.host, db=url.database, user=url.username, passwd=url.password, charset='utf8')

    cur = client.cursor()

    sql = "SELECT A.stock_id, A.total, A.rest, IFNULL(A.ordered, 0), IFNULL(B.in_cart, 0) \
    FROM ( \
    SELECT s.id AS stock_id, s.quantity AS total, ss.quantity AS rest, SUM(opi.quantity) AS ordered \
    FROM Stock s, StockStatus ss, Performance p, StockType st, ProductItem pi \
    LEFT OUTER JOIN OrderedProductItem opi ON pi.id = opi.product_item_id \
    LEFT OUTER JOIN OrderedProduct op ON opi.ordered_product_id = op.id \
    LEFT OUTER JOIN ticketing.Order o ON op.order_id = o.id \
    WHERE s.id = ss.stock_id AND s.performance_id = p.id AND s.stock_type_id = st.id AND st.quantity_only = 1 \
    AND s.id = pi.stock_id AND pi.deleted_at IS NULL AND o.deleted_at IS NULL AND op.deleted_at IS NULL AND opi.deleted_at IS NULL \
    AND o.canceled_at IS NULL AND o.released_at IS NULL AND o.id IS NOT NULL \
    GROUP BY s.id \
    ) A LEFT OUTER JOIN \
    ( \
    SELECT s.id AS stock_id, IFNULL(SUM(cpi.quantity), 0) AS in_cart \
    FROM Stock s, StockStatus ss, Performance p, StockType st, ProductItem pi \
    LEFT OUTER JOIN CartedProductItem cpi ON pi.id = cpi.product_item_id \
    LEFT OUTER JOIN CartedProduct cp ON cpi.carted_product_id = cp.id AND cp.cart_id IS NOT NULL \
    LEFT OUTER JOIN Cart c ON cp.cart_id = c.id \
    WHERE s.id = ss.stock_id AND s.performance_id = p.id AND s.stock_type_id = st.id AND st.quantity_only = 1 \
    AND s.id = pi.stock_id AND pi.deleted_at IS NULL \
    AND c.order_id IS NULL AND c.deleted_at IS NULL AND c.id IS NOT NULL AND cp.id IS NOT NULL AND cpi.id IS NOT NULL \
    AND c.finished_at IS NULL AND cp.finished_at IS NULL AND cpi.finished_at IS NULL \
    GROUP BY s.id \
    ) B ON A.stock_id = B.stock_id \
    WHERE A.total - A.rest - IFNULL(A.ordered, 0) - IFNULL(B.in_cart, 0) <> 0"

    cur.execute(sql)
    data = cur.fetchall()

    for datum in data:
        msg = "Stock quantity mismatch with seat Stock ID = {0}, Total = {1}, Rest = {2}"
        logger.error(msg.format(datum[0], datum[1], datum[2]))

    logger.info("Stock quantity mismatch with seat end")
