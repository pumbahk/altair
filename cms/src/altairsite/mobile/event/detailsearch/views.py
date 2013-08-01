# -*- coding: utf-8 -*-
from altaircms.genre.searcher import GenreSearcher
from altairsite.config import mobile_site_view_config
from altairsite.mobile.event.detailsearch.forms import DetailSearchForm
from altairsite.mobile.core.helper import get_event_paging, get_week_map, log_info
from altairsite.mobile.core.searcher import create_event_searcher
from datetime import date

@mobile_site_view_config(route_name='detailsearchinit', request_type="altairsite.tweens.IMobileRequest"
    , renderer='altairsite.mobile:templates/detailsearch/detailsearch.mako')
def move_detailsearch(request):

    log_info("move_detailsearch", "start")
    form = DetailSearchForm(request.GET)
    form = create_genre_selectbox(request, form)
    form = create_date_selectbox(form)
    log_info("move_detailsearch", "end")

    return {'form':form}

@mobile_site_view_config(route_name='detailsearch', request_type="altairsite.tweens.IMobileRequest"
    , renderer='altairsite.mobile:templates/searchresult/detailsearch.mako')
def move_detailsearch_post(request):

    log_info("move_detailsearch_post", "start")

    form = DetailSearchForm(request.GET)
    form = create_genre_selectbox(request, form)
    form = create_date_selectbox(form)
    form.num.data = 0

    if form.validate():
        log_info("move_detailsearch_post", "detail search start")
        searcher = create_event_searcher(request, form)
        qs = searcher.get_events_from_freeword(form)
        qs = searcher.get_events_from_area(form, qs)
        qs, form = searcher.get_events_from_start_on(form, qs)
        if qs:
            # 以下は絞り込み条件
            qs = searcher.get_events_from_sale(form, qs)
            qs = searcher.get_events_from_salessegment(form, qs)

        log_info("move_detailsearch_post", "detail search end")

        form = get_event_paging(request=request, form=form, qs=qs)
        form = create_genre_selectbox(request, form)
        form.week.data = get_week_map()
        form.path.data = request.route_path('detailsearch')

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
    form.since_year.choices.append(['-', '-'])
    form.year.choices.append(['-', '-'])
    form.since_month.choices.append(['-', '-'])
    form.month.choices.append(['-', '-'])
    form.since_day.choices.append(['-', '-'])
    form.day.choices.append(['-', '-'])

    today = date.today() ##受付formなのでaltair.nowではなくてok

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
