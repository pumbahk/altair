# -*- coding: utf-8 -*-

from pyramid.view import view_config
import webhelpers.paginate as paginate
from cmsmobile.event.search.forms import SearchForm
from cmsmobile.core.searcher import EventSearcher
from cmsmobile.core.const import get_prefecture_name
from altaircms.models import Genre
from cmsmobile.core.helper import exist_value

class ValidationFailure(Exception):
    pass

@view_config(route_name='search', renderer='cmsmobile:templates/searchresult/search.mako')
@view_config(route_name='genresearch', renderer='cmsmobile:templates/searchresult/genresearch.mako')
def search(request):

    form = SearchForm(request.GET)
    searcher = EventSearcher()

    # freeword, genre, subgenre
    qs = searcher.get_events_from_freeword(request, form)

    # 地域検索
    qs = searcher.get_events_from_area(form, qs)

    # week_sale
    qs = searcher.get_events_week_sale(form, qs)

    # paging
    events = None
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

    # genre
    genre = None
    if exist_value(form.genre.data):
        genre = request.allowable(Genre).filter(Genre.id==form.genre.data).first()

    # subgenre
    subgenre = None
    if exist_value(form.sub_genre.data):
        subgenre = request.allowable(Genre).filter(Genre.id==form.sub_genre.data).first()

    # areaname
    areaname = None
    if exist_value(form.area.data):
        areaname = get_prefecture_name(form.area.data)

    return {
         'dispgenre':genre
        ,'dispsubgenre':subgenre
        ,'disparea':areaname
        ,'events':events
        ,'form':form
    }
