# -*- coding:utf-8 -*-


import logging
import json
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPBadRequest
from altaircms.modellib import DBSession
from sqlalchemy import or_
from sqlalchemy.orm import joinedload
from ..event.models import Event
from ..models import Performance, Word, WordSearch, Performance_Word, Event_Word

from altair.viewhelpers.datetime_ import dt2str
logger = logging.getLogger(__file__)


@view_config(route_name="api_keyword", request_method="GET", renderer='json')
def api_word_get(request):
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

        w1 = request.allowable(Word)\
        .filter(Word.deleted_at==None)\
        .join(Performance_Word)\
        .join(Performance)\
        .filter(Performance.backend_id==cart_performance)

        w2 = request.allowable(Word)\
        .filter(Word.deleted_at==None)\
        .join(Event_Word)\
        .join(Event)\
        .filter(Event.id==performance.event_id)

        words = list()
        word_ids = set()
        for word in w1.all():
            words.append(dict(id=word.id, label=word.label, type=word.type))
            word_ids.add(word.id)
        for word in w2.all():
            if word.id not in word_ids:
                words.append(dict(id=word.id, label=word.label, type=word.type))
                word_ids.add(word.id)

        event = dict(id=performance.event.id, title=performance.event.title)
        return dict(performance=dict(title=performance.title, event=event), words=words)
    elif cart_event:
        event = request.allowable(Event)\
            .filter_by(backend_id=cart_event)\
            .first()
        if event is None:
            # no such event
            return dict()

        w1 = request.allowable(Word)\
        .filter(Word.deleted_at==None)\
        .join(Event_Word)\
        .join(Event)\
        .filter(Event.backend_id==cart_event)

        words = list()
        word_ids = set()
        for word in w1.all():
            words.append(dict(id=word.id, label=word.label, type=word.type))
            word_ids.add(word.id)

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
    words = request.allowable(Word)\
        .filter(Word.deleted_at==None)\
        .outerjoin(WordSearch)\
        .filter(WordSearch.deleted_at==None)

    id_list = request.params.get('id')
    if id_list is not None and 0 < len(id_list):
        words = words.filter(Word.id.in_(id_list.split(' ')))
    else:
        q = request.params.get('q')
        if q is not None and 0 < len(q):
            words = words.filter(or_(Word.label.contains(q), Word.label_kana.contains(q), WordSearch.data.contains(q)))
        else:
            raise HTTPBadRequest()

    words = words.distinct().all()
    word_dicts = list()
    for word in words:
        word_dicts.append(dict(id=word.id, label=word.label, label_kana=word.label_kana, description=word.description, type=word.type))
    return dict(words=word_dicts)