# -*- coding: utf-8 -*-

from pyramid.view import view_config
from cmsmobile.event.detailsearch.forms import DetailSearchForm
from cmsmobile.core.searcher import EventSearcher
import webhelpers.paginate as paginate
from cmsmobile.core.helper import exist_value
from altaircms.genre.searcher import GenreSearcher

@view_config(route_name='detailsearch', request_method="GET", renderer='cmsmobile:templates/detailsearch/detailsearch.mako')
def move_detailsearch(request):

    form = DetailSearchForm()

    # genre select box
    create_genre_selectbox(request, form)

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