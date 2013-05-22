# -*- coding:utf-8 -*-
from .searcher import EventSearcher
from .helper import SmartPhoneHelper
from .const import get_areas, SalesEnum
from ..search.search_query import SearchQuery
from ..search.forms import TopSearchForm, GenreSearchForm, GenreAreaSearchForm

from sqlalchemy import asc
from datetime import datetime
from altaircms.models import Genre
from altaircms.tag.models import HotWord
from altaircms.topic.api import get_topic_searcher
from altaircms.genre.searcher import GenreSearcher
from altaircms.topic.models import TopicTag, PromotionTag, TopcontentTag

class GenreNode(object):
    def __init__(self, genre, children):
        self.genre = genre
        self.children = children

class CommonResource(object):
    def __init__(self, request):
        self.request = request

    def get_top_render_param(self):
        promotions = self.getInfo(kind="promotion", system_tag_id=None)[0:5]
        topcontents = self.getInfo(kind="topcontent", system_tag_id=None)[0:5]
        topics = self.getInfo(kind="topic", system_tag_id=None)[0:5]
        hotwords = self.get_hotword()[0:5]
        genretree = self.get_genre_tree(parent=None)
        areas = self.get_area()

        return {
             'promotions':promotions
            ,'topcontents':topcontents
            ,'topics':topics
            ,'hotwords':hotwords
            ,'genretree':genretree
            ,'areas':areas
            ,'helper':SmartPhoneHelper()
            ,'form':TopSearchForm()
        }

    def get_genre_render_param(self):
        form = GenreSearchForm()
        genre_id = self.request.matchdict.get('genre_id')
        form.genre_id.data = genre_id
        genre = self.get_genre(id=genre_id)
        promotions = self.getInfo(kind="promotion", system_tag_id=genre_id)[0:5]
        topcontents = self.getInfo(kind="topcontent", system_tag_id=genre_id)[0:5]
        topics = self.getInfo(kind="topic", system_tag_id=genre_id)[0:5]
        hotwords = self.get_hotword()[0:5]
        genretree = self.get_genre_tree(parent=genre)
        areas = self.get_area()
        week_sales = self.search_week(genre, 1, 10)
        near_end_sales = self.search_near_end(genre, 1, 10)
        area_form = GenreAreaSearchForm()
        area_form.genre_id.data = genre.id

        return {
             'genre':genre
            ,'promotions':promotions
            ,'topcontents':topcontents
            ,'topics':topics
            ,'hotwords':hotwords
            ,'genretree':genretree
            ,'areas':areas
            ,'week_sales':week_sales
            ,'near_end_sales':near_end_sales
            ,'helper':SmartPhoneHelper()
            ,'form':form
            ,'area_form':area_form
        }

    def get_subsubgenre_render_param(self, genre_id):
        form = GenreSearchForm(self.request.GET)
        genre = self.get_genre(form.data['genre_id'])
        if not genre:
            genre = self.get_genre(genre_id)
        query = SearchQuery(None, genre, SalesEnum.ON_SALE.v, None)
        page = form.data['page'] if form.data['page'] else 1
        result = self.search_subsubgenre(query, int(page), 10)

        return {
             'form':form
            ,'result':result
            ,'helper':SmartPhoneHelper()
        }

    # サブサブジャンル検索
    def search_subsubgenre(self, query, page, per):
        searcher = EventSearcher(request=self.request)
        qs = searcher.search_freeword(search_query=query, genre_label=query.genre.label, cond=None)
        qs = searcher.search_sale(search_query=query, qs=qs)
        result = searcher.create_result(qs=qs, page=page, query=query, per=per)
        return result

    def get_system_tag_label(self, request, system_tag_id):
        if not system_tag_id:
            return None
        system_tag = request.allowable(Genre).filter(Genre.id==system_tag_id).first()
        return system_tag.label

    def _getInfo(self, searcher, tag, system_tag_label):
        if system_tag_label:
            system_tag = searcher.get_tag_from_genre_label(system_tag_label)
            results = searcher.query_publishing_topics(datetime.now(), tag, system_tag)
        else:
            results = searcher.query_publishing_topics(datetime.now(), tag)
        return results

    def getInfo(self, kind, system_tag_id):
        if kind == "promotion":
            searcher = get_topic_searcher(self.request, "promotion")
            tag = self.request.allowable(PromotionTag).filter_by(label=u"プロモーション枠").first()
        elif kind == "topcontent":
            searcher = get_topic_searcher(self.request, "topcontent")
            tag = self.request.allowable(TopcontentTag).filter_by(label=u"注目のイベント").first()
        elif kind == "topic":
            searcher = get_topic_searcher(self.request, "topic")
            tag = self.request.allowable(TopicTag).filter_by(label=u"トピックス").first()
        elif kind == "canceled":
            searcher = get_topic_searcher(self.request, "topic")
            tag = self.request.allowable(TopicTag).filter_by(label=u"公演中止情報").first()
        elif kind == "help":
            searcher = get_topic_searcher(self.request, "topic")
            tag = self.request.allowable(TopicTag).filter_by(label=u"質問").first()
        system_tag_label = self.get_system_tag_label(request=self.request, system_tag_id=system_tag_id)
        return self._getInfo(searcher=searcher, tag=tag, system_tag_label=system_tag_label)

    def get_hotword(self):
        today = datetime.now()
        hotwords = self.request.allowable(HotWord).filter(HotWord.term_begin <= today).filter(today <= HotWord.term_end) \
                 .filter_by(enablep=True).order_by(asc("display_order"), asc("term_end"))
        return hotwords

    def get_genre_tree(self, parent):
        genre_searcher = GenreSearcher(self.request)
        tree = genre_searcher.root.children
        if parent:
            tree = genre_searcher.get_children(parent)

        genretree = []
        for genre in tree:
            subgenre = genre_searcher.get_children(genre)
            node = GenreNode(genre=genre, children=subgenre)
            genretree.append(node)
        return genretree

    def get_area(self):
        return get_areas()

    def get_genre(self, id):
        genre = self.request.allowable(Genre).filter(Genre.id == id).first()
        return genre
