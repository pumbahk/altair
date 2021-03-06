# -*- coding: utf-8 -*-
from altairsite.config import mobile_site_view_config
from altairsite.mobile.event.orderreview.forms import OrderReviewForm
from altairsite.mobile.core.helper import log_info
from altairsite.separation import selectable_renderer

@mobile_site_view_config(route_name='order', request_type="altair.mobile.interfaces.IMobileRequest"
    , renderer=selectable_renderer('altairsite.mobile:templates/%(prefix)s/orderreview/orderreview.mako'))
def move_order(request):
    log_info("move_order", "start")
    form = OrderReviewForm()
    form.altair_orderreview_url.data = request.altair_orderreview_url
    form.getti_orderreview_url.data = request.getti_orderreview_url
    form.lots_orderreview_url.data = request.lots_orderreview_url
    log_info("move_order", "end")
    return {'form':form}
