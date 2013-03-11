# -*- coding: utf-8 -*-
from pyramid.view import view_config
from cmsmobile.event.detailsearch.forms import DetailSearchForm
from cmsmobile.core.searcher import EventSearcher
from altaircms.genre.searcher import GenreSearcher
from cmsmobile.core.helper import get_event_paging, get_week_map

@view_config(route_name='detailsearch', request_method="GET",
             renderer='cmsmobile:templates/detailsearch/detailsearch.mako')
def move_detailsearch(request):

    form = DetailSearchForm()
    form = create_genre_selectbox(request, form)
    form = create_date_selectbox(form)

    return {'form':form}

@view_config(route_name='detailsearch', request_method="POST",
             renderer='cmsmobile:templates/searchresult/detailsearch.mako')
def move_detailsearch_post(request):

    searcher = EventSearcher(request)

    form = DetailSearchForm(request.POST)
    form.num.data = 0

    if form.validate():
        qs = searcher.get_events_from_freeword(form)
        qs = searcher.get_events_from_area(form, qs)
        qs = searcher.get_events_from_sale(form, qs)
        qs = searcher.get_events_from_start_on(form, qs)
        qs = searcher.get_events_from_salessegment(form, qs)

        form = get_event_paging(request=request, form=form, qs=qs)
        form = create_genre_selectbox(request, form)
        form.week.data = get_week_map()

    return {'form':form}

def create_genre_selectbox(request, form):
    genre_searcher = GenreSearcher(request)
    genres = genre_searcher.root.children

    form.genre.choices = []
    form.genre.choices.append([0, u'選択なし'])
    for genre in genres:
        form.genre.choices.append([genre.id, genre.label])
        for sub_genre in genre.children:
            form.genre.choices.append([sub_genre.id, u"┗ " + sub_genre.label])
    return form

# 2100年まで設定可能にした
def create_date_selectbox(form):
    del form.year.choices[:]
    del form.since_year.choices[:]
    del form.month.choices[:]
    del form.since_month.choices[:]
    del form.day.choices[:]
    del form.since_day.choices[:]

    form.since_year.choices.append([0, '-'])
    form.year.choices.append([0, '-'])
    form.since_month.choices.append([0, '-'])
    form.month.choices.append([0, '-'])
    form.since_day.choices.append([0, '-'])
    form.day.choices.append([0, '-'])

    for year in range(2013, 2100):
        form.since_year.choices.append([year, year])
        form.year.choices.append([year, year])

    for month in range(1, 13):
        form.since_month.choices.append([month, month])
        form.month.choices.append([month, month])

    for day in range(1, 32):
        form.since_day.choices.append([day, day])
        form.day.choices.append([day, day])
    return form
