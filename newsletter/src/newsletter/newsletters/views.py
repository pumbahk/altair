# -*- coding: utf-8 -*-

import urllib
import os

import webhelpers.paginate as paginate

from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.url import route_path
from pyramid.response import Response

from newsletter.models import merge_session_with_post, record_to_multidict
from newsletter.views import BaseView
from newsletter.fanstatic import with_bootstrap
from newsletter.newsletters.models import session, Newsletter
from newsletter.newsletters.forms import NewslettersForm

import logging
log = logging.getLogger(__name__)

@view_defaults(decorator=with_bootstrap)
class Newsletters(BaseView):

    @view_config(route_name='newsletters.index', renderer='newsletter:templates/newsletters/index.html')
    def index(self):
        current_page = int(self.request.params.get('page', 1))
        sort = self.request.GET.get('sort', 'id')
        direction = self.request.GET.get('direction', 'asc')
        if direction not in ['asc', 'desc']:
            direction = 'asc'

        page_url = paginate.PageURL_WebOb(self.request)
        query = session.query(Newsletter).order_by(sort + ' ' + direction)
        newsletters = paginate.Page(query, page=current_page, items_per_page=10, url=page_url)

        f = NewslettersForm()
        return {
            'form' : f,
            'newsletters' : newsletters
        }

    @view_config(route_name='newsletters.copy', request_method='GET', renderer='newsletter:templates/newsletters/edit.html')
    def copy(self):
        f = NewslettersForm()

        id = int(self.request.matchdict.get('id', 0)) 
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

    @view_config(route_name='newsletters.new', request_method='GET', renderer='newsletter:templates/newsletters/edit.html')
    def new_get(self):
        f = NewslettersForm()
        return {
            'form' : f
        }   

    @view_config(route_name='newsletters.new', request_method='POST', renderer='newsletter:templates/newsletters/edit.html')
    def new_post(self):
        f = NewslettersForm(self.request.POST)

        if f.validate():
            record = merge_session_with_post(Newsletter(), f.data)
            id = Newsletter.add(record)

            file = f.subscriber_file.data.file if f.subscriber_file.data != '' else None
            Newsletter.save_file(id, file)

            self.request.session.flash(u'メールマガジンを登録しました')
            return HTTPFound(location=route_path('newsletters.index', self.request))
        else:
            return {
                'form' : f
            }

    @view_config(route_name='newsletters.show', renderer='newsletter:templates/newsletters/show.html')
    def show(self):
        id = int(self.request.matchdict.get('id', 0)) 
        newsletter = Newsletter.get(id)
        if newsletter is None:
            return HTTPNotFound('newsletter id %d is not found' % id)

        f = NewslettersForm()
        return {
            'form' : f,
            'newsletter' : newsletter,
        }   

    @view_config(route_name='newsletters.edit', request_method='GET', renderer='newsletter:templates/newsletters/edit.html')
    def edit_get(self):
        id = int(self.request.matchdict.get('id', 0))
        newsletter = Newsletter.get(id)
        if newsletter is None:
            return HTTPNotFound('client id %d is not found' % id)

        f = NewslettersForm()
        f.process(record_to_multidict(newsletter))
        return {
            'form' : f,
            'newsletter' : newsletter
        }

    @view_config(route_name='newsletters.edit', request_method='POST', renderer='newsletter:templates/newsletters/edit.html')
    def edit_post(self):
        id = int(self.request.matchdict.get('id', 0))
        newsletter = Newsletter.get(id)
        if newsletter is None:
            return HTTPNotFound('client id %d is not found' % id)

        f = NewslettersForm(self.request.POST)
        if f.validate():
            record = merge_session_with_post(newsletter, f.data)
            Newsletter.update(record)

            file = f.subscriber_file.data.file if f.subscriber_file.data != '' else None
            Newsletter.save_file(id, file)

            self.request.session.flash(u'メールマガジンを保存しました')
            return HTTPFound(location=route_path('newsletters.show', self.request, id=newsletter.id))
        else:
            return {
                'form' : f,
                'newsletter' : newsletter
            }

    @view_config(route_name='newsletters.delete')
    def delete(self):
        id = int(self.request.matchdict.get('id', 0))
        newsletter = Newsletter.get(id)
        if newsletter is None:
            return HTTPNotFound('newsletter id %d is not found' % id)

        Newsletter.delete(newsletter)

        self.request.session.flash(u'メールマガジンを削除しました')
        return HTTPFound(location=route_path('newsletters.index', self.request))

    @view_config(route_name='newsletters.download')
    def download(self):
        id = int(self.request.matchdict.get('id', 0)) 
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

    @view_config(route_name='newsletters.test_mail')
    def test_mail(self):
        id = int(self.request.matchdict.get('id', 0)) 
        recipient= self.request.POST.get('recipient')
        Newsletter.test_mail(id, recipient)

        self.request.session.flash(u'テスト送信しました')
        return HTTPFound(location=route_path('newsletters.show', self.request, id=id))

    @view_config(route_name='newsletters.htmlmail')
    def htmlmail(self):
        id = int(self.request.matchdict.get('id', 0)) 
        newsletter = Newsletter.get(id)

        response = Response(newsletter.description)
        return response

