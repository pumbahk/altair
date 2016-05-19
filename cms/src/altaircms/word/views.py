# -*- coding:utf-8 -*-
#
from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound

from sqlalchemy import func, distinct
import sqlalchemy.orm as orm
from sqlalchemy import or_
import altaircms.helpers as h
from datetime import datetime

from ..event.word import api_word_get
from .forms import WordForm
from ..lib.fanstatic_decorator import with_bootstrap
from altaircms.helpers.viewhelpers import get_endpoint
from altaircms.lib.crud.views import CRUDResource
from urlparse import urlparse, parse_qsl, urlunparse
from urllib import urlencode

from ..models import DBSession
from ..models import Word, WordSearch
from ..event.models import Event_Word, Event

from types import MethodType

import logging
logger = logging.getLogger(__name__)

def after_created(event):
    orig = urlparse(event.request.context.get_endpoint())
    query = dict(parse_qsl(orig.query))
    query['word'] = event.obj.id

    def with_id(self):
        return urlunparse((orig.scheme, orig.netloc, orig.path, orig.params, urlencode(query), orig.fragment))

    if 'cb' in query:
        # replace method
        event.request.context.get_endpoint = MethodType(with_id, event.request.context, CRUDResource)

@view_defaults(
    # FIXME:
               permission="event_update",
               decorator=with_bootstrap
)
class WordManageView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(route_name='word_list',
        request_method="GET",
        renderer="altaircms:templates/word/list.html",)
    def index(self):
        search = self.request.params.get('q')
        query = DBSession.query(Word.id, Word.label, Word.label_kana,
                            func.count(distinct(WordSearch.id)).label("num_searches"),
                            func.count(distinct(Event.id)).label("num_events"),
                            Word.created_at, Word.updated_at,
                            )
        qs = self.request.allowable(Word, query)\
            .filter(Word.deleted_at==None)\
            .outerjoin(WordSearch)\
            .filter(WordSearch.deleted_at==None)\
            .outerjoin(Event_Word, Event)\
            .group_by(Word.id)
        if search is not None and 0 < len(search):
            qs = qs.filter(or_(Word.label.contains(search), WordSearch.data.contains(search)))
        elif self.request.params.get('id'):
            qs = qs.filter(Word.id==int(self.request.params.get('id')))
        if self.request.params.get('o') == 'created':
            sorter = self.request.params.get('o')
            qs = qs.order_by(Word.created_at.desc())
        else:
            sorter = 'kana'
            qs = qs.order_by(Word.label_kana)

        return {
            "q": search if not None else '',
            "o": sorter,
            "xs": h.paginate(self.request, qs, item_count=qs.count(), items_per_page=50),
        }

    @view_config(route_name='word_create_back',
        request_method="GET",
        renderer="altaircms:templates/word/back.html",)
    def after_created_view(self):
        return {
            "cb": self.request.params.get('cb'),
            "word": self.request.params.get('word'),
        }

    @view_config(route_name='event_list_for_word',
        request_method="GET",
        renderer="altaircms:templates/word/event_list.html",)
    def event_index(self):
        deal = self.request.params.get('deal')

        query = DBSession.query(Event.id, Event.title,
                                Event.keywords,
                            )
        qs = self.request.allowable(Event)\
            .outerjoin(Event_Word)\
            .outerjoin(Word)\
            .filter(Word.deleted_at==None)\
            .group_by(Event.id)\
            .order_by(Event.deal_open)
        if deal == 'closed':
            qs = qs.filter(Event.deal_close < datetime.now())
        elif deal == 'open':
            qs = qs.filter(Event.deal_open <= datetime.now() <= Event.deal_close)
        else: # future
            deal = 'future'
            qs = qs.filter(datetime.now() < Event.deal_open)

        return {
            "xs": h.paginate(self.request, qs, item_count=qs.count()),
            "deal": deal,
            "now": datetime.now(),
        }
