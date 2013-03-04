# -*- coding: utf-8 -*-
from cmsmobile.solr import helper
from pyramid.httpexceptions import HTTPNotFound
from altaircms.models import Performance
from altaircms.event.models import Event
import logging

logger = logging.getLogger(__file__)

class EventSearcher(object):

    def get_events_from_freeword(self, request, form):

        search_word = ""
        if form.word.data != "" and form.word.data is not None:
            search_word = form.word.data

        if form.sub_genre.data != "" and form.sub_genre.data is not None:
            search_word = search_word + " " + form.sub_genre.data
        elif form.genre.data != "" and form.genre.data is not None:
            search_word = search_word + " " + form.genre.data

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


    def get_events_from_area(self, form, qs):
        if form.area.data:
            prefectures = _get_prefecture(form.area.data)
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

def _get_prefecture(area):
    areas = {
         u'北海道':['hokkaido']
        ,u'北関東':['ibaraki','tochigi','gunma','saitama']
        ,u'東海':['gifu','aichi','mie','shizuoka']
        ,u'甲信越':['niigata','yamanashi','nagano']
        ,u'北陸':['toyama','ishikawa','fukui']
        ,u'東北':['aomori', 'iwate', 'akita', 'miyagi', 'yamagata', 'fukushima']
        ,u'首都圏':['chiba','tokyo','kanagawa']
        ,u'近畿':['shiga','kyoto','osaka','hyogo','nara','wakayama']
        ,u'中国':['tottori','shimane','okayama','hiroshima','yamaguchi']
        ,u'四国':['tokushima','kagawa','ehime','kouchi']
        ,u'九州':['fukuoka','saga','nagasaki','kumamoto','oita','miyazaki','kagoshima']
        ,u'沖縄':['okinawa']
    }
    return areas[area]
