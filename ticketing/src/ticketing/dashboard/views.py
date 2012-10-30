 # -*- coding: utf-8 -*-

from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound

from ticketing.models import merge_session_with_post, record_to_multidict
from ticketing.core.models import Event
from ticketing.views import BaseView
from ticketing.fanstatic import with_bootstrap

import webhelpers.paginate as paginate

@view_defaults(decorator=with_bootstrap, permission='event_editor')
class Dashboard(BaseView):

    @view_config(route_name='dashboard.index', renderer='ticketing:templates/dashboard/index.html')
    def index(self):
        current_page = int(self.request.params.get("page", 0))
        page_url = paginate.PageURL_WebOb(self.request)
        query = Event.filter_by(organization_id=self.context.user.organization_id)
        events = paginate.Page(query.order_by(Event.id), current_page, url=page_url)
        return {
            'events':events
        }
