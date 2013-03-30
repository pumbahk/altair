# -*- coding:utf-8 -*-
import sqlalchemy as sa
import sqlalchemy.orm as orm
from datetime import datetime
from zope.deprecation import deprecate

from altaircms.tag.models import HotWord
from altaircms.page.models import PageTag
from altaircms.models import Category, Genre, SalesSegmentKind, _GenrePath
from markupsafe import Markup


class MyLayout(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request


    def navigation_link_list(self, hierarchy):
        return get_navigation_links(self.request, hierarchy)

    ## ?
    def salessegment_group_list(self):
        return get_salessegment_groups(self.request)

    def hotword_list(self):
        return get_current_hotwords(self.request)

    @property
    def top_salessegment_kind_list(self):
        return get_salessegment_kinds(self.request)

    @property
    def top_category_genre_list(self):
        return get_top_category_genres(self.request, strict=True)

    def get_subgenre_list_from_genre(self, genre):
        return (genre.children or []) if genre else []        

    def get_subgenre_list_from_page(self, page):
        if page and hasattr(page, "pageset") and page.pageset.genre_id:
            genre = page.pageset.genre
            return genre.children if genre else []
        return []
       
    def get_genre_tree_with_nestlevel(self, genre):
        if not genre:
            return []
        ancestors = genre.query_ancestors().with_entities(_GenrePath.hop, Genre)
        ancestors = ancestors.options(orm.joinedload(Genre.category_top_pageset)).all()
        r = []
        max_depth = ancestors[-1][0]
        ancestors.pop()
        if not ancestors:
            r.append((1, True, genre))
            for g in self.get_subgenre_list_from_genre(genre):
                r.append((2, False, g))
            return r
        for i, g in reversed(ancestors):
            r.append((max_depth-i, False, g))
            if i == 1:
                sibblings = g.query_descendant(hop=1).options(orm.joinedload(Genre.category_top_pageset)).all()
                index = max_depth + 1
                for g in sibblings:
                    if g.id == genre.id:
                        r.append((index, True, g))
                        for g in genre.children:
                            r.append((index+1, False, g))
                    else:
                        r.append((index, False, g))
        return r

    def get_genre_tree_with_nestlevel_from_page(self, page):
        if page and hasattr(page, "pageset") and page.pageset.genre_id:
            return self.get_genre_tree_with_nestlevel(page.pageset.genre)
        return []
         
    _body_id = "index"
    @property
    def body_id(self):
        return getattr(self.request, "body_id", None) or self._body_id

    header_images_dict = dict(
        searchform=Markup(u'<img id="titleImage" src="/static/RT/img/search/title_searchform.gif" alt="絞り込み検索"/>'), 
        search=Markup(u'<img id="titleImage" src="/static/RT/img/search/title_search.gif" alt="検索結果"/>')
        )
    @property
    def page_title_image(self):
        return self.header_images_dict.get(self.body_id, "")

def get_top_category_genres(request, strict=False):
    root = request.allowable(Genre).filter(Genre.is_root==True).first()
    if not strict:
        return root.children
    return [g for g in root.children if g.category_top_pageset_id]

def get_system_tags_from_genres(request, genres):
    genres = [g.label for g in genres]
    return PageTag.query.filter(PageTag.organization_id==None, PageTag.label.in_([genres]))

def get_salessegment_kinds(request):
    return request.allowable(SalesSegmentKind).filter_by(publicp=True).all()
    
def get_salessegment_groups(request):
    request.allowable()

def get_navigation_links(request, hierarchy):
    qs =  Category.get_toplevel_categories(hierarchy=hierarchy, request=request)
    return qs.order_by(sa.asc("display_order")).options(orm.joinedload("pageset"))
_get_categories = get_navigation_links

def get_current_hotwords(request, _nowday=datetime.now):
    today = _nowday()
    qs =  HotWord.query.filter(HotWord.term_begin <= today).filter(today <= HotWord.term_end)
    qs = qs.filter_by(enablep=True).order_by(sa.asc("display_order"), sa.asc("term_end"))
    return qs

@deprecate("this is obsolete")
def get_subcategories_from_page(request, page):
    """ カテゴリトップのサブカテゴリを取得する
    """
    qs = Category.query.filter(Category.pageset==page.pageset).filter(Category.pageset != None)
    root_category = qs.first()
    return root_category.children if root_category else []

@deprecate("this is obsolete")
def get_navigation_categories(request):
    """ ページヘッダのナビゲーション用のcategoryを取得する。
    """
    top_outer_categories = _get_categories(request, hierarchy=u"top_outer")
    top_inner_categories = _get_categories(request, hierarchy=u"top_inner")

    categories = _get_categories(request, hierarchy=u"大")

    return dict(categories=categories,
                top_outer_categories=top_outer_categories,
                top_inner_categories=top_inner_categories)

