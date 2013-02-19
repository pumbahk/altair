# -*- coding:utf-8 -*-
# see. __init__.py

def performance_describe_panel(context, request, performance):
    salessegments = performance.salessegments
    return dict(performance=performance, 
                sales_segments=salessegments)
