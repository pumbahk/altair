# -*- coding:utf-8 -*-


class MismatchSeatInCartException(Exception):
    """ カートが掴んだ席と一致しない場合に発生する """
    pass


class NoStockStatusException(Exception):
    """ StockStatusが存在しない場合に発生する """
    pass
