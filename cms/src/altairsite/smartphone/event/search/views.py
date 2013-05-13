# -*- coding:utf-8 -*-
from altairsite.config import usersite_view_config
from altairsite.smartphone.common.helper import SmartPhoneHelper
from altairsite.smartphone.event.search.forms import TopSearchForm, GenreSearchForm, AreaSearchForm, DetailSearchForm
from altairsite.smartphone.event.search.resources import SearchQuery, AreaSearchQuery, DetailSearchQuery
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

@usersite_view_config(route_name='init_detail',request_type="altairsite.tweens.ISmartphoneRequest"
             , renderer='altairsite.smartphone:templates/searchresult/detail_search.html')
def init_detail_search(context, request):
    # 詳細検索画面表示
    return {
         'form':DetailSearchForm()
        ,'helper':SmartPhoneHelper()
    }

@usersite_view_config(route_name='search_detail',request_type="altairsite.tweens.ISmartphoneRequest"
             , renderer='altairsite.smartphone:templates/searchresult/detail_search.html')
def detail_search(context, request):
    # 詳細検索
    form = DetailSearchForm(request.GET)
    query = DetailSearchQuery(word=form.data['word'], word_option=form.data['word_option'])
    result = context.search_detail(query, int(form.data['page']), 10)

    return {
         'form':form
        ,'result':result
        ,'helper':SmartPhoneHelper()
    }

"""
@usersite_view_config(route_name='detailsearchinit', request_type="altairsite.tweens.IMobileRequest"
    , renderer='altairsite.mobile:templates/detailsearch/detailsearch.mako')
def move_detailsearch(request):

    log_info("move_detailsearch", "start")
    form = DetailSearchForm(request.GET)
    form = create_genre_selectbox(request, form)
    form = create_date_selectbox(form)
    log_info("move_detailsearch", "end")

    return {'form':form}

@usersite_view_config(route_name='detailsearch', request_type="altairsite.tweens.IMobileRequest"
    , renderer='altairsite.mobile:templates/searchresult/detailsearch.mako')
def move_detailsearch_post(request):

    log_info("move_detailsearch_post", "start")
    searcher = EventSearcher(request)

    form = DetailSearchForm(request.GET)
    form = create_genre_selectbox(request, form)
    form = create_date_selectbox(form)
    form.num.data = 0

    if form.validate():
        log_info("move_detailsearch_post", "detail search start")
        qs = searcher.get_events_from_freeword(form)
        if not qs:
            log_info("move_detailsearch_post", "free word not result")
        else:
            qs = searcher.get_events_from_area(form, qs)
            qs = searcher.get_events_from_sale(form, qs)
            qs = searcher.get_events_from_start_on(form, qs)
            qs = searcher.get_events_from_salessegment(form, qs)

        log_info("move_detailsearch_post", "detail search end")

        form = get_event_paging(request=request, form=form, qs=qs)
        form = create_genre_selectbox(request, form)
        form.week.data = get_week_map()

    log_info("move_detailsearch_post", "end")
    return {'form':form}

def create_genre_selectbox(request, form):
    log_info("create_genre_selectbox", "start")
    genre_searcher = GenreSearcher(request)
    genres = genre_searcher.root.children

    form.genre.choices = []
    form.genre.choices.append([0, u'選択なし'])
    for genre in genres:
        form.genre.choices.append([genre.id, genre.label])
        for sub_genre in genre.children:
            form.genre.choices.append([sub_genre.id, u"┗ " + sub_genre.label])
    log_info("create_genre_selectbox", "end")
    return form

# 2100年まで設定可能にした
def create_date_selectbox(form):
    log_info("create_date_selectbox", "start")

    log_info("create_date_selectbox", "selectbox delete start")
    del form.year.choices[:]
    del form.since_year.choices[:]
    del form.month.choices[:]
    del form.since_month.choices[:]
    del form.day.choices[:]
    del form.since_day.choices[:]
    log_info("create_date_selectbox", "selectbox delete end")

    log_info("create_date_selectbox", "input start")
    form.since_year.choices.append(['0', '-'])
    form.year.choices.append(['0', '-'])
    form.since_month.choices.append(['0', '-'])
    form.month.choices.append(['0', '-'])
    form.since_day.choices.append(['0', '-'])
    form.day.choices.append(['0', '-'])

    today = date.today()

    for year in range(today.year, today.year + 3):
        form.since_year.choices.append([str(year), str(year)])
        form.year.choices.append([str(year), str(year)])

    for month in range(1, 13):
        form.since_month.choices.append([str(month), str(month)])
        form.month.choices.append([str(month), str(month)])

    for day in range(1, 32):
        form.since_day.choices.append([str(day), str(day)])
        form.day.choices.append([str(day), str(day)])
    log_info("create_date_selectbox", "input end")

    log_info("create_date_selectbox", "end")
    return form
"""