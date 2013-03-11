# -*- coding: utf-8 -*-
from pyramid.view import view_config
from cmsmobile.event.orderreview.forms import OrderReviewForm
from cmsmobile.core.helper import log_info

class ValidationFailure(Exception):
    pass

@view_config(route_name='order', renderer='cmsmobile:templates/orderreview/orderreview.mako')
def move_order(request):
    log_info("move_order", "start")
    form = OrderReviewForm()
    form.altair_orderreview_url.data = request.altair_orderreview_url
    form.getti_orderreview_url.data = request.getti_orderreview_url
    log_info("move_order", "end")
    return {'form':form}