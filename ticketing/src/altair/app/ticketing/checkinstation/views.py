# -*- coding:utf-8 -*-
from pyramid.view import view_defaults, view_config
import logging
logger = logging.getLogger(__name__)
from altair.now import get_now
from pyramid.httpexceptions import HTTPBadRequest

class BaseView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

def access_log(prefix, identity):
    if identity:
        logger.info("{prefix} CheckinIdentity.secret=%s, operator.id=%s".format(prefix=prefix), identity.secret, identity.operator_id)
    else:
        logger.info("{prefix} CheckinIdentity not found".format(prefix=prefix))

## status = {ok, ng}

@view_defaults(route_name="login.status", request_method="GET", renderer="json")
class LoginInfoView(BaseView):
    ## permissionでdispatchできなかったっけ？
    @view_config(permission="everybady")
    def for_guest_user_view(self):
        logger.info("*login status no login user")
        return {"login": False}


    @view_config(permission="sales_counter")
    def for_login_user_view(self):
        access_log("*login status start", self.context.identity)
        operator = self.context.operator
        if not operator:
            return {"login": False}
        return {"login": True,
                "loginuser": {"type": u"login",
                              "id": unicode(operator.id),
                              "name": operator.name},
                "organization": {"id": unicode(operator.organization_id)}}


## EventSelect
from .domainmodel import ChoosablePerformance
from .todict import dict_from_performance

@view_config(route_name="performance.list", request_method="GET", renderer="json",  permission="sales_counter")
def performance_list(context, request):
    access_log("*performance list", context.identity)

    ev = ChoosablePerformance(request, context.operator)
    now = get_now(request)
    qs = ev.choosable_performance_query(now).all()
    return {"performances": [dict_from_performance(e) for e in qs]}

## 大体QRAppのviewの利用しているものをそのまま使う。
## signed -> qrdata. 公演名やチケットの購入情報など
from .domainmodel import (
    TicketData, 
)
from .todict import (
    data_dict_from_order_and_history,
    verified_data_dict_from_secret,
    TokenStatusDictBuilder, 
)

@view_config(route_name="qr.ticketdata", permission="sales_counter", renderer="json")
def ticket_data_from_signed_string(context, request):
    access_log("*qr ticketdata", context.identity)
    if not "qrsigned" in request.json_body:
        raise HTTPBadRequest(u"引数が足りません")

    ticket_data = TicketData(request, context.operator)
    try:
        order, history = ticket_data.get_order_and_history_from_signed(request.json_body["qrsigned"])

        data = data_dict_from_order_and_history(order, history)
        ## 認証用の文字列追加
        data.update(verified_data_dict_from_secret(context.identity.secret))
        ## 印刷済み、キャンセル済みなどのステータス付加
        data.update(TokenStatusDictBuilder(order, history).build())
        return data
    except KeyError:
        logger.warn("*qr ticketdata: %s", request.json_body)
        raise HTTPBadRequest(u"不正な入力が渡されました")


## token -> [svg] #one
from .domainmodel import ItemTokenData
from .domainmodel import SVGDataSource

@view_config(route_name="qr.svgsource.one", permission="sales_counter", renderer="json")
def svgsource_one_from_token(context, request):
    access_log("*qr.svg.one", context.identity)
    if not "ordered_product_item_token_id" in request.json_body:
        raise HTTPBadRequest(u"引数が足りません")

    token_data = ItemTokenData(request, context.operator)
    svg_source = SVGDataSource(request)

    token = token_data.get_item_token_from_id(request.json_body["ordered_product_item_token_id"])
    datalist = svg_source.data_list_for_one(token)
    return {"datalist": datalist}

## token -> [svg] #all

@view_config(route_name="qr.svgsource.all", permission="sales_counter", renderer="json")
def svgsource_all_from_order_no(context, request):
    access_log("*qr.svg.all", context.identity)
    if not "order_no" in request.json_body:
        raise HTTPBadRequest(u"引数が足りません")
    order_no = request.json_body["order_no"]

    token_data = ItemTokenData(request, context.operator)
    svg_source = SVGDataSource(request)

    token_list = token_data.get_item_token_list_from_order_no(request.json_body["order_no"])
    datalist = svg_source.data_list_for_all(order_no, token_list)
    return {"datalist": datalist}
