# -*- coding:utf-8 -*-
from .forms import TopSearchForm, GenreSearchForm, AreaSearchForm, DetailSearchForm, HotwordSearchForm
from .search_query import SearchQuery, AreaSearchQuery, HotwordSearchQuery, DetailSearchQuery, EventOpenInfo, SaleInfo\
    , PerformanceInfo
from ..common.const import SalesEnum, get_areas
from ..common.helper import SmartPhoneHelper
from altairsite.config import smartphone_site_view_config
from altairsite.separation import selectable_renderer, enable_search_function

from pyramid.renderers import render_to_response

@smartphone_site_view_config(route_name='smartphone.search',request_type="altair.mobile.interfaces.ISmartphoneRequest", custom_predicates=(enable_search_function, )
             , renderer=selectable_renderer('altairsite.smartphone:templates/%(prefix)s/searchresult/search.html'))
def search(context, request):
    # トップ画面の検索
    form = TopSearchForm(request.GET)

    if not form.validate():
        render_param = context.get_top_render_param()
        render_param['form'] = form
        return render_to_response(selectable_renderer('altairsite.smartphone:templates/%(prefix)s/top.html'), render_param, request=request)

    query = SearchQuery(form.data['word'], None, form.data['sale'], None)
    page = form.data['page'] if form.data['page'] else 1
    result = context.search(query, int(page), 10)

    return {
         'form':form
        ,'result':result
        ,'areas':get_areas()
        ,'helper':SmartPhoneHelper()
    }

@smartphone_site_view_config(route_name='smartphone.search_genre',request_type="altair.mobile.interfaces.ISmartphoneRequest", custom_predicates=(enable_search_function, )
             , renderer=selectable_renderer('altairsite.smartphone:templates/%(prefix)s/searchresult/genre.html'))
def genre_search(context, request):
    # ジャンル画面の検索
    form = GenreSearchForm(request.GET)
    search_word = form.data['word']
    genre_id = form.data['genre_id']
    genre = context.get_genre(form.data['genre_id'])

    if not form.validate():
        render_param = context.get_genre_render_param(genre_id)
        render_param['form'] = form
        return render_to_response(selectable_renderer('altairsite.smartphone:templates/%(prefix)s/genre/genre.html'), render_param, request=request)

    if form.data['sale'] == SalesEnum.GENRE.v:
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

@smartphone_site_view_config(route_name='smartphone.search_subsubgenre',request_type="altair.mobile.interfaces.ISmartphoneRequest", custom_predicates=(enable_search_function, )
             , renderer=selectable_renderer('altairsite.smartphone:templates/%(prefix)s/searchresult/subgenre.html'))
def subsubgenre_search(context, request):
    # サブサブジャンルは検索結果
    return context.get_subsubgenre_render_param(genre_id=None)

@smartphone_site_view_config(route_name='smartphone.search_area',request_type="altair.mobile.interfaces.ISmartphoneRequest", custom_predicates=(enable_search_function, )
             , renderer=selectable_renderer('altairsite.smartphone:templates/%(prefix)s/searchresult/area.html'))
def search_area(context, request):
    # トップ画面のエリア検索
    form = AreaSearchForm(request.GET)
    query = AreaSearchQuery(area=form.data['area'], genre=None, genre_label=form.word.data)
    result = context.search_area(query, int(form.data['page']), 10)

    return {
         'result':result
        ,'helper':SmartPhoneHelper()
    }

@smartphone_site_view_config(route_name='smartphone.search_genre_area',request_type="altair.mobile.interfaces.ISmartphoneRequest", custom_predicates=(enable_search_function, )
             , renderer=selectable_renderer('altairsite.smartphone:templates/%(prefix)s/searchresult/genre_area.html'))
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

@smartphone_site_view_config(route_name='smartphone.init_detail',request_type="altair.mobile.interfaces.ISmartphoneRequest", custom_predicates=(enable_search_function, )
             , renderer=selectable_renderer('altairsite.smartphone:templates/%(prefix)s/searchresult/detail_search.html'))
def init_detail_search(context, request):
    # 詳細検索画面表示
    form = DetailSearchForm()
    context.init_detail_search_form(form=form)

    return {
         'form':form
        ,'helper':SmartPhoneHelper()
    }

@smartphone_site_view_config(route_name='smartphone.search_detail',request_type="altair.mobile.interfaces.ISmartphoneRequest", custom_predicates=(enable_search_function, )
             , renderer=selectable_renderer('altairsite.smartphone:templates/%(prefix)s/searchresult/detail_search.html'))
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

    since_event_open, event_open = form.get_event_open()
    form.update_form(since_event_open, event_open)
    event_open_info = EventOpenInfo(since_event_open=since_event_open, event_open=event_open)
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

@smartphone_site_view_config(route_name='smartphone.hotword',request_type="altair.mobile.interfaces.ISmartphoneRequest"
             , renderer=selectable_renderer('altairsite.smartphone:templates/%(prefix)s/searchresult/hotword.html'))
def move_hotword(context, request):
    form = HotwordSearchForm(request.GET)
    hotword = context.get_hotword_from_id(form.data['hotword_id'])
    query = HotwordSearchQuery(hotword=hotword)
    page = form.data['page'] if form.data['page'] else 1
    result = context.search_hotword(query=query, page=page, per=10)

    return {
         'result':result
        ,'genre_id':form.data['genre_id']
        ,'helper':SmartPhoneHelper()
    }
