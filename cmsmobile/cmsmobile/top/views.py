# -*- coding: utf-8 -*-

from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound

from cmsmobile.core.models import Host
from cmsmobile.core.views import BaseView
from cmsmobile.core.fanstatic import with_bootstrap

import webhelpers.paginate as paginate

@view_defaults(decorator=with_bootstrap, permission='event_editor')
class Top(BaseView):

    @view_config(route_name='top.search', renderer='cmsmobile:templates/search/search.mako')
    def search(self):
        current_page = int(self.request.params.get("page", 0))
        area = int(self.request.params.get("area", 0))
        if area:
            pass
        return {
        }

    @view_config(route_name='top.genre', request_method="POST", renderer='cmsmobile:templates/genre/genre.mako')
    def move_genre(self):
        current_page = int(self.request.params.get("page", 0))
        genre = self.request.params.get("genre", None)
        page_url = paginate.PageURL_WebOb(self.request)
        return {
            'genre':genre,
        }

    @view_config(route_name='top.detail', renderer='cmsmobile:templates/detail/detail.mako')
    def move_detail(self):
        event_id = self.request.params.get("event_id", None)
        return {
        }

    @view_config(route_name='top.inquiry', renderer='cmsmobile:templates/inquiry/inquiry.mako')
    def move_inquiry(self):
        return {
        }

    @view_config(route_name='top.help', renderer='cmsmobile:templates/help/help.mako')
    def move_help(self):
        return {
        }

    @view_config(route_name='top.order', renderer='cmsmobile:templates/order/order.mako')
    def move_order(self):
        return {
        }

