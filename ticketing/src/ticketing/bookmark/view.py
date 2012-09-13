# -*- coding: utf-8 -*-
from ticketing.views import BaseView

from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound

from ticketing.models import merge_session_with_post, record_to_multidict, merge_and_flush
from pyramid.url import route_path
from ticketing.fanstatic import with_bootstrap
from models import Bookmark
from forms import BookmarkForm

import sqlahelper
session = sqlahelper.get_session()

@view_defaults(decorator=with_bootstrap, permission='event_editor')
class BookmarkView(BaseView):
    @view_config(route_name='bookmark.index', renderer='ticketing:templates/bookmark/index.html')
    def index(self):
        return {
            'bookmarks' : Bookmark.find_by_organization_id(1)
        }

    @view_config(route_name='bookmark.new', request_method="GET", renderer='ticketing:templates/bookmark/edit.html')
    def new_get(self):
        f = BookmarkForm()
        return {
            'route_name' : route_path("bookmark.new", self.request),
            'form' : f
        }

    @view_config(route_name='bookmark.new', request_method="POST", renderer='ticketing:templates/bookmark/edit.html')
    def new_post(self):
        form = BookmarkForm()
        if form.validate():
            data = form.data
            record = Bookmark()
            record = merge_session_with_post(record, data)
            session.add(record)
        else:
            return {
                'form' : form
            }

    @view_config(route_name='bookmark.edit', request_method="GET", renderer='ticketing:templates/bookmark/edit.html')
    def edit_get(self):
        bookmark_id = int(self.request.matchdict.get("bookmark_id", 0))
        bookmark = Bookmark.get(bookmark_id)
        if bookmark is None:
            return HTTPNotFound("Operator id %d is not found" % bookmark_id)
        form = BookmarkForm()
        d = record_to_multidict(bookmark)
        form.process(d)
        return {
            'bookmark_id'   : bookmark_id,
            'form'          : form
        }

    @view_config(route_name='bookmark.edit', request_method="POST", renderer='ticketing:templates/bookmark/edit.html')
    def edit_post(self):
        bookmark_id = int(self.request.matchdict.get("bookmark_id", 0))
        bookmark = Bookmark.get(bookmark_id)
        if bookmark is None:
            return HTTPNotFound("Operator id %d is not found" % bookmark_id)
        form = BookmarkForm(self.request.POST)
        if form.validate():
            data = form.data
            record = merge_session_with_post(bookmark, data)
            merge_and_flush(record)
        else:
            return {
                'bookmark_id'   : bookmark_id,
                'form'          : form
            }

        return HTTPFound(location=route_path("bookmark.index", self.request, bookmark_id = bookmark_id))