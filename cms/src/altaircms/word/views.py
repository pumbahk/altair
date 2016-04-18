# -*- coding:utf-8 -*-
#
from pyramid.view import view_config, view_defaults

from sqlalchemy import func, distinct
import sqlalchemy.orm as orm
import altaircms.helpers as h

from ..event.word import api_word_get
from .forms import WordForm
from ..lib.fanstatic_decorator import with_bootstrap

from ..models import DBSession
from ..models import Word, WordSearch
from ..event.models import Event_Word, Event

import logging
logger = logging.getLogger(__name__)

@view_defaults(
    # FIXME:
               permission="event_update",
               decorator=with_bootstrap
)
class WordManageView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(route_name='word',
        request_method="GET",
        renderer="altaircms:templates/word/list.html",)
    def index(self):
        q = DBSession.query(Word.id, Word.label, Word.label_kana,
                            func.count(distinct(WordSearch.id)).label("num_searches"),
                            func.count(distinct(Event.id)).label("num_events"),
                            Word.updated_at,
                            )
        words = self.request.allowable(Word, q)\
            .filter(Word.deleted_at==None)\
            .outerjoin(WordSearch)\
            .filter(WordSearch.deleted_at==None)\
            .outerjoin(Event_Word, Event)\
            .group_by(Word.id)\
            .order_by(Word.label_kana)\
            .all()
        return dict(words=words)

    @view_config(request_method="GET")
    def form(self):
        id = self.request.matchdict['id']
        logger.debug("id=%s" % id)
        word = self.request.allowable(Word)\
            .filter(Word.deleted_at==None)\
            .filter(Word.id==id)\
            .one()
        form = WordForm(word=word)
        return {"form": form, "word": word}
