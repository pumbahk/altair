# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPBadRequest
from altair.now import get_now
from altair.app.ticketing.qr.builder import InvalidSignedString

@view_config(route_name="refresh.token", permission="sales_counter", renderer="json")
def refresh_token(context, request):
    pass

from ..views import access_log
from ..domainmodel import TicketData
from ..domainmodel import OrderData

@view_config(route_name="refresh.order", permission="sales_counter", renderer="json", request_method="POST")
def refresh_order_with_signed(context, request):
    # QRに紐付いた全てのチケットを未発券にする
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
        except InvalidSignedString as e:
            logger.error(repr(e))
            raise HTTPBadRequest(u"E@:データが読み取れませんでした。QRコードの読み取りに失敗した可能性があります!")

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

@view_config(route_name="refresh.order.qr", permission="sales_counter", renderer="json", request_method="POST")
def refresh_order_with_signed_qr(context, request):
    # QRに対応したチケットのみ未発券にする
    import ipdb;ipdb.set_trace()
    access_log("*refresh order with signed qr", context.identity)
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
        except InvalidSignedString as e:
            logger.error(repr(e))
            raise HTTPBadRequest(u"E@:データが読み取れませんでした。QRコードの読み取りに失敗した可能性があります!")

        now = get_now(request)
        order.printed_at = None
        for ordered_product in order.ordered_products:
            for ordered_product_item in ordered_product.ordered_product_items:
                for token in ordered_product_item.tokens:
                    if token.id == history.item_token_id:
                        token.refreshed_at = now
        return {"refreshed_at": str(now), "order_no": order.order_no}
    except KeyError:
        logger.warn("*qr ticketdata: KeyError: json=%s", request.json_body)
        raise HTTPBadRequest(u"E@:データが見つかりません。不正なQRコードの可能性があります!!")



@view_config(route_name="refresh.order2", permission="sales_counter", renderer="json", request_method="POST")
def refresh_order_with_orderno(context, request):
    access_log("*refresh order with signed", context.identity)
    if not "order_no" in request.json_body:
        raise HTTPBadRequest(u"E@:引数が足りません")
    if not "tel" in request.json_body:
        raise HTTPBadRequest(u"E@:引数が足りません")

    order_no = request.json_body["order_no"]
    tel = request.json_body["tel"].strip()

    now = get_now(request)


    order = OrderData(request, context.operator).get_order_from_order_no(order_no)

    if not (order.shipping_address is None or order.shipping_address.tel_1 == tel or order.shipping_address.tel_2 == tel):
        logger.warn("*orderno ticketdata: invalid paramaters json=%s", request.json_body)
        raise HTTPBadRequest(u"E@:データが見つかりません。受付番号か電話番号に誤りがあります")

    order.printed_at = None
    for ordered_product in order.ordered_products:
        for ordered_product_item in ordered_product.ordered_product_items:
            for token in ordered_product_item.tokens:
                token.refreshed_at = now
    return {"refreshed_at": str(now), "order_no": order.order_no}
