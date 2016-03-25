# -*- coding:utf-8 -*-

from pyramid.view import view_config

from sqlalchemy.orm import joinedload

from altaircms.modellib import DBSession as session
from altaircms.models import Performance
from altaircms.event.models import Event
from altaircms.models import Word, Performance_Word, Event_Word

"""
必要になるpublic API
- backend_performance_idからword一覧を得る
- word id一覧からword一覧を得る
"""

@view_config(route_name="api.word.get", request_method="GET", renderer='json')
def api_word_get(self, request):
    # subscribableなものだけを返す
    organization_id = 8    # FIXME:
    cart_performance = request.params.get('backend_performance_id')
    if cart_performance:
        performance = session.query(Performance)\
            .options(joinedload(Performance.event))\
            .filter_by(backend_id=cart_performance)\
            .one()

        w1 = session.query(Word)\
        .join(Performance_Word)\
        .filter(Word.organization_id==organization_id)\
        .filter(Performance_Word.subscribable==True)\
        .join(Performance)\
        .filter(Performance.backend_id==cart_performance)\
        .order_by(Performance_Word.sorting)

        w2 = session.query(Word)\
        .join(Event_Word)\
        .filter(Word.organization_id==organization_id)\
        .filter(Event_Word.subscribable==True)\
        .join(Event)\
        .filter(Event.id==performance.event_id)\
        .order_by(Event_Word.sorting)

        words = list()
        for word in w1.all():
            words.append(dict(id=word.id, data=word.data))
        for word in w2.all():
            # FIXME: 重複排除, でも並び順は維持したい
            words.append(dict(id=word.id, data=word.data))

        event = dict(title=performance.event.title)
        return dict(performance=dict(title=performance.title, event=event), words=words)

    words = session.query(Word).all()
    word_dicts = list()
    for word in words:
        word_dicts.append(dict(data=word.data))
    return dict(count=len(words), data=word_dicts)
