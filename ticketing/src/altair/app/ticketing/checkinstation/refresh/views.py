# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPBadRequest
from altair.now import get_now

@view_config(route_name="refresh.token", permission="sales_counter", renderer="json")
def refresh_token(context, request):
    pass

from ..views import access_log
from ..domainmodel import OrderData


@view_config(route_name="refresh.order", permission="sales_counter", renderer="json", request_method="POST")
def refresh_order(context, request):
    access_log("*refresh order", context.identity)
    if not "order_no" in request.json_body:
        raise HTTPBadRequest(u"E@:引数が足りません")

    now = get_now(request)
    order_no = request.json_body["order_no"]
    order = OrderData(request, context.operator).get_order_from_order_no(order_no)

    order.printed_at = None
    for ordered_product in order.ordered_products:
        for ordered_product_item in ordered_product.ordered_product_items:
            for token in ordered_product_item.tokens:
                token.refreshed_at = now
    return {"refreshed_at": str(now), "order_no": order_no}
