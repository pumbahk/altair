# -*- coding:utf-8 -*-
from pyramid.view import view_config
from . import api
from markupsafe import Markup
from ..slackoff import mappers as sm
from ..slackoff import forms as sf

def table_headers(headers):
    return Markup(u"<th>%s</th>" % u"</th></th>".join(headers)) 

@view_config(name="describe_pageset", renderer="altaircms:templates/event/viewlet/pagesets.mako")
def describe_pageset(request):
    event = api.get_event(request)
    pagesets = api.get_pagesets(request)
    return {
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


@view_config(name="describe_hotword", renderer="altaircms:templates/page/viewlet/hotwords.mako")
def describe_hotword(request):
    hotwords = api.get_hotwords(request)
    display_fields = sf.HotWordForm.__display_fields__
    labels = [getattr(sf.HotWordForm, k).kwargs["label"] for k in display_fields]
    return {
        "hotwords": hotwords, 
        "mapper": sm.hotword_mapper, 
        "display_fields": display_fields, 
        "labels": labels
        }

@view_config(name="describe_accesskey", renderer="altaircms:templates/page/viewlet/accesskeys.mako")
def describe_accesskey(request):
    page = api.get_page(request)
    accesskeys = api.get_accesskeys(request)
    return {
        "page": page, 
        "accesskeys": accesskeys, 
        }

@view_config(name="describe_pagetag", renderer="altaircms:templates/page/viewlet/tags.mako")
def describe_pagetag(request):
    page = api.get_page(request)
    pagetags = api.get_tags(request)
    public_tags = []
    private_tags = []
    for tag in pagetags:
        if tag.publicp:
            public_tags.append(tag)
        else:
            private_tags.append(tag)

    return {
        "headers": table_headers([u"タグの種類",u"",u"ラベル",u"作成日時",u"更新日時"]), 
        "page": page, 
        "public_tags": public_tags, 
        "private_tags": private_tags, 
        }

@view_config(name="describe_asset", renderer="altaircms:templates/page/viewlet/assets.mako")
def describe_asset(request):
    assets = api.get_assets(request)
    return {"assets": assets}



