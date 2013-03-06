# -*- coding: utf-8 -*-

from pyramid.view import view_config
from cmsmobile.event.detailsearch.forms import DetailSearchForm
from cmsmobile.core.searcher import EventSearcher
import webhelpers.paginate as paginate
from cmsmobile.core.helper import exist_value
from altaircms.genre.searcher import GenreSearcher
from datetime import date

@view_config(route_name='detailsearch', request_method="GET", renderer='cmsmobile:templates/detailsearch/detailsearch.mako')
def move_detailsearch(request):

    form = DetailSearchForm()

    # genre select box
    form = create_genre_selectbox(request, form)

    # date select box
    form = create_date_selectbox(form)
    # form = select_date_selectbox(form)

    return {
        'form':form
    }

@view_config(route_name='detailsearch', request_method="POST", renderer='cmsmobile:templates/searchresult/detailsearch.mako')
def move_detailsearch_post(request):

    searcher = EventSearcher(request)

    form = DetailSearchForm(request.POST)

    # freeword, genre, subgenre
    qs = searcher.get_events_from_freeword(form)

    # 地域検索
    qs = searcher.get_events_from_area(form, qs)

    # 発売状況
    qs = searcher.get_events_from_sale(form, qs)

    # 公演日期間
    qs = searcher.get_events_start_on(form, qs)

    print qs

    # paging
    events = None
    form.num.data = 0
    if qs:
        events = qs.all()
        if events:
            form.num.data = len(events)
            items_per_page = 10
            events = paginate.Page(
                events,
                form.page.data,
                items_per_page,
                url=paginate.PageURL_WebOb(request)
            )
            if form.num.data % items_per_page == 0:
                form.page_num.data = form.num.data / items_per_page
            else:
                form.page_num.data = form.num.data / items_per_page + 1

    # genre select box
    create_genre_selectbox(request, form)

    return {
        'events':events,
        'form':form
    }

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

def select_date_selectbox(form):
    today = date.today()
    form.year.default = today.year
    form.since_year.default = today.year
    form.month.default = today.month
    form.since_month.default = today.month
    form.day.default = today.day
    form.since_day.default = today.day
    form.process()
    return form