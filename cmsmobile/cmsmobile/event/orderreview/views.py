# -*- coding: utf-8 -*-
from pyramid.view import view_config
from cmsmobile.event.orderreview.forms import OrderReviewForm

class ValidationFailure(Exception):
    pass

@view_config(route_name='order', renderer='cmsmobile:templates/orderreview/orderreview.mako')
def move_order(request):
    form = OrderReviewForm()
    form.altair_orderreview_url.data = request.altair_orderreview_url
    form.getti_orderreview_url.data = request.getti_orderreview_url
    return {'form':form}