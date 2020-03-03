# -*- coding:utf-8 -*-
import logging
import argparse
import sqlahelper
from pyramid.paster import bootstrap, setup_logging
from altair.sqlahelper import get_db_session


def main():
    """
    数受けの在庫において、在庫総数と注文、カート、残数が一致しているかチェックする。
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
    SUM(IFNULL(_order._qty, 0)) AS stock_ordered,
    SUM(IFNULL(_cart._qty, 0)) AS stock_carted,
    Performance.name AS performance_name
FROM Stock
JOIN Performance ON Performance.id = Stock.performance_id
JOIN StockStatus ON StockStatus.stock_id = Stock.id
JOIN StockType ON StockType.id = Stock.stock_type_id
JOIN ProductItem ON ProductItem.stock_id = Stock.id
LEFT JOIN (
    SELECT
        OrderedProductItem.product_item_id,
        SUM(OrderedProductItem.quantity) AS _qty
    FROM OrderedProductItem
    JOIN OrderedProduct ON OrderedProduct.id = OrderedProductItem.ordered_product_id
    JOIN `Order` ON `Order`.id = OrderedProduct.order_id
    WHERE 1
        AND OrderedProductItem.deleted_at IS NULL
        AND OrderedProduct.deleted_at IS NULL
        AND `Order`.deleted_at IS NULL
        AND `Order`.canceled_at IS NULL
        AND `Order`.released_at IS NULL
    GROUP BY OrderedProductItem.product_item_id
) AS _order ON _order.product_item_id = ProductItem.id
LEFT JOIN (
    SELECT
        CartedProductItem.product_item_id,
        SUM(CartedProductItem.quantity) AS _qty
    FROM CartedProductItem
    JOIN CartedProduct ON CartedProduct.id = CartedProductItem.carted_product_id
    JOIN Cart ON Cart.id = CartedProduct.cart_id
    WHERE 1
        AND CartedProductItem.deleted_at IS NULL
        AND CartedProductItem.finished_at IS NULL
        AND CartedProduct.deleted_at IS NULL
        AND CartedProduct.finished_at IS NULL
        AND Cart.deleted_at IS NULL
        AND Cart.finished_at IS NULL
    GROUP BY CartedProductItem.product_item_id
) AS _cart ON _cart.product_item_id = ProductItem.id
WHERE 1
    AND Stock.deleted_at IS NULL
    AND StockStatus.deleted_at IS NULL
    AND StockType.deleted_at IS NULL
    AND ProductItem.deleted_at IS NULL
    AND StockType.quantity_only = '1'
GROUP BY Stock.id
HAVING stock_total <> stock_rest + stock_ordered + stock_carted
"""
    results = session.execute(sql)

    for result in results:
        msg = u"Stock quantity mismatch for kazuuke: stock_id={0}, stock_total={1}, stock_rest={2}, stock_ordered={3}, stock_carted={4}, performance={5}"
        logger.error(msg.format(result[0], result[1], result[2], result[3], result[4], result[5]))

    session.execute("select release_lock('{0}')".format(LOCK_NAME)).first()
    logger.info("{} end".format(__name__))
