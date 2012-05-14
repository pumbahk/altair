# -*- coding:utf-8 -*-

from altaircms.models import model_to_dict
import altaircms.helpers as h

class ObjectLike(dict):
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__

def promotion_unit_mapper(request, obj):
    objlike = ObjectLike(id=obj.id, text=obj.text)
    objlike.promotion = obj.promotion.name
    objlike.main_image = obj.main_image.title or u"名前なし"
    objlike.thumbnail = obj.thumbnail.title or u"名前なし"
    objlike.pageset = obj.pageset.name if obj.pageset else None
    objlike.link = obj.get_link(request)
    return objlike
    

def performance_mapper(request, obj):
    objlike = ObjectLike(**model_to_dict(obj))
    objlike.event = obj.event.title if obj.event else None
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
    class imgRender(object):
        def __html__(self):
            return u'<img src="%s"/>' % obj.imgsrc
    objlike.imgsrc = imgRender()
    for k, v in objlike.iteritems():
        if v is None:
            setattr(objlike, k, u"-")
    return objlike
