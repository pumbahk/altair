# -*- coding: utf-8 -*-

from pyramid.view import view_config
from cmsmobile.event.detailsearch.forms import DetailSearchForm
from cmsmobile.core.searcher import EventSearcher
import webhelpers.paginate as paginate

@view_config(route_name='detailsearch', request_method="GET", renderer='cmsmobile:templates/detailsearch/detailsearch.mako')
def move_detailsearch(request):

    form = DetailSearchForm()

    return {
        'form':form
    }

@view_config(route_name='detailsearch', request_method="POST", renderer='cmsmobile:templates/searchresult/detailsearch.mako')
def move_detailsearch_post(request):

    searcher = EventSearcher()

    form = DetailSearchForm(request.POST)

    # freeword, genre, subgenre
    #qs = searcher.get_events_from_freeword(request, form)

    # 地域検索
    qs = searcher.get_events_from_area(form,qs=None)

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

    return {
        'events':events,
        'form':form
    }
