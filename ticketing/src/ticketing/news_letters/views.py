 # -*- coding: utf-8 -*-

from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.url import route_path

from ticketing.models import merge_session_with_post, record_to_multidict
from models import session, NewsLetter
from ticketing.views import BaseView
from ticketing.fanstatic import with_bootstrap

from forms import NewsLettersForm

import webhelpers.paginate as paginate

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
            news_letter = Event.get(news_letter_id)
            if news_letter is None:
                return HTTPNotFound('Event not found')
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
            return HTTPFound(location=route_path('news_letters.index', self.request))
        else:
            return {
                'form':f
            }

    @view_config(route_name='news_letters.show', renderer='ticketing:templates/news_letters/show.html')
    def show(self):
        news_letter_id = int(self.request.matchdict.get("news_letter_id", 0)) 
        news_letter = NewsLetter.get(news_letter_id)
        if news_letter is None:
            return HTTPNotFound("news_letter id %d is not found" % news_letter_id)

        current_page = int(self.request.params.get("page", 0)) 
        page_url = paginate.PageURL_WebOb(self.request)

        return {
            'news_letter' : news_letter,
        }   

