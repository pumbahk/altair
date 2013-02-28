# -*- coding: utf-8 -*-
from cmsmobile.solr import helper
from pyramid.httpexceptions import HTTPNotFound
import logging

logger = logging.getLogger(__file__)

class EventSearcher(object):

    def get_events_from_freeword(self, request, form, events):

        search_word = form.word.data
        if form.sub_genre.data != "" and form.sub_genre.data is not None:
            search_word = form.word.data + " " + form.sub_genre.data
        elif form.genre.data != "" and form.genre.data is not None:
            search_word = form.word.data + " " + form.genre.data

        if search_word != "" and search_word is not None:
            try:
                events = helper.searchEvents(request, search_word)
            except Exception, e:
                logger.exception(e)
                raise HTTPNotFound
        return events


    def get_events_from_area(self, events, area):
        prefectures = _get_prefecture(area)

        events_from_area = []
        for event in events:
            for perf in event.performances:
                for prefecture in prefectures:
                    if perf.prefecture.find(prefecture) != -1:
                        events_from_area.append(event)
        return events_from_area

def _get_prefecture(area):
    areas = {
        '北海道':['hokkaido']
        ,'北関東':['ibaraki','tochigi','gunma','saitama']
        ,'東海':['gifu','aichi','mie','shizuoka']
        ,'甲信越':['niigata','yamanashi','nagano']
        ,'北陸':['toyama','ishikawa','fukui']
        ,'東北':['aomori', 'iwate', 'akita', 'miyagi', 'yamagata', 'fukushima']
        ,'首都圏':['chiba','tokyo','kanagawa']
        ,'近畿':['shiga','kyoto','osaka','hyogo','nara','wakayama']
        ,'中国':['tottori','shimane','okayama','hiroshima','yamaguchi']
        ,'四国':['tokushima','kagawa','ehime','kouchi']
        ,'九州':['fukuoka','saga','nagasaki','kumamoto','oita','miyazaki','kagoshima']
        ,'沖縄':['okinawa']
    }
    return areas[area.encode('utf-8')]
