# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)
from altaircms.plugins.interfaces import IExternalAPI

from .stockstatus import StockDataAPI
from .stockstatus import CalcResult
"""
status :: performance -> stock-status
"""
dummy_data = {"stocks": []}
def get_stockstatus_summary(request, event, status_impl, cache_off=False):
    cache_name = "_stock_data"
    data = getattr(request, cache_name, None)
    if data and not cache_off:
        return data
    data = get_stock_data_api(request).fetch_stock_status(request, event)
    result = _get_stockstatus_summary(request, CalcResult(rawdata=data, status_impl=status_impl))
    setattr(request, cache_name, result)
    return result

def _get_stockstatus_summary(request, data):
    for stock in data.rawdata["stocks"]:
        data.add_stock(stock)
    return data

def get_stock_data_api(request):
    return request.registry.getUtility(IExternalAPI, name=StockDataAPI.__name__)
