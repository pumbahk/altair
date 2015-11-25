# -*- coding:utf-8 -*-

import logging
logger  = logging.getLogger(__name__)
from datetime import datetime
from pyramid.view import view_config
from altaircms.modellib import DBSession as session
from . import api
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
    topcontents = api.get_topcontents(session, request, d, organization_id=8, limit=5)
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
    pquery = api.get_performance_list_query(session, request, organization_id=8)
    performances = paginate.Page(
            pquery,
            page=int(request.params.get('page', 0)),
            items_per_page=50
        )

    builder = PerformanceGroupListResponseBuilder()
    res = builder.build_response(request, performances.items)

    return res

@view_config(route_name="api.event_detail", request_method="GET", renderer='json')
def api_event_detail(self, request):
    event = api.get_event(session, request)
    widget_summary = api.get_widget_summary(session, event)
    builder = EventDetailResponseBuilder()
    res = builder.build_response(request, event, widget_summary)
    return res
