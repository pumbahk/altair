# -*- coding:utf-8 -*-

from altaircms.models import model_to_dict
from altaircms.topic.models import Topcontent
import altaircms.helpers as h

import pkg_resources
def import_symbol(symbol):
    return pkg_resources.EntryPoint.parse("x=%s" % symbol).load(False)

class ObjectLike(dict):
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__

class RawText(object):
    def __init__(self, text):
        self.text = text

    def __html__(self):
        return self.text or u"-"

def layout_mapper(request, obj):
    objlike = ObjectLike(**model_to_dict(obj))
    return objlike

def promotion_mapper(request, obj):
    objlike = ObjectLike(**model_to_dict(obj))
    return objlike

def promotion_unit_mapper(request, obj):
    objlike = ObjectLike(id=obj.id, text=obj.text)
    objlike.promotion = obj.promotion.name
    objlike.main_image = obj.main_image.title or u"名前なし"
    objlike.thumbnail = obj.thumbnail.title or u"名前なし"
    objlike.pageset = RawText(u'<a href="%s">%s</a>' % (h.link.to_preview_page_from_pageset(request, obj.pageset), obj.pageset.name)) if obj.pageset else u"-"
    url = obj.get_link(request)
    objlike.link = RawText(u'<a href="%s">%s</a>' % (url, url))
    return objlike
    
PDICT = import_symbol("altaircms.seeds.prefecture:PrefectureMapping").name_to_label
def performance_mapper(request, obj):
    objlike = ObjectLike(**model_to_dict(obj))
    objlike.event = RawText(u'<a href="%s">%s</a>' % (request.route_path("event", id=obj.event.id), obj.event.title)) if obj.event else u"-"
    objlike.prefecture = PDICT.get(obj.prefecture, u"-")
    return objlike


SALES_DICT = dict(import_symbol("altaircms.seeds.saleskind:SALESKIND_CHOICES"))
def sale_mapper(request, obj):
    objlike = ObjectLike(**model_to_dict(obj))
    objlike.event = RawText(u'<a href="%s">%s</a>' % (request.route_path("event", id=obj.event.id), obj.event.title)) if obj.event else u"-"
    objlike.kind = SALES_DICT[obj.kind]
    return objlike


def ticket_mapper(request, obj):
    objlike = ObjectLike(**model_to_dict(obj))
    # objlike.event = obj.event.title if obj.event else None
    objlike.sale = RawText(u'<a href="%s">%s</a>' % (request.route_path("sale_update", id=obj.sale.id, action="input"), obj.sale.name)) if obj.sale else u"-"
    return objlike

def category_mapper(request, obj):
    objlike = ObjectLike(**model_to_dict(obj))
    objlike.parent = obj.parent.name if obj.parent else None

    objlike.pageset = RawText(u'<a href="%s">%s</a>' % (h.link.to_preview_page_from_pageset(request, obj.pageset), obj.pageset.name)) if obj.pageset else u"-"
    objlike.imgsrc = RawText(u'<img src="%s"/>' % obj.imgsrc)
    for k, v in objlike.iteritems():
        if v is None:
            setattr(objlike, k, u"-")
    return objlike

def topic_mapper(request, obj):
    objlike = ObjectLike(**model_to_dict(obj))
    objlike.event = RawText(u'<a href="%s">%s</a>' % (request.route_path("event", id=obj.event.id), obj.event.title)) if obj.event else u"-"
    objlike.text = obj.text if len(obj.text) <= 20 else obj.text[:20]+u"..."
    objlike.bound_page = obj.bound_page.name if obj.bound_page else u"-"
    objlike.linked_page = obj.linked_page.name if obj.linked_page else u"-"
    return objlike

CDWN_DICT = dict(Topcontent.COUNTDOWN_CANDIDATES)
def topcontent_mapper(request, obj):
    objlike = ObjectLike(**model_to_dict(obj))
    image_asset = obj.image_asset.title or u"名前なし"
    objlike.image_asset = RawText(u'<a href="%s">%s</a>' % (h.asset.to_show_page(request, obj.image_asset), image_asset))
    objlike.bound_page = obj.bound_page.name if obj.bound_page else u"-"
    objlike.linked_page = obj.linked_page.name if obj.linked_page else u"-"
    objlike.countdown_type = CDWN_DICT[obj.countdown_type]
    return objlike

def hotword_mapper(request, obj):
    objlike = ObjectLike(**model_to_dict(obj))
    objlike.tag = obj.tag.label if obj.tag else u"------"
    return objlike

def pagedefaultinfo_mapper(request, obj):
    objlike = ObjectLike(**model_to_dict(obj))
    objlike.pageset = RawText(u'<a href="%s">%s</a>' % (h.link.to_preview_page_from_pageset(request, obj.pageset), obj.pageset.name)) if obj.pageset else u"-"
    return objlike
