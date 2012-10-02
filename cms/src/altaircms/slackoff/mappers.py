# -*- coding:utf-8 -*-

from altaircms.models import model_to_dict as model_to_dict_original

def model_to_dict(obj):
    if hasattr(obj, "to_dict"):
        return obj.to_dict()
    else:
        return model_to_dict_original(obj)

from altaircms.topic.models import Topcontent
import altaircms.helpers as h
from markupsafe import Markup

import pkg_resources
def import_symbol(symbol):
    return pkg_resources.EntryPoint.parse("x=%s" % symbol).load(False)

class ObjectLike(dict):
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__

def image_asset_layout(request, asset):
    if asset is None:
        u""
    else:
        return Markup(u"""
<a href="%(href)s"><img src="%(href)s" width=50px height=50px alt="%(alt)s"/></a>
""" % dict(href=h.asset.to_show_page(request, asset), alt=asset.title))


def layout_mapper(request, obj):
    objlike = ObjectLike(**model_to_dict(obj))
    return objlike

def promotion_mapper(request, obj):
    objlike = ObjectLike(**model_to_dict(obj))
    objlike.kind_content = obj.kind_content
    objlike.main_image = image_asset_layout(request, obj.main_image)
    objlike.thumbnail = image_asset_layout(request, obj.thumbnail)
    objlike.linked_page = Markup(u'<a href="%s">%s</a>' % (h.link.preview_page_from_pageset(request, obj.linked_page), obj.linked_page.name)) if obj.linked_page else u"-"
    url = h.link.get_link_from_promotion(request, obj)
    objlike.link = Markup(u'<a href="%s">リンク先</a>' % url)
    return objlike
    
PDICT = import_symbol("altaircms.seeds.prefecture:PrefectureMapping").name_to_label
def performance_mapper(request, obj):
    objlike = ObjectLike(**model_to_dict(obj))
    objlike.event = Markup(u'<a href="%s">%s</a>' % (request.route_path("event", id=obj.event.id), obj.event.title)) if obj.event else u"-"
    objlike.prefecture = PDICT.get(obj.prefecture, u"-")
    return objlike


SALES_DICT = dict(import_symbol("altaircms.seeds.saleskind:SALESKIND_CHOICES"))
def sale_mapper(request, obj):
    objlike = ObjectLike(**model_to_dict(obj))
    objlike.event = Markup(u'<a href="%s">%s</a>' % (request.route_path("event", id=obj.event.id), obj.event.title)) if obj.event else u"-"
    objlike.kind = SALES_DICT.get(obj.kind, u"-")
    return objlike


def ticket_mapper(request, obj):
    objlike = ObjectLike(**model_to_dict(obj))
    # objlike.event = obj.event.title if obj.event else None
    objlike.sale = Markup(u'<a href="%s">%s</a>' % (request.route_path("sale_update", id=obj.sale.id, action="input"), obj.sale.name)) if obj.sale else u"-"
    return objlike

def category_mapper(request, obj):
    objlike = ObjectLike(**model_to_dict(obj))
    objlike.parent = obj.parent.label if obj.parent else None

    objlike.pageset = Markup(u'<a href="%s">%s</a>' % (h.link.preview_page_from_pageset(request, obj.pageset), obj.pageset.name)) if obj.pageset else u"-"
    objlike.imgsrc = Markup(u'<img src="%s"/>' % obj.imgsrc)
    for k, v in objlike.iteritems():
        if v is None:
            setattr(objlike, k, u"-")
    return objlike

def show_cms_detail_page(request, page):
    if page is None:
        return u"-"
    url= request.route_path("page_detail", page_id=page.id)
    return Markup(u'<a href="%s">%s</a>' % (url, page.name))

def topic_mapper(request, obj):
    objlike = ObjectLike(**model_to_dict(obj))
    objlike.event = Markup(u'<a href="%s">%s</a>' % (request.route_path("event", id=obj.event.id), obj.event.title)) if obj.event else u"-"
    objlike.text = obj.text if len(obj.text) <= 20 else obj.text[:20]+u"..."
    objlike.bound_page = show_cms_detail_page(request, obj.bound_page)
    objlike.linked_page = show_cms_detail_page(request, obj.linked_page)
    objlike.link = obj.link or u"-"
    objlike.mobile_link = obj.mobile_link or u"-"
    return objlike

CDWN_DICT = dict(Topcontent.COUNTDOWN_CANDIDATES)    
def topcontent_mapper(request, obj):
    objlike = ObjectLike(**model_to_dict(obj))
    objlike.image_asset = image_asset_layout(request, obj.image_asset)
    objlike.mobile_image_asset = image_asset_layout(request, obj.mobile_image_asset)
    objlike.bound_page = show_cms_detail_page(request, obj.bound_page)
    objlike.linked_page = show_cms_detail_page(request, obj.linked_page)
    objlike.link = obj.link or u"-"
    objlike.mobile_link = obj.mobile_link or u"-"
    objlike.countdown_type = CDWN_DICT[obj.countdown_type]
    return objlike

def hotword_mapper(request, obj):
    objlike = ObjectLike(**model_to_dict(obj))
    objlike.tag = obj.tag.label if obj.tag else u"------"
    return objlike

def pagedefaultinfo_mapper(request, obj):
    objlike = ObjectLike(**model_to_dict(obj))
    objlike.pageset = Markup(u'<a href="%s">%s</a>' % (h.link.preview_page_from_pageset(request, obj.pageset), obj.pageset.name)) if obj.pageset else u"-"
    return objlike
