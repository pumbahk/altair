 # -*- coding: utf-8 -*-

from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.url import route_path

from ticketing.models import merge_session_with_post, record_to_multidict
from ticketing.core.models import Event
from ticketing.views import BaseView
from ticketing.fanstatic import with_bootstrap

import webhelpers.paginate as paginate

import sqlahelper
session = sqlahelper.get_session()

@view_defaults(decorator=with_bootstrap, permission='event_editor')
class Dashboard(BaseView):

    @view_config(route_name='dashboard.index', renderer='ticketing:templates/dashboard/index.html')
    def index(self):
        current_page = int(self.request.params.get("page", 0))
        page_url = paginate.PageURL_WebOb(self.request)
        query = session.query(Event)
        events = paginate.Page(query.order_by(Event.id), current_page, url=page_url)
        return {
            'events'        : events
        }
