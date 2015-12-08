# -*- coding:utf-8 -*-

from datetime import datetime as dt

def grep_prfms_in_sales(performances):
    prfms_in_sales = []
    now = dt.now()
    for prfm in performances:
        for s in prfm.sales:
            if s.start_on <= now <= s.end_on:
                prfms_in_sales.append(prfm)

    return prfms_in_sales