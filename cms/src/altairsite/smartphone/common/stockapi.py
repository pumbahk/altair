# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)
from altaircms.plugins.extra.api import get_stock_data_api
from altaircms.plugins.extra.stockstatus import CalcResult

def get_stockstatus(request, salessegment, event, status_impl):
    cache_name = "_stock_data"
    data = getattr(request, cache_name, None)
    if data:
        return data
    data = get_stock_data_api(request).fetch_stock_status(request, event, salessegment)
    result = _get_stockstatus_summary(CalcResult(rawdata=data, status_impl=status_impl))
    setattr(request, cache_name, result)
    return result

def _get_stockstatus_summary(data):
    for stock in data.rawdata["stocks"]:
        data.add_stock(stock)
    return data