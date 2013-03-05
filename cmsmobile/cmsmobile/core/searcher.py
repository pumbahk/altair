# -*- coding: utf-8 -*-
from cmsmobile.solr import helper
from pyramid.httpexceptions import HTTPNotFound
from altaircms.models import Performance
from altaircms.event.models import Event
from altaircms.models import Genre
from cmsmobile.core.const import get_prefecture

import logging

logger = logging.getLogger(__file__)

class EventSearcher(object):

    def get_events_from_freeword(self, request, form):

        search_word = ""
        if form.word.data != "" and form.word.data is not None:
            search_word = form.word.data

        if form.sub_genre.data != "" and form.sub_genre.data is not None:
            genre = request.allowable(Genre).filter(Genre.id==form.genre.data).first()
            search_word = search_word + " " + genre.label
        elif form.genre.data != "" and form.genre.data is not None:
            subgenre = request.allowable(Genre).filter(Genre.id==form.genre.data).first()
            search_word = search_word + " " + subgenre.label

        qs = None
        if search_word != "":
            try:
                events = helper.searchEvents(request, search_word)
                ids = _create_ids(events)
                qs = Event.query \
                    .join(Performance).filter(Event.id == Performance.event_id)\
                    .filter(Event.id.in_(ids))
            except Exception, e:
                logger.exception(e)
                raise HTTPNotFound
        return qs


    def get_events_from_area(self, form, qs=None):
        if form.area.data:
            prefectures = get_prefecture(form.area.data)
            # 絞り込み
            if qs:
                qs.filter(Performance.prefecture.in_(prefectures))

            # 新規検索
            else:
                qs = Event.query \
                        .join(Performance).filter(Event.id == Performance.event_id) \
                        .filter(Performance.prefecture.in_(prefectures))
        return qs

def _create_ids(events):
    ids = []
    for event in events:
        ids.append(event.id)
    return ids
