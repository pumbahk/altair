# -*- coding:utf-8 -*-
from altairsite.config import usersite_view_config
from altairsite.smartphone.common.helper import SmartPhoneHelper
from altairsite.smartphone.event.search.forms import TopSearchForm, GenreSearchForm, AreaSearchForm, DetailSearchForm
from altairsite.smartphone.event.search.resources import SearchQuery, AreaSearchQuery, DetailSearchQuery\
    , EventOpenInfo, SaleInfo, PerformanceInfo
from altairsite.smartphone.common.const import SalesEnum

@usersite_view_config(route_name='search',request_type="altairsite.tweens.ISmartphoneRequest"
             , renderer='altairsite.smartphone:templates/searchresult/search.html')
def search(context, request):
    # トップ画面の検索
    form = TopSearchForm(request.GET)
    query = SearchQuery(form.data['word'], form.data['sale'])
    result = context.search(query, int(form.data['page']), 10)

    return {
         'result':result
        ,'helper':SmartPhoneHelper()
    }

@usersite_view_config(route_name='search_genre',request_type="altairsite.tweens.ISmartphoneRequest"
             , renderer='altairsite.smartphone:templates/searchresult/search.html')
def genre_search(context, request):
    # ジャンル画面の検索
    form = GenreSearchForm(request.GET)
    search_word = form.data['word']
    if form.data['sale'] == SalesEnum.GENRE.v:
        genre = context.get_genre(form.data['genre_id'])
        search_word = search_word + ' ' + genre.label

    query = SearchQuery(search_word, SalesEnum.ON_SALE.v)
    result = context.search(query, int(form.data['page']), 10)

    return {
         'result':result
        ,'helper':SmartPhoneHelper()
    }

@usersite_view_config(route_name='search_area',request_type="altairsite.tweens.ISmartphoneRequest"
             , renderer='altairsite.smartphone:templates/searchresult/area.html')
def search_area(context, request):
    # トップ画面のエリア検索
    form = AreaSearchForm(request.GET)
    query = AreaSearchQuery(area=form.data['area'], genre_id=None, genre_label=None)
    result = context.search_area(query, int(form.data['page']), 10)
    print form.data['area']

    return {
         'query':query
        ,'result':result
        ,'helper':SmartPhoneHelper()
    }

@usersite_view_config(route_name='search_genre_area',request_type="altairsite.tweens.ISmartphoneRequest"
             , renderer='altairsite.smartphone:templates/searchresult/genre_area.html')
def search_genre_area(context, request):
    # ジャンル画面のエリア検索
    form = AreaSearchForm(request.GET)
    genre = context.get_genre(form.data['genre_id'])
    query = AreaSearchQuery(area=form.data['area'], genre_id=genre.id, genre_label=genre.label)
    result = context.search_area(query, int(form.data['page']), 10)

    return {
         'query':query
        ,'result':result
        ,'helper':SmartPhoneHelper()
    }

@usersite_view_config(route_name='init_detail',request_type="altairsite.tweens.ISmartphoneRequest"
             , renderer='altairsite.smartphone:templates/searchresult/detail_search.html')
def init_detail_search(context, request):
    # 詳細検索画面表示
    form = DetailSearchForm()
    context.init_detail_search_form(form=form)

    return {
         'form':form
        ,'helper':SmartPhoneHelper()
    }

@usersite_view_config(route_name='search_detail',request_type="altairsite.tweens.ISmartphoneRequest"
             , renderer='altairsite.smartphone:templates/searchresult/detail_search.html')
def detail_search(context, request):
    # 詳細検索
    form = DetailSearchForm(request.GET)
    context.init_detail_search_form(form=form)

    genre = context.get_genre(form.data['genre_id'])
    event_open_info = EventOpenInfo(since_event_open=form.get_since_event_open(), event_open=form.get_event_open())
    sale_info = SaleInfo(sale_start=form.data['sale_start'], sale_end=form.data['sale_end'])
    perf_info = PerformanceInfo(canceled=form.data['canceled_perf'], closed=form.data['closed_perf'])

    query = DetailSearchQuery(word=form.data['word'], cond=form.data['cond'], genre=genre
        , prefectures=form.get_prefectures(), sales_segment=form.data['sales_segment'], event_open_info=event_open_info
        , sale_info=sale_info, perf_info=perf_info)
    result = context.search_detail(query, int(form.data['page']), 10)

    return {
         'form':form
        ,'result':result
        ,'helper':SmartPhoneHelper()
    }

