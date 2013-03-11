# -*- coding: utf-8 -*-
from pyramid.view import view_config
from cmsmobile.event.detailsearch.forms import DetailSearchForm
from cmsmobile.core.searcher import EventSearcher
from altaircms.genre.searcher import GenreSearcher
from cmsmobile.core.helper import get_event_paging, get_week_map
from cmsmobile.core.helper import log_info

@view_config(route_name='detailsearch', request_method="GET",
             renderer='cmsmobile:templates/detailsearch/detailsearch.mako')
def move_detailsearch(request):

    log_info("move_detailsearch", "start")
    form = DetailSearchForm()
    form = create_genre_selectbox(request, form)
    form = create_date_selectbox(form)
    log_info("move_detailsearch", "end")

    return {'form':form}

@view_config(route_name='detailsearch', request_method="POST",
             renderer='cmsmobile:templates/searchresult/detailsearch.mako')
def move_detailsearch_post(request):

    log_info("move_detailsearch_post", "start")
    searcher = EventSearcher(request)

    form = DetailSearchForm(request.POST)
    form = create_genre_selectbox(request, form)
    form = create_date_selectbox(form)
    form.num.data = 0

    if form.validate():
        log_info("move_detailsearch_post", "detail search start")
        qs = searcher.get_events_from_freeword(form)
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

    log_info("create_date_selectbox", "selectbox deelte start")
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

    for year in range(2013, 2100):
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
