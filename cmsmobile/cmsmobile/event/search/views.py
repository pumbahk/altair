# -*- coding: utf-8 -*-
from pyramid.view import view_config
from altaircms.models import Genre
from cmsmobile.event.search.forms import SearchForm
from cmsmobile.core.searcher import EventSearcher
from cmsmobile.core.const import get_prefecture_name
from cmsmobile.core.helper import exist_value, get_week_map, get_event_paging
from cmsmobile.core.helper import log_info

class ValidationFailure(Exception):
    pass

@view_config(route_name='search', renderer='cmsmobile:templates/searchresult/search.mako')
@view_config(route_name='genresearch', renderer='cmsmobile:templates/searchresult/genresearch.mako')
def search(request):

    log_info("search", "start")
    form = SearchForm(request.GET)
    form.num.data = 0

    if form.validate():

        form.week.data = get_week_map()

        searcher = EventSearcher(request)

        log_info("search", "search event start")
        qs = searcher.get_events_from_freeword(form)
        qs = searcher.get_events_from_area(form, qs)
        qs = searcher.get_events_week_sale(form, qs)
        qs = searcher.get_events_soon_act(form, qs)
        log_info("search", "search event end")

        form = get_event_paging(request=request, form=form, qs=qs)

    # パンくずリスト用
    log_info("search", "breadcrumb create start")
    if exist_value(form.genre.data):
        form.navi_genre.data = request.allowable(Genre).filter(Genre.id==form.genre.data).first()

    if exist_value(form.sub_genre.data):
        form.navi_sub_genre.data = request.allowable(Genre).filter(Genre.id==form.sub_genre.data).first()

    if exist_value(form.area.data):
        form.navi_area.data = get_prefecture_name(form.area.data)
    log_info("search", "breadcrumb create end")

    log_info("search", "end")
    return {'form':form}
