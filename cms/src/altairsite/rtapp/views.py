# -*- coding:utf-8 -*-

import logging
logger = logging.getLogger(__name__)
from datetime import datetime
from pyramid.view import view_config
from altaircms.modellib import DBSession as session
from altaircms.event.event_info import get_event_notify_info
from pyramid.httpexceptions import HTTPNotFound
from sqlalchemy.orm.exc import NoResultFound
from . import api
from .helpers import grep_prfms_in_sales
from .builders import (
    GenreListResponseBuilder,
    PerformanceGroupListResponseBuilder,
    EventDetailResponseBuilder,
    TopPageResponseBuilder
)
import webhelpers.paginate as paginate


@view_config(route_name="api.top_page", request_method="GET", renderer='json')
def api_top_page(self, request):
    d = datetime.now()
    topcontents = api.get_topcontents(session, request, d, organization_id=8, limit=6)
    topics = api.get_topics(session, request, d, organization_id=8, limit=5)

    builder = TopPageResponseBuilder()
    res = builder.build_response(request, topcontents, topics)

    return res


@view_config(route_name="api.genre_list", request_method="GET", renderer='json')
def api_genre_list(self, request):
    genres = api.get_genre_list(session, request, organization_id=8)

    builder = GenreListResponseBuilder()
    res = builder.build_response(request, genres)

    return res


@view_config(route_name="api.performance_list", request_method="GET", renderer='json')
def api_performance_list(self, request):
    equery = api.get_performance_list_query(session, request, organization_id=8)

    events = paginate.Page(
            equery,
            page=int(request.params.get('page', 0)),
            items_per_page=50
        )

    builder = PerformanceGroupListResponseBuilder()
    res = builder.build_response(request, events.items, events.page_count)

    return res


@view_config(route_name="api.event_detail", request_method="GET", renderer='json')
def api_event_detail(self, request):
    try:
        event = api.get_event(session, request)
    except NoResultFound:
        res = HTTPNotFound()
        res.content_type = 'application/json'
        res.text = u'{"message": "event not found"}'
        return res
    performances = sorted(event.performances, key=lambda p:p.start_on, reverse=True)
    event_info = get_event_notify_info(event)
    builder = EventDetailResponseBuilder()
    res = builder.build_response(request, event, performances, event_info)
    return res


@view_config(route_name="api.bookmark_events", request_method="GET", renderer='json')
def api_bookmark_performance_list(self, request):
    equery = api.get_bookmarked_events(session, request, organization_id=8)
    #events = equery.all() if equery else []

    events = paginate.Page(
            equery,
            page=int(request.params.get('page', 0)),
            items_per_page=50
        )

    builder = PerformanceGroupListResponseBuilder()
    res = builder.build_response(request, events.items, events.page_count)

    return res
