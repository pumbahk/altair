# -*- coding:utf-8 -*-

from pyramid.view import view_config
import json
from altaircms.modellib import DBSession
from sqlalchemy.orm import joinedload
from ..event.models import Event
from ..models import Performance, Word, Performance_Word, Event_Word
from ..plugins.widget.summary.models import SummaryWidget


@view_config(route_name="api_keyword", request_method="GET", renderer='json')
def api_word_get(request):
    organization_id = 8    # FIXME:
    cart_performance = request.params.get('backend_performance_id')
    if cart_performance:
        performance = DBSession.query(Performance)\
            .options(joinedload(Performance.event))\
            .filter_by(backend_id=cart_performance)\
            .one()

        w1 = DBSession.query(Word)\
        .join(Performance_Word)\
        .filter(Word.organization_id==organization_id)\
        .filter(Performance_Word.subscribable==True)\
        .join(Performance)\
        .filter(Performance.backend_id==cart_performance)\
        .order_by(Performance_Word.sorting)

        w2 = DBSession.query(Word)\
        .join(Event_Word)\
        .filter(Word.organization_id==organization_id)\
        .filter(Event_Word.subscribable==True)\
        .join(Event)\
        .filter(Event.id==performance.event_id)\
        .order_by(Event_Word.sorting)

        words = list()
        word_ids = set()
        for word in w1.all():
            words.append(dict(id=word.id, label=word.label))
            word_ids.add(word.id)
        for word in w2.all():
            if word.id not in word_ids:
                words.append(dict(id=word.id, label=word.label))
                word_ids.add(word.id)

        event = dict(title=performance.event.title)
        return dict(performance=dict(title=performance.title, event=event), words=words)

    words = DBSession.query(Word).all()
    word_dicts = list()
    for word in words:
        word_dicts.append(dict(data=word.data))
    return dict(count=len(words), data=word_dicts)