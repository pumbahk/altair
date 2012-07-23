# -*- coding:utf-8 -*-

"""
在庫数管理
"""

from ticketing.core.models import *

class NotEnoughStockException(Exception):
    """ 必要な在庫数がない場合 """

class Stocker(object):
    def __init__(self, request):
        self.request = request


    def take_stock(self, stock_requires):
        """
        :param stock_requires: list of tuple (stock_id, quantity)

        """
        stock_ids = [s[0] for s in stock_requires]
        require_quantities = dict(stock_requires)
        statuses = StockStatus.query.filter(StockStatus.stock_id.in_(stock_ids)).with_lockmode('update').all()
        
        # 在庫数を確認、確保
        for status in statuses:
            quantity = require_quantities[status.stock_id]
            if status.quantity < quantity:
                raise NotEnoughStockException
            status.quantity -= quantity
        return statuses
