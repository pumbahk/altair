# -*- coding:utf-8 -*-

"""
在庫数管理
"""
import logging
import itertools
from ticketing.core.models import *

logger = logging.getLogger(__name__)

class NotEnoughStockException(Exception):
    """ 必要な在庫数がない場合 """

class Stocker(object):
    def __init__(self, request):
        self.request = request

    # TODO: 在庫オブジェクトの取得内容を確認。必要なproductの分がすべて取得できているか？
    def take_stock(self, performance_id, product_requires):
        """
        :param product_requires: list of tuple (product_id, quantity)

        """

        stock_requires = self.quantity_for_stock_id(performance_id, product_requires)
        logger.debug("stock requires %s" % stock_requires)
        return self._take_stock(stock_requires)


    def _take_stock(self, stock_requires):
        """
        :param stock_requires: list of tuple (stock_id, quantity)
        :return: list of StockStatus

        """
        stock_ids = [s[0] for s in stock_requires]
        require_quantities = dict(stock_requires)
        statuses = StockStatus.query.filter(StockStatus.stock_id.in_(stock_ids)).with_lockmode('update').all()
        
        results = []
        # 在庫数を確認、確保
        for status in statuses:
            quantity = require_quantities[status.stock_id]
            if status.quantity < quantity:
                raise NotEnoughStockException
            status.quantity -= quantity
            results.append((status, quantity))
        return results

    def _convert_order_product_items(self, performance_id, ordered_products):
        """ 選択したProductからProductItemと個数の組に展開する
        :param ordered_products: list of (product, quantity)
        :return: iter of (product_item_id, quantity)
        """
        for product, quantity in ordered_products:
            for product_item in DBSession.query(ProductItem).filter(
                        ProductItem.product_id==product.id).filter(
                        ProductItem.performance_id==performance_id).all():
                yield (product_item, quantity)

    def quantity_for_stock_id(self, performance_id, ordered_products):
        """ Productと個数の組から、stock_id, 個数の組に集約する
        :param ordered_product: iter of (product, quantity)

        """

        logger.debug("ordered products: %s" % ordered_products)
        ordered_product_items = self._convert_order_product_items(performance_id, ordered_products=ordered_products)
        ordered_product_items = list(ordered_product_items)
        logger.debug("ordered product items: %s" % ordered_product_items)
        q = sorted(ordered_product_items, key=lambda x: x[0].stock_id)
        q = itertools.groupby(q, key=lambda x: x[0].stock_id)
        return [(stock_id, sum(quantity for _, quantity in ordered_items)) for stock_id, ordered_items in q]

