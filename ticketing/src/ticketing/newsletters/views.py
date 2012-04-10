# -*- coding: utf-8 -*-

import urllib

from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.url import route_path
from pyramid.response import Response

from ticketing.models import merge_session_with_post, record_to_multidict
from ticketing.views import BaseView
from ticketing.fanstatic import with_fanstatic_jqueries
from models import session, Newsletter

from forms import NewslettersForm

import webhelpers.paginate as paginate

import logging
import os
log = logging.getLogger(__name__)

@view_defaults(decorator=with_fanstatic_jqueries)
class Newsletters(BaseView):

    @view_config(route_name='newsletters.index', renderer='ticketing:templates/newsletters/index.html')
    def index(self):
        f = NewslettersForm()
        current_page = int(self.request.params.get("page", 1))
        page_url = paginate.PageURL_WebOb(self.request)

        sort = 'id'
        if self.request.GET.get("sort"):
            sort = self.request.GET.get("sort")
        direction = 'asc'
        if self.request.GET.get("direction") and self.request.GET.get("direction") in ["asc", "desc"]:
            direction = self.request.GET.get("direction")
        query = session.query(Newsletter).order_by(sort + ' ' + direction)
        newsletters = paginate.Page(query, page=current_page, items_per_page=10, url=page_url)

        return {
            'form' : f,
            'newsletters' : newsletters
        }

    @view_config(route_name='newsletters.copy', request_method="GET", renderer='ticketing:templates/newsletters/edit.html')
    def copy(self):
        f = NewslettersForm()
        id = int(self.request.matchdict.get("id", 0)) 
        if id:
            newsletter = Newsletter.get(id)
            if newsletter is None:
                return HTTPNotFound('Newsletter not found')
            newsletter = record_to_multidict(newsletter)
            newsletter.pop('id')
            newsletter.pop('status')
            f.process(newsletter)

        return {
            'form' : f
        }   

    @view_config(route_name='newsletters.new', request_method="GET", renderer='ticketing:templates/newsletters/edit.html')
    def new_get(self):
        f = NewslettersForm()

        return {
            'form' : f
        }   

    @view_config(route_name='newsletters.new', request_method="POST", renderer='ticketing:templates/newsletters/edit.html')
    def new_post(self):
        f = NewslettersForm(self.request.POST)
        if f.validate():
            data = f.data
            record = Newsletter()
            record = merge_session_with_post(record, data)
            Newsletter.add(record)
            Newsletter.save_file(1, f)

            self.request.session.flash(u'メールマガジンを登録しました')
            return HTTPFound(location=route_path('newsletters.index', self.request))
        else:
            return {
                'form' : f
            }

    @view_config(route_name='newsletters.show', renderer='ticketing:templates/newsletters/show.html')
    def show(self):
        id = int(self.request.matchdict.get("id", 0)) 
        newsletter = Newsletter.get(id)
        if newsletter is None:
            return HTTPNotFound("newsletter id %d is not found" % id)
        f = NewslettersForm()

        return {
            'form' : f,
            'newsletter' : newsletter,
        }   

    @view_config(route_name='newsletters.edit', request_method="GET", renderer='ticketing:templates/newsletters/edit.html')
    def edit_get(self):
        id = int(self.request.matchdict.get("id", 0))
        newsletter = Newsletter.get(id)
        if newsletter is None:
            return HTTPNotFound("client id %d is not found" % id)

        app_structs = record_to_multidict(newsletter)
        f = NewslettersForm()
        f.process(app_structs)
        return {
            'form' : f,
            'newsletter' : newsletter
        }

    @view_config(route_name='newsletters.edit', request_method="POST", renderer='ticketing:templates/newsletters/edit.html')
    def edit_post(self):
        id = int(self.request.matchdict.get("id", 0))
        newsletter = Newsletter.get(id)
        if newsletter is None:
            return HTTPNotFound("client id %d is not found" % id)

        f = NewslettersForm(self.request.POST)
        if f.validate():
            data = f.data
            record = merge_session_with_post(newsletter, data)
            Newsletter.update(record)
            Newsletter.save_file(id, f)

            self.request.session.flash(u'メールマガジンを保存しました')
            return HTTPFound(location=route_path('newsletters.show', self.request, id=newsletter.id))
        else:
            return {
                'form' : f,
                'newsletter' : newsletter
            }

    @view_config(route_name='newsletters.delete')
    def delete(self):
        id = int(self.request.matchdict.get("id", 0)) 
        newsletter = Newsletter.get(id)
        if newsletter is None:
            return HTTPNotFound("newsletter id %d is not found" % id)
        Newsletter.delete(newsletter)

        self.request.session.flash(u'メールマガジンを削除しました')
        return HTTPFound(location=route_path('newsletters.index', self.request))

    @view_config(route_name='newsletters.download')
    def download(self):
        id = int(self.request.matchdict.get("id", 0)) 
        newsletter = Newsletter.get(id)

        fname = os.path.join(Newsletter.subscriber_dir(), newsletter.subscriber_file())
        f = open(fname)
        headers = [
            ('Content-Type', 'application/octet-stream'),
            ('Content-Disposition', 'attachment; filename=%s' % os.path.basename(fname))
        ]
        response = Response(f.read(), headers=headers)
        f.close()

        return response

    @view_config(route_name='newsletters.htmlmail')
    def htmlmail(self):
        id = int(self.request.matchdict.get("id", 0)) 
        newsletter = Newsletter.get(id)
        response = Response(newsletter.description)

        return response

