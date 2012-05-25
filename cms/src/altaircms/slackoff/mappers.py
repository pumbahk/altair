# -*- coding:utf-8 -*-

from altaircms.models import model_to_dict
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
    objlike.pageset = obj.pageset.name if obj.pageset else None
    objlike.link = obj.get_link(request)
    return objlike
    
PDICT = import_symbol("altaircms.seeds.prefecture:PrefectureMapping").name_to_label
def performance_mapper(request, obj):
    objlike = ObjectLike(**model_to_dict(obj))
    objlike.event = obj.event.title if obj.event else None
    objlike.prefecture = PDICT.get(obj.prefecture, u"-")
    return objlike

def ticket_mapper(request, obj):
    objlike = ObjectLike(**model_to_dict(obj))
    objlike.event = obj.event.title if obj.event else None
    return objlike

def category_mapper(request, obj):
    objlike = ObjectLike(**model_to_dict(obj))
    objlike.parent = obj.parent.name if obj.parent else None

    class pageLinkRender(object):
        def __html__(self):
            if obj.pageset:
                return u'<a href="%s">%s</a>' % (h.link.to_publish_page_from_pageset(request, obj.pageset), obj.pageset.name)
            else:
                return u"-"
    objlike.pageset = pageLinkRender()
    objlike.imgsrc = RawText(u'<img src="%s"/>' % obj.imgsrc)
    for k, v in objlike.iteritems():
        if v is None:
            setattr(objlike, k, u"-")
    return objlike

def topic_mapper(request, obj):
    objlike = ObjectLike(**model_to_dict(obj))
    objlike.event = obj.event.title if obj.event else u"-"
    objlike.text = obj.text if len(obj.text) <= 20 else obj.text[:20]+u"..."
    objlike.page = obj.page.title if obj.page else u"-"
    return objlike

def topcontent_mapper(request, obj):
    objlike = ObjectLike(**model_to_dict(obj))
    image_asset = obj.image_asset.title or u"名前なし"
    objlike.image_asset = RawText(u'<a href="%s">%s</a>' % (h.asset.to_show_page(request, obj.image_asset), image_asset))
    objlike.page = obj.page.title if obj.page else u"-"
    return objlike

def hotword_mapper(request, obj):
    objlike = ObjectLike(**model_to_dict(obj))
    objlike.tag = obj.tag.label if obj.tag else u"------"
    return objlike
