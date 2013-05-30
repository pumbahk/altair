# -*- coding:utf-8 -*-
from .forms import TopSearchForm, GenreSearchForm, AreaSearchForm, DetailSearchForm, HotwordSearchForm
from .search_query import SearchQuery, AreaSearchQuery, HotwordSearchQuery, DetailSearchQuery, EventOpenInfo, SaleInfo\
    , PerformanceInfo
from ..common.const import SalesEnum
from ..common.helper import SmartPhoneHelper
from altairsite.config import usersite_view_config

from pyramid.renderers import render_to_response

@usersite_view_config(route_name='search',request_type="altairsite.tweens.ISmartphoneRequest"
             , renderer='altairsite.smartphone:templates/searchresult/search.html')
def search(context, request):
    # トップ画面の検索
    form = TopSearchForm(request.GET)

    if not form.validate():
        render_param = context.get_top_render_param()
        render_param['form'] = form
        return render_to_response('altairsite.smartphone:templates/top.html', render_param, request=request)

    query = SearchQuery(form.data['word'], None, form.data['sale'], None)
    page = form.data['page'] if form.data['page'] else 1
    result = context.search(query, int(page), 10)

    return {
         'form':form
        ,'result':result
        ,'helper':SmartPhoneHelper()
    }

@usersite_view_config(route_name='search_genre',request_type="altairsite.tweens.ISmartphoneRequest"
             , renderer='altairsite.smartphone:templates/searchresult/genre.html')
def genre_search(context, request):
    # ジャンル画面の検索
    form = GenreSearchForm(request.GET)
    search_word = form.data['word']

    if not form.validate():
        render_param = context.get_genre_render_param()
        render_param['form'] = form
        return render_to_response('altairsite.smartphone:templates/genre/genre.html', render_param, request=request)

    if form.data['sale'] == SalesEnum.GENRE.v:
        genre = context.get_genre(form.data['genre_id'])
        query = SearchQuery(search_word, genre, SalesEnum.GENRE.v, None)
    else:
        query = SearchQuery(search_word, None, SalesEnum.ON_SALE.v, None)

    page = form.data['page'] if form.data['page'] else 1
    result = context.search(query, int(page), 10)

    return {
         'form':form
        ,'genre':genre
        ,'result':result
        ,'helper':SmartPhoneHelper()
    }

@usersite_view_config(route_name='search_subsubgenre',request_type="altairsite.tweens.ISmartphoneRequest"
             , renderer='altairsite.smartphone:templates/searchresult/subgenre.html')
def subsubgenre_search(context, request):
    # サブサブジャンルは検索結果
    return context.get_subsubgenre_render_param(genre_id=None)

@usersite_view_config(route_name='search_area',request_type="altairsite.tweens.ISmartphoneRequest"
             , renderer='altairsite.smartphone:templates/searchresult/area.html')
def search_area(context, request):
    # トップ画面のエリア検索
    form = AreaSearchForm(request.GET)
    query = AreaSearchQuery(area=form.data['area'], genre=None, genre_label=None)
    result = context.search_area(query, int(form.data['page']), 10)

    return {
         'result':result
        ,'helper':SmartPhoneHelper()
    }

@usersite_view_config(route_name='search_genre_area',request_type="altairsite.tweens.ISmartphoneRequest"
             , renderer='altairsite.smartphone:templates/searchresult/genre_area.html')
def search_genre_area(context, request):
    # ジャンル画面のエリア検索
    form = AreaSearchForm(request.GET)
    genre = context.get_genre(form.data['genre_id'])
    query = AreaSearchQuery(area=form.data['area'], genre=genre, genre_label=genre.label)
    result = context.search_area(query, int(form.data['page']), 10)

    return {
         'result':result
        ,'genre':genre
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

    if not form.validate():
        return {
             'form':form
            ,'result':None
            ,'helper':SmartPhoneHelper()
        }

    event_open_info = EventOpenInfo(since_event_open=form.get_since_event_open(), event_open=form.get_event_open())
    sale_info = SaleInfo(sale_start=form.data['sale_start'], sale_end=form.data['sale_end'])
    perf_info = PerformanceInfo(canceled=form.data['canceled_perf'], closed=form.data['closed_perf'])
    query = DetailSearchQuery(word=form.data['word'], cond=form.data['cond'], genre_music=form.data['genre_music']
        , genre_sports=form.data['genre_sports'], genre_stage=form.data['genre_stage'], genre_event=form.data['genre_event']
        , pref_hokkaido=form.data['pref_hokkaido'], pref_syutoken=form.data['pref_syutoken'], pref_koshinetsu=form.data['pref_koshinetsu']
        , pref_kinki=form.data['pref_kinki'], pref_chugoku=form.data['pref_chugoku'], pref_kyusyu=form.data['pref_kyusyu']
        , sales_segment=form.data['sales_segment'], event_open_info=event_open_info
        , sale_info=sale_info, perf_info=perf_info, genres_label=context.get_genres_label(form)
        , prefectures_label=context.get_prefectures_label(form))
    page = form.data['page'] if form.data['page'] else 1
    result = context.search_detail(query, int(page), 10)

    return {
         'form':form
        ,'result':result
        ,'helper':SmartPhoneHelper()
    }

@usersite_view_config(route_name='hotword',request_type="altairsite.tweens.ISmartphoneRequest"
             , renderer='altairsite.smartphone:templates/searchresult/hotword.html')
def move_hotword(context, request):
    form = HotwordSearchForm(request.GET)
    hotword = context.get_hotword_from_id(form.data['hotword_id'])
    query = HotwordSearchQuery(hotword=hotword)
    page = form.data['page'] if form.data['page'] else 1
    result = context.search_hotword(query=query, page=page, per=10)

    return {
         'result':result
        ,'helper':SmartPhoneHelper()
    }
