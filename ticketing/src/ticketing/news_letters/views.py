# -*- coding: utf-8 -*-

import urllib

from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.url import route_path
from pyramid.response import Response

from ticketing.models import merge_session_with_post, record_to_multidict
from models import session, NewsLetter
from ticketing.views import BaseView
from ticketing.fanstatic import with_bootstrap

from forms import NewsLettersForm

import webhelpers.paginate as paginate

import logging
import os
log = logging.getLogger(__name__)

@view_defaults(decorator=with_bootstrap)
class NewsLetters(BaseView):

    @view_config(route_name='news_letters.index', renderer='ticketing:templates/news_letters/index.html')
    def index(self):
        current_page = int(self.request.params.get("page", 0))
        page_url = paginate.PageURL_WebOb(self.request)
        query = session.query(NewsLetter)
        news_letters = paginate.Page(query.order_by(NewsLetter.id), current_page, url=page_url)
        return {
            'news_letters' : news_letters
        }

    @view_config(route_name='news_letters.new', request_method="GET", renderer='ticketing:templates/news_letters/new.html')
    def new_get(self):
        f = NewsLettersForm()
        news_letter_id = int(self.request.GET.get("news_letter_id", 0)) 
        if news_letter_id:
            news_letter = NewsLetter.get(news_letter_id)
            if news_letter is None:
                return HTTPNotFound('NewsLetter not found')
            f.process(record_to_multidict(news_letter))

        return {
            'form':f
        }   

    @view_config(route_name='news_letters.new', request_method="POST", renderer='ticketing:templates/news_letters/new.html')
    def new_post(self):
        f = NewsLettersForm(self.request.POST)
        if f.validate():
            data = f.data
            record = NewsLetter()
            record = merge_session_with_post(record, data)
            NewsLetter.add(record)
            NewsLetter.save_file(1, f)
            return HTTPFound(location=route_path('news_letters.index', self.request))
        else:
            return {
                'form':f
            }

    @view_config(route_name='news_letters.show', renderer='ticketing:templates/news_letters/show.html')
    def show(self):
        news_letter_id = int(self.request.matchdict.get("news_letter_id", 0)) 
        news_letter = NewsLetter.get(news_letter_id)
        log.debug(vars(news_letter))
        if news_letter is None:
            return HTTPNotFound("news_letter id %d is not found" % news_letter_id)
        f = NewsLettersForm()

        return {
            'form' :f,
            'news_letter' : news_letter,
        }   

    @view_config(route_name='news_letters.edit', request_method="GET", renderer='ticketing:templates/news_letters/edit.html')
    def edit_get(self):
        news_letter_id = int(self.request.matchdict.get("news_letter_id", 0))
        news_letter = NewsLetter.get(news_letter_id)
        if news_letter is None:
            return HTTPNotFound("client id %d is not found" % news_letter_id)

        app_structs = record_to_multidict(news_letter)
        f = NewsLettersForm()
        f.process(app_structs)
        return {
            'form' :f,
            'news_letter' : news_letter
        }

    @view_config(route_name='news_letters.edit', request_method="POST", renderer='ticketing:templates/news_letters/edit.html')
    def edit_post(self):
        news_letter_id = int(self.request.matchdict.get("news_letter_id", 0))
        news_letter = NewsLetter.get(news_letter_id)
        if news_letter is None:
            return HTTPNotFound("client id %d is not found" % news_letter_id)

        f = NewsLettersForm(self.request.POST)
        if f.validate():
            data = f.data
            record = merge_session_with_post(news_letter, data)
            NewsLetter.update(record)
            NewsLetter.save_file(news_letter_id, f)
            return HTTPFound(location=route_path('news_letters.show', self.request, news_letter_id=news_letter.id))
        else:
            return {
                'form':f,
                'news_letter' : news_letter
            }

    @view_config(route_name='news_letters.download')
    def download(self):
        news_letter_id = int(self.request.matchdict.get("news_letter_id", 0)) 
        news_letter = NewsLetter.get(news_letter_id)
        log.debug(vars(news_letter))

        fname = news_letter.subscriber_file()
        f = open(fname)
        headers = [
            ('Content-Type', 'application/octet-stream'),
            ('Content-Disposition', 'attachment; filename=%s' % os.path.basename(fname))
        ]
        response = Response(f.read(), headers=headers)
        f.close()

        return response

