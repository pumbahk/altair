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
from ..domainmodel import TicketData

@view_config(route_name="refresh.order", permission="sales_counter", renderer="json", request_method="POST")
def refresh_order_with_signed(context, request):
    access_log("*refresh order with signed", context.identity)
    if not "qrsigned" in request.json_body:
        raise HTTPBadRequest(u"E@:引数が足りません")

    ticket_data = TicketData(request, context.operator)
    try:
        try:
            signed = request.json_body["qrsigned"]
            order, history = ticket_data.get_order_and_history_from_signed(signed)
        except TypeError:
            logger.warn("*qr ticketdata: history not found: json=%s", request.json_body)
            raise HTTPBadRequest(u"E@:データが見つかりません。不正なQRコードの可能性があります!")

        now = get_now(request)
        order.printed_at = None
        for ordered_product in order.ordered_products:
            for ordered_product_item in ordered_product.ordered_product_items:
                for token in ordered_product_item.tokens:
                    token.refreshed_at = now
        return {"refreshed_at": str(now), "order_no": order.order_no}
    except KeyError:
        logger.warn("*qr ticketdata: KeyError: json=%s", request.json_body)
        raise HTTPBadRequest(u"E@:データが見つかりません。不正なQRコードの可能性があります!!")
