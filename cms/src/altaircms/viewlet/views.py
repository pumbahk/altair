# -*- coding:utf-8 -*-
from pyramid.view import view_config
from . import api
from markupsafe import Markup

def table_headers(headers):
    return Markup(u"<th>%s</th>" % u"</th></th>".join(headers)) 

@view_config(name="pageset_from_event", renderer="altaircms:templates/event/viewlet/pagesets.mako")
def describe_pageset(request):
    event = api.get_event(request)
    return {
        "headers": table_headers([u"ページセット", u"ページ", u"現在表示状況", u"公開開始", u"公開終了", u"作成日時"]), 
        "event": event, 
        "pagesets": event.pagesets
        }

@view_config(name="performance_from_event", renderer="altaircms:templates/event/viewlet/performances.mako")
def describe_performance(request):
    event = api.get_event(request)
    return {
        "headers": table_headers([u"",u"公演名",u"バックエンドID",u"公演日時",u"場所",u"pc購入URL",u"mobile購入URL"]), 
        "event": event, 
        "performances": event.performances
        }

@view_config(name="sale_from_event", renderer="altaircms:templates/event/viewlet/sales.mako")
def describe_sale(request):
    event = api.get_event(request)
    return {
        "headers": table_headers([u"",u"名前",u"販売条件",u"適用期間",u"券種",u"席種",u"価格"]), 
        "event": event, 
        "sales": event.sales
        }



