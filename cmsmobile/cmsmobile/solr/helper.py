# -*- coding: utf-8 -*-
from altaircms.solr import api as solrapi
from altaircms.event.models import Event
from altaircms.page.models import Page

def searchEvents(request, word, area=None):
    searcher = solrapi.get_fulltext_search(request)
    response = searcher.solr.select(word)
    events = getResultEvets(response)
    if area:
        prefectures = get_prefecture(area)
        events = getEventsFromArea(events, prefectures)
    return events

def getResultEvets(response):
    ids = [res['id'] for res in response]
    events = []
    for page_id in ids:
        page = Page.query.filter(Page.id == page_id).first()
        if page:
            event = Event.query.filter(Event.id == page.event_id).first()
            if event:
                if not event in events:
                    events.append(event)
    return events

def get_prefecture(area):

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

    prefectures = areas[area]
    return prefectures

def getEventsFromArea(events, prefectures):
    events_from_area = []
    for event in events:
        for perf in event.performances:
            for prefecture in prefectures:
                if perf.prefecture.find(prefecture) != -1:
                    events_from_area.append(event)
    return events_from_area