# -*- coding:utf-8 -*-
from ..common.searcher import EventSearcher
from ..common.resources import CommonResource
from altaircms.models import Genre
from altaircms.event.models import Event
from altaircms.tag.models import HotWord
from altaircms.genre.searcher import GenreSearcher
from altaircms.page.models import PageSet, PageTag2Page, PageTag
from altairsite.mobile.core.helper import log_info

from datetime import date, datetime

class SearchPageResource(CommonResource):
    def __init__(self, request):
        self.request = request

    def get_genre(self, id):
        genre = self.request.allowable(Genre).filter(Genre.id==id).first()
        return genre

    # トップ画面、ジャンル画面の検索
    def search(self, query, page, per):
        searcher = EventSearcher(request=self.request)
        if query.genre:
            qs = searcher.search_freeword(search_query=query, genre_label=query.genre.label, cond=None)
        else:
            qs = searcher.search_freeword(search_query=query, genre_label=None, cond=None)
        qs = searcher.search_sale(search_query=query, qs=qs)
        result = searcher.create_result(qs=qs, page=page, query=query, per=per)
        return result

    # トップ画面、ジャンルのエリア検索
    def search_area(self, query, page, per):
        searcher = EventSearcher(request=self.request)
        qs = None
        if query.word:
            log_info("search_area", "genre=" + query.word)
            qs = searcher.search_freeword(search_query=query, genre_label=None, cond=None)
            qs = searcher.search_area(search_query=query, qs=qs)
        else:
            qs = searcher.search_area(search_query=query, qs=qs)

        qs = searcher.search_on_sale(qs=qs)
        result = searcher.create_result(qs=qs, page=page, query=query, per=per)
        return result

    # 詳細検索
    def search_detail(self, query, page, per):
        searcher = EventSearcher(request=self.request)
        qs = None

        # フリーワード、ジャンル
        if query.word:
            if query.genre:
                qs = searcher.search_freeword(search_query=query, genre_label=query.genre.label, cond=query.cond)
            else:
                qs = searcher.search_freeword(search_query=query, genre_label=None, cond=query.cond)
        qs = searcher.search_prefectures(search_query=query, qs=qs)
        qs = searcher.search_sales_segment(search_query=query, qs=qs)
        qs = searcher.search_event_open(search_query=query, qs=qs)
        qs = searcher.search_near_sale_start(search_query=query, qs=qs)
        qs = searcher.search_near_sale_end(search_query=query, qs=qs)
        qs = searcher.search_perf(search_query=query, qs=qs)
        result = searcher.create_result(qs=qs, page=page, query=query, per=per)
        return result

    # ホットワード検索結果表示
    def search_hotword(self, query, page, per):
        searcher = EventSearcher(request=self.request)
        today = datetime.now()
        hotword = self.request.allowable(HotWord).filter(HotWord.term_begin <= today) \
            .filter(today <= HotWord.term_end) \
            .filter_by(enablep=True).filter(HotWord.id == query.hotword.id).first()

        qs = self.request.allowable(Event) \
                    .filter(Event.is_searchable == True) \
                    .join(PageSet, Event.id == PageSet.event_id) \
                    .join(PageTag2Page, PageSet.id == PageTag2Page.object_id) \
                    .join(PageTag, PageTag2Page.tag_id == PageTag.id) \
                    .filter(PageTag.id == hotword.tag_id)

        result = searcher.create_result(qs=qs, page=page, query=query, per=per)
        return result

    # 詳細検索フォーム生成
    def init_detail_search_form(self, form):
        form.genre_id.choices = self.create_genre_selectbox(self.request)
        form.year.choices, form.month.choices, form.day.choices = self.create_date_selectbox()
        form.since_year.choices, form.since_month.choices, form.since_day.choices = self.create_date_selectbox()
        form.sale_start.choices = self.create_choices(1, 32)
        form.sale_end.choices = self.create_choices(1, 32)

    def create_genre_selectbox(self, request):
        genre_searcher = GenreSearcher(request)
        genres = genre_searcher.root.children

        choices = []
        choices.append([0, u'選択なし'])
        for genre in genres:
            choices.append([genre.id, genre.label])
            for sub_genre in genre.children:
                choices.append([sub_genre.id, u"┗ " + sub_genre.label])
        return choices

    def create_choices(self, start, end):
        choices = []
        choices.append(['', '-'])
        for value in range(start, end):
            choices.append([str(value), str(value)])
        return choices

    def create_date_selectbox(self):
        today = date.today()
        year_choices = self.create_choices(today.year, today.year + 3)
        month_choices = self.create_choices(1, 13)
        day_choices = self.create_choices(1, 32)
        return year_choices, month_choices, day_choices

    def get_hotword_from_id(self, id):
        genre = self.request.allowable(HotWord).filter(HotWord.id == id).first()
        return genre

