 # -*- coding: utf-8 -*-

from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.url import route_path

from ticketing.models import merge_session_with_post, record_to_multidict
from ..models import session, Event, Performance
from ticketing.views import BaseView
from ticketing.fanstatic import with_bootstrap


import webhelpers.paginate as paginate

@view_defaults(decorator=with_bootstrap)
class Performances(BaseView):
    @view_config(route_name='performances.show', renderer='ticketing:templates/performances/show.html')
    def show(self):
        performance_id = int(self.request.matchdict.get("performance_id", 0))
        performance = Performance.get(performance_id)

        return {
            'performance' : performance
        }
