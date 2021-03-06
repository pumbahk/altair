# -*- coding:utf-8 -*-
from .searcher import EventSearcher, SimpleEventSearcher, PrefectureEventSearcher
from .helper import SmartPhoneHelper
from .const import get_areas, SalesEnum
from .utils import SnsUtils
from ..search.search_query import SearchQuery
from ..search.forms import TopSearchForm, GenreSearchForm, AreaSearchForm
from ..search.search_query import SaleInfo

from sqlalchemy import asc
from altaircms.datelib import get_now
from altaircms import helpers
from altaircms.models import Genre, Category
from altaircms.page.models import StaticPageSet
from altaircms.genre.searcher import GenreSearcher
from altaircms.tag.models import HotWord
from altaircms.topic.api import get_topic_searcher
from altaircms.genre.searcher import GenreSearcher
from altaircms.topic.models import TopicTag, PromotionTag, TopcontentTag
from altairsite.separation import get_organization_from_request

class GenreNode(object):
    def __init__(self, genre, children):
        self.genre = genre
        self.children = children

class CommonResource(object):
    def __init__(self, request):
        self.request = request

    def get_top_render_param(self):
        org = get_organization_from_request(self.request)
        if org.short_name == 'RT':
            promotions = self.getInfo(kind="promotion", system_tag_id=None)[0:15]
            topcontents = self.getInfo(kind="topcontent", system_tag_id=None)[0:5]
            topics = self.getInfo(kind="topic", system_tag_id=None)[0:5]
            hotwords = self.get_hotword()[0:5]
        else:
            promotions = self.getInfo(kind="promotion", system_tag_id=None)
            topcontents = self.getInfo(kind="topcontent", system_tag_id=None)
            topics = self.getInfo(kind="topic", system_tag_id=None)
            hotwords = self.get_hotword()

        weekly_sale = self.search_week(None, 1, 100)
        # 静的ページの表示順が1のものを初期表示、もっと見るを押すと2のものを表示
        static_pagesets_dict = self.get_static_pagesets_dict()
        genretree = self.get_genre_tree(parent=None)
        areas = self.get_area()
        promotion_banners = self.get_promotion_banners()
        news = self.get_news()
        top_news = self.get_top_news()
        pr_list = self.get_pr_list()

        return {
            'promotions': promotions
            , 'topcontents': topcontents
            , 'topics': topics
            , 'hotwords': hotwords
            , 'weekly_sale': weekly_sale
            , 'static_pagesets_dict': static_pagesets_dict
            , 'genretree': genretree
            , 'genre_searcher': GenreSearcher(self.request)
            , 'areas': areas
            , 'helper': SmartPhoneHelper()
            , 'helpers': helpers
            , 'form': TopSearchForm()
            , 'promotion_banners': promotion_banners
            , 'news': news
            , 'top_news': top_news
            , 'pr_list': pr_list
        }

    def get_genre_render_param(self, genre_id):
        org = get_organization_from_request(request=self.request)
        form = GenreSearchForm()
        genre_id = genre_id or self.request.matchdict.get('genre_id')
        form.genre_id.data = genre_id
        genre = self.get_genre(id=genre_id)
        promotions = self.getInfo(kind="promotion", system_tag_id=genre_id)[0:15]
        topcontents = self.getInfo(kind="topcontent", system_tag_id=genre_id)[0:5]
        if org.code == 'YT':
            topcontents = self.getInfo(kind="topcontent", system_tag_id=genre_id).all()
        topics = self.getInfo(kind="topic", system_tag_id=genre_id)[0:5]
        hotwords = self.get_hotword()[0:5]
        genretree = self.get_genre_tree(parent=genre)
        areas = self.get_area()
        week_sales = self.search_week(genre, 1, 10)
        near_end_sales = self.search_near_end(genre, 1, 10)
        utils = SnsUtils(request=self.request)

        return {
            'genre': genre
            , 'promotions': promotions
            , 'topcontents': topcontents
            , 'topics': topics
            , 'hotwords': hotwords
            , 'genretree': genretree
            , 'genre_searcher': GenreSearcher(self.request)
            , 'areas': areas
            , 'week_sales': week_sales
            , 'near_end_sales': near_end_sales
            , 'helper': SmartPhoneHelper()
            , 'helpers': helpers
            , 'form': form
            , 'sns': {
                'url': utils.get_sns_url_from_genre(genre=genre),
                'title': u"楽天チケット-" + genre.label
            }
        }

    def get_subsubgenre_render_param(self, genre_id):
        form = GenreSearchForm(self.request.GET)
        genre = self.get_genre(form.data['genre_id'])
        if not genre:
            genre = self.get_genre(genre_id)
        query = SearchQuery(None, genre, SalesEnum.ON_SALE.v, None)
        page = form.data['page'] if form.data['page'] else 1
        result = self.search_subsubgenre(query, int(page), 10)
        utils = SnsUtils(request=self.request)

        return {
             'form':form
            ,'genre':genre
            ,'result':result
            ,'helper':SmartPhoneHelper()
            , 'sns':{
                'url':utils.get_sns_url_from_genre(genre=genre),
                'title':u"楽天チケット-" + genre.label
            }
        }

    # サブサブジャンル検索
    def search_subsubgenre(self, query, page, per):
        searcher = SimpleEventSearcher(request=self.request)
        qs = searcher.search_freeword(search_query=query, genre_label=query.genre.label, cond=None)
        if qs:
            qs = searcher.search_sale(search_query=query, qs=qs)
        result = searcher.create_result(qs=qs, page=page, query=query, per=per)
        return result

    # 今週発売
    def search_week(self, genre, page, per):
        searcher = SimpleEventSearcher(request=self.request)
        query = SearchQuery(None, genre, SalesEnum.WEEK_SALE.v, None)
        qs = self.load_freeword(search_query=query)
        qs = searcher.search_week_sale(offset=None, qs=qs)
        result = searcher.create_result(qs=qs, page=page, query=query, per=per)
        return result

    # 販売終了間近
    def search_near_end(self, genre, page, per):
        searcher = SimpleEventSearcher(request=self.request)
        sale_info = SaleInfo(sale_start=None, sale_end=7)
        query = SearchQuery(None, genre, SalesEnum.NEAR_SALE_END.v, sale_info)
        qs = self.load_freeword(search_query=query)
        qs = searcher.search_near_sale_end(search_query=query, qs=qs)
        result = searcher.create_result(qs=qs, page=page, query=query, per=per)
        return result

    # ２回全文検索しない
    def load_freeword(self, search_query):
        qs = None
        if getattr(self.request, "genre_freeword", None):
            qs = self.request.genre_freeword
        else:
            searcher = SimpleEventSearcher(request=self.request)
            if search_query.genre:
                qs = searcher.search_freeword(search_query=search_query, genre_label=search_query.genre.label,
                                              cond=None)
            else:
                qs = searcher.search_freeword(search_query=search_query, genre_label=None, cond=None)
            self.request.genre_freeword = qs
        return qs

    def get_system_tag_label(self, request, system_tag_id):
        if not system_tag_id:
            return None
        system_tag = request.allowable(Genre).filter(Genre.id==system_tag_id).first()
        return system_tag.label

    def _getInfo(self, searcher, tag, system_tag_label):
        if tag is None:
            return []
        elif system_tag_label:
            system_tag = searcher.get_tag_from_genre_label(system_tag_label)
            results = searcher.query_publishing_topics(get_now(self.request), tag, system_tag)
        else:
            results = searcher.query_publishing_topics(get_now(self.request), tag)
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
        today = get_now(self.request)
        hotwords = self.request.allowable(HotWord).filter(HotWord.term_begin <= today).filter(today <= HotWord.term_end) \
                 .filter_by(enablep=True).order_by(asc("display_order"), asc("term_end"))
        return hotwords

    def get_genre_tree(self, parent):
        genre_searcher = GenreSearcher(self.request)
        if genre_searcher.root is None:
            return []
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

    def get_static_pagesets_dict(self):
        # 静的ページで1のものを初期表示、もっと見るを押すと2のものを表示
        initial_disp_static_pagesets = self.request.allowable(StaticPageSet).filter(
            StaticPageSet.display_order == 1).all()
        static_pagesets = self.request.allowable(StaticPageSet).filter(
            StaticPageSet.display_order == 2).all()
        static_pagesets_dict = {'initial_disp': initial_disp_static_pagesets, 'disp': static_pagesets}
        return static_pagesets_dict

    def get_genre(self, id):
        genre = self.request.allowable(Genre).filter(Genre.id == id).first()
        return genre

    def get_top_news(self):
        top_news = self.request.allowable(Category).filter(Category.hierarchy == 'top_news').order_by(
            Category.display_order).all()
        return top_news

    def get_news(self):
        news = self.request.allowable(Category).filter(Category.hierarchy == 'news').order_by(
            Category.display_order).all()
        return news

    def get_pr_list(self):
        pr_list = self.request.allowable(Category).filter(Category.hierarchy == 'pr_list').order_by(
            Category.display_order).all()
        return pr_list

    def get_promotion_banners(self):
        banners = self.request.allowable(Category).filter(Category.hierarchy == 'promotion_banner').order_by(
            Category.display_order).all()
        return banners
