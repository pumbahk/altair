# -*- coding:utf-8 -*-

from datetime import datetime as dt
from urlparse import urlparse
import logging

logger = logging.getLogger()

def grep_prfms_in_sales(performances):
    prfms_in_sales = []
    now = dt.now()
    for prfm in performances:
        for s in prfm.sales:
            if s.start_on <= now <= s.end_on:
                prfms_in_sales.append(prfm)

    return prfms_in_sales


def is_performance_on_sale(performance, dt):
    if performance is not None:
        for s in performance.sales:
            if s.start_on <= dt <= s.end_on:
                return True
    return False


def get_lot_id_from_url(url):
    lot_id = None
    if url is None:
        return None
    try:
        path = urlparse(url).path
        lot_id = path.split('/entry/')[1]
    except:
        logger.warn("warn occured while getting lot_id from url: %s", url)
    return lot_id