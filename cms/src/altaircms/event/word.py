# -*- coding:utf-8 -*-


import logging
import json
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPBadRequest
from altaircms.modellib import DBSession
from sqlalchemy import or_, and_
from sqlalchemy.orm import joinedload, aliased
from ..event.models import Event
from ..models import Performance, Word, WordSearch, Performance_Word, Event_Word

from altair.viewhelpers.datetime_ import dt2str
logger = logging.getLogger(__file__)


def make_words(tuples_list):
    words = dict()
    for tuples in tuples_list:
        for word in tuples:
            words[word.id] = dict([ (k, v) for (k, v) in word.__dict__.items() if k[0]!='_' ])
            words[word.id]["merge"] = []

    for tuples in tuples_list:
        for word in tuples:
            if word.merge_word_id:
                if word.merge_word_id not in words[word.id]["merge"]:
                    words[word.id]["merge"].append(word.merge_word_id)

    return words.values()


@view_config(route_name="api_keyword", request_method="GET", renderer='json')
def api_word_get(request):
    merge_word = aliased(Word)
    query = DBSession.query(Word.id, Word.label, Word.type, merge_word.id.label('merge_word_id'))

    cart_performance = request.params.get('backend_performance_id')
    cart_event = request.params.get('backend_event_id')
    if cart_performance:
        performance = request.allowable(Performance)\
            .options(joinedload(Performance.event))\
            .filter_by(backend_id=cart_performance)\
            .first()
        if performance is None:
            # no such performance
            return dict()

        w1 = request.allowable(Word, query)\
        .filter(Word.merge_to_word_id==None)\
        .join(Performance_Word)\
        .join(Performance)\
        .outerjoin(merge_word, and_(merge_word.merge_to_word_id==Word.id, merge_word.deleted_at==None))\
        .filter(Performance.backend_id==cart_performance)

        w2 = request.allowable(Word, query)\
        .filter(Word.merge_to_word_id==None)\
        .join(Event_Word)\
        .join(Event)\
        .outerjoin(merge_word, and_(merge_word.merge_to_word_id==Word.id, merge_word.deleted_at==None))\
        .filter(Event.id==performance.event_id)

        words = make_words([ w1.all(), w2.all() ])

        event = dict(id=performance.event.id, title=performance.event.title)
        return dict(performance=dict(title=performance.title, event=event), words=words)
    elif cart_event:
        event = request.allowable(Event)\
            .filter_by(backend_id=cart_event)\
            .first()
        if event is None:
            # no such event
            return dict()

        w1 = request.allowable(Word, query)\
        .filter(Word.merge_to_word_id==None)\
        .join(Event_Word)\
        .join(Event)\
        .outerjoin(merge_word, and_(merge_word.merge_to_word_id==Word.id, merge_word.deleted_at==None))\
        .filter(Event.backend_id==cart_event)

        words = make_words([ w1.all() ])

        include_pages = True
        if include_pages:
            pages = list()
            for ps in event.pagesets:
                p = ps.current()
                if p is not None:
                    pages.append(dict(path=ps.url,
                                      page_id=p.id,
                                      publish_begin=p.publish_begin.isoformat() if p.publish_begin is not None else None,
                                      publish_end=p.publish_end.isoformat() if p.publish_end is not None else None,
                                      ))
            return dict(event=dict(id=event.id, title=event.title), pages=pages, words=words)

        include_performances = False
        if include_performances:
            performances = list()
            for p in event.performances:
                performances.append(dict(id=p.id, title=p.title))

            return dict(event=dict(id=event.id, title=event.title), performances=performances, words=words)
        else:
            return dict(event=dict(id=event.id, title=event.title), words=words)

    # all words
    query = DBSession.query(Word.id, Word.label, Word.label_kana, Word.description, Word.type, merge_word.id.label('merge_word_id'))
    words = request.allowable(Word, query)\
        .filter(Word.deleted_at==None)\
        .outerjoin(WordSearch)\
        .filter(WordSearch.deleted_at==None)

    id_list = request.params.get('id')
    if id_list is not None and 0 < len(id_list):
        id_list = id_list.split(' ')
        words = words\
            .outerjoin(merge_word, and_(merge_word.merge_to_word_id==Word.id, merge_word.deleted_at==None))\
            .filter(Word.merge_to_word_id == None)\
            .filter(or_(Word.id.in_(id_list), (merge_word.id.in_(id_list))))
    else:
        q = request.params.get('q')
        if q is not None and 0 < len(q):
            words = words\
                .filter(Word.merge_to_word_id==None)\
                .filter(or_(Word.label.contains(q), Word.label_kana.contains(q), WordSearch.data.contains(q)))
        else:
            raise HTTPBadRequest()

    word_dicts = make_words([ words.distinct().all() ])
    return dict(words=word_dicts)