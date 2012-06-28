# -*- coding:utf-8 -*-
from pyramid.view import view_config
from . import api
from markupsafe import Markup

def table_headers(headers):
    return Markup(u"<th>%s</th>" % u"</th></th>".join(headers)) 

@view_config(name="describe_pageset", renderer="altaircms:templates/event/viewlet/pagesets.mako")
def describe_pageset(request):
    event = api.get_event(request)
    pagesets = api.get_pagesets(request)
    return {
        "headers": table_headers([u"ページセット", u"ページ", u"現在表示状況", u"公開開始", u"公開終了", u"作成日時"]), 
        "event": event, 
        "pagesets": pagesets
        }

@view_config(name="describe_performance", renderer="altaircms:templates/event/viewlet/performances.mako")
def describe_performance(request):
    performances = api.get_performances(request)
    return {
        "headers": table_headers([u"",u"公演名",u"バックエンドID",u"公演日時",u"場所",u"pc購入URL",u"mobile購入URL"]), 
        "performances": performances
        }

@view_config(name="describe_sale", renderer="altaircms:templates/event/viewlet/sales.mako")
def describe_sale(request):
    sales = api.get_sales(request)
    return {
        "headers": table_headers([u"",u"名前",u"販売条件",u"適用期間",u"券種",u"席種",u"価格"]), 
        "sales": sales
        }



