# -*- coding:utf-8 -*-

from altaircms.models import model_to_dict as model_to_dict_original, SalesSegment
from altaircms.topic.models import Topcontent
import altaircms.helpers as h
from markupsafe import Markup
from altaircms.asset.viewhelpers import image_asset_layout
from altaircms.models import Genre
from altaircms.page.models import PageType

import pkg_resources

def model_to_dict(obj):
    if hasattr(obj, "to_dict"):
        return obj.to_dict()
    else:
        return model_to_dict_original(obj)

def show_cms_detail_page(request, page):
    if page is None:
        return u"-"
    url= request.route_path("page_detail", page_id=page.id)
    return Markup(u'<a href="%s">%s</a>' % (url, page.name))

def label_from_genre(genre_id_list):
    return u", ".join([g.label for g in Genre.query.filter(Genre.id.in_(genre_id_list))])

def import_symbol(symbol):
    return pkg_resources.EntryPoint.parse("x=%s" % symbol).load(False)

class ObjectLike(dict):
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__


def layout_mapper(request, obj):
    objlike = ObjectLike(**model_to_dict(obj))
    downloadlink = request.route_path("layout_download", layout_id=obj.id)
    previewlink = request.route_path("layout_preview", layout_id=obj.id)
    objlike.template_filename = Markup(u'%s(<a href="%s">download</a>)<a href="%s"><i class="icon-eye-open"></i></a>' % (obj.template_filename, downloadlink, previewlink))
    return objlike

def promotion_mapper(request, obj):
    objlike = ObjectLike(**model_to_dict(obj))
    objlike.tag_content = u", ".join(obj.tag_content)
    objlike.genre =  label_from_genre(obj.genre)
    objlike.main_image = image_asset_layout(request, obj.main_image)
    objlike.linked_page = show_cms_detail_page(request, obj.linked_page)
    objlike.link = obj.link or u"-"
    objlike.mobile_tag = obj.mobile_tag.label if obj.mobile_tag else ""
    return objlike

def topic_mapper(request, obj):
    objlike = ObjectLike(**model_to_dict(obj))
    objlike.tag_content = u", ".join(obj.tag_content)
    objlike.genre =  label_from_genre(obj.genre)
    objlike.linked_page = show_cms_detail_page(request, obj.linked_page)
    objlike.link = obj.link or u"-"
    objlike.mobile_link = obj.mobile_link or u"-"
    objlike.mobile_tag = obj.mobile_tag.label if obj.mobile_tag else ""
    return objlike

CDWN_DICT = dict(Topcontent.COUNTDOWN_CANDIDATES)    
def topcontent_mapper(request, obj):
    objlike = ObjectLike(**model_to_dict(obj))
    objlike.tag_content = u", ".join(obj.tag_content)
    objlike.genre =  label_from_genre(obj.genre)
    objlike.image_asset = image_asset_layout(request, obj.image_asset)
    objlike.mobile_image_asset = image_asset_layout(request, obj.mobile_image_asset)
    objlike.linked_page = show_cms_detail_page(request, obj.linked_page)
    objlike.link = obj.link or u"-"
    objlike.mobile_link = obj.mobile_link or u"-"
    objlike.countdown_type = CDWN_DICT[obj.countdown_type]
    objlike.mobile_tag = obj.mobile_tag.label if obj.mobile_tag else ""
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
    objlike.performance = obj.performance.title
    objlike.group = obj.group.name
    return objlike


def ticket_mapper(request, obj):
    objlike = ObjectLike(**model_to_dict(obj))
    salessegment = SalesSegment.query.filter_by(id=obj.sale.id).first()
    objlike.sale = salessegment.group.name if salessegment.group_id else u"--"
    return objlike

def category_mapper(request, obj):
    objlike = ObjectLike(**model_to_dict(obj))
    objlike.parent = obj.parent.label if obj.parent else None

    objlike.pageset = Markup(u'<a href="%s">%s</a>' % (h.link.preview_page_from_pageset(request, obj.pageset), obj.pageset.name)) if obj.pageset else u"-"
    objlike.imgsrc = Markup(u'<img src="%s"/>' % obj.imgsrc)
    objlike.url = Markup(u'<a href="%s">%s</a>' % (obj.url, obj.url)) if obj.url else u"-"
    for k, v in objlike.iteritems():
        if v is None:
            setattr(objlike, k, u"-")
    return objlike

def hotword_mapper(request, obj):
    objlike = ObjectLike(**model_to_dict(obj))
    objlike.tag = obj.tag.label if obj.tag else u"------"
    return objlike

def pagedefaultinfo_mapper(request, obj):
    objlike = ObjectLike(**model_to_dict(obj))
    objlike.pagetype = Markup(u'<a href="%s">%s</a>' % (request.route_path("pagetype_update", action="input", id=obj.pagetype.id, _query=dict(endpoint=request.url)), obj.pagetype.label)) if obj.pagetype else u"-"
    objlike.title_prefix = obj.title_prefix if obj.title_prefix else ""
    objlike.title_suffix = obj.title_suffix if obj.title_suffix else ""
    return objlike

prole_dict = dict(PageType.page_role_candidates)
prendering_type_dict = dict(PageType.page_rendering_type_candidates)
def pagetype_mapper(request, obj):
    objlike = ObjectLike(**model_to_dict(obj))
    objlike.page_role = prole_dict.get(obj.page_role, u"-")
    objlike.page_rendering_type = prendering_type_dict.get(obj.page_rendering_type, u"-")
    return objlike

def pageset_mapper(request, obj):
    objlike = ObjectLike(**model_to_dict(obj))
    objlike.genre_id =  label_from_genre([obj.genre_id])
    objlike.tags_string = obj.tags_string
    objlike.private_tags_string = obj.private_tags_string
    objlike.mobile_tags_string = obj.mobile_tags_string
    return objlike

def staticpage_mapper(request, obj):
    objlike = ObjectLike(**model_to_dict(obj))
    if obj.layout:
        objlike.layout = u"%s(%s)" % (obj.layout.title, obj.layout.template_filename)
    else:
        objlike.layout = None
    return objlike
