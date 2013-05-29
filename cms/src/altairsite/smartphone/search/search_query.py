# -*- coding:utf-8 -*-
from altairsite.smartphone.common.helper import SmartPhoneHelper
from altaircms.models import Genre

class SearchQuery(object):
    def __init__(self, word, genre, sale, sale_info):
        self.word = word
        self.genre = genre
        self.sale = sale
        self.sale_info = sale_info
    def create_query(self):
        helper=SmartPhoneHelper()
        query = []
        if self.word:
            query.append(u"フリーワード：" + self.word)
        if self.genre:
            query.append(u"ジャンル：" + self.genre.label)
        if self.sale:
            query.append(helper.get_sale_japanese(self.sale))
        if self.sale_info:
            if self.sale_info.sale_start:
                query.append(u"販売開始まで：" + str(self.sale.sale_start) + u"日")
            if self.sale_info.sale_end:
                query.append(u"販売終了まで：" + str(self.sale.sale_end) + u"日")
        return u"、".join(query)
    def create_parameter(self):
        parameter = "?sale=" + str(self.sale)
        if self.word:
            parameter += "&word=" + self.word
        if self.genre:
            parameter += "&genre_id=" + str(self.genre.id)
        if self.sale_info:
            if self.sale_info.sale_start:
                parameter += "&sale_start="
                parameter += str(self.sale_info.sale_start)
            if self.sale_info.sale_end:
                parameter += "&sale_end=" + str(self.sale_info.sale_end)
        return parameter

class AreaSearchQuery(object):
    def __init__(self, area, genre, genre_label):
        self.area = area
        self.genre = genre
        self.word = genre_label
    def create_query(self):
        helper=SmartPhoneHelper()
        query = []
        query.append(u"地域：" + helper.get_area_japanese(self.area))
        if self.word:
            query.append(u"ジャンル：" + self.word)
        return u"、".join(query)
    def create_parameter(self):
        parameter = "?area=" + self.area
        if self.genre:
            parameter += "&genre_id=" + str(self.genre.id)
        return parameter

class HotwordSearchQuery(object):
    def __init__(self, hotword):
        self.hotword = hotword
    def create_query(self):
        if self.hotword:
            return u"ホットワード：" + self.hotword.name
        return ""
    def create_parameter(self):
        parameter = ""
        if self.hotword:
            prameter = "?hotword_id=" + str(self.hotword.id)
        return parameter

class DetailSearchQuery(object):
    def __init__(self, word, cond, genre_music, genre_sports, genre_stage, genre_event, genres_label, prefectures, sales_segment, event_open_info, sale_info, perf_info):
        self.word = word
        self.cond = cond
        self.genre_music = genre_music
        self.genre_sports = genre_sports
        self.genre_stage = genre_stage
        self.genre_event = genre_event
        self.genres_label = genres_label
        self.prefectures = prefectures
        self.sales_segment = sales_segment
        self.event_open_info = event_open_info
        self.sale_info = sale_info
        self.perf_info = perf_info
    def create_query(self):
        helper=SmartPhoneHelper()
        query = []
        query.append(u"フリーワード：" + self.word)
        if self.cond == "union":
            query.append(u"少なくとも１つを含む")
        else:
            query.append(u"全てを含む")
        if self.genres_label:
            query.append(u"ジャンル：" + ", ".join(self.genres_label))
        if self.sales_segment:
            query.append(helper.get_sales_segment_japanese(self.sales_segment))
        if self.event_open_info:
            if self.event_open_info.since_event_open and self.event_open_info.event_open:
                query.append(u"公演日：" + self.event_open_info.since_event_open.strftime("%Y-%m-%d") + u" 〜 " + self.event_open_info.event_open.strftime("%Y-%m-%d"))
        if self.sale_info:
            if self.sale_info.sale_start:
                query.append(u"販売開始まで：" + str(self.sale_info.sale_start) + u"日")
            if self.sale_info.sale_end:
                query.append(u"販売終了まで：" + str(self.sale_info.sale_end) + u"日")
        if self.perf_info:
            if self.perf_info.canceled:
                query.append(u"中止した公演")
            if self.perf_info.closed:
                query.append(u"販売終了した公演")
        if self.prefectures:
            first = False
            for pref in self.prefectures:
                if first:
                    query.append(helper.get_prefecture_japanese(pref))
                else:
                    query.append(u"県名：" + helper.get_prefecture_japanese(pref))
                    first = True
        return u"、".join(query)
    def create_parameter(self):
        parameter = "?word=" + self.word
        if self.cond:
            parameter += "&cond=" + self.cond
        if self.genre_music:
            for genre_id in self.genre_music:
                parameter += "&genre_music=" + str(genre_id)
        if self.genre_sports:
            for genre_id in self.genre_sports:
                parameter += "&genre_sports=" + str(genre_id)
        if self.genre_stage:
            for genre_id in self.genre_stage:
                parameter += "&genre_stage=" + str(genre_id)
        if self.genre_event:
            for genre_id in self.genre_event:
                parameter += "&genre_event=" + str(genre_id)
        if self.prefectures:
            parameter += "&prefecture_hokkaido=" + "&prefecture_hokkaido=".join(self.prefectures)
        if self.sales_segment:
            parameter += "&sales_segment=" + self.sales_segment
        if self.event_open_info:
            if self.event_open_info.since_event_open:
                if self.event_open_info.event_open:
                    # smell
                    parameter += "&since_year=" + str(self.event_open_info.since_event_open.year)
                    parameter += "&since_month=" + str(self.event_open_info.since_event_open.month)
                    parameter += "&since_day=" + str(self.event_open_info.since_event_open.day)
                    parameter += "&year=" + str(self.event_open_info.event_open.year)
                    parameter += "&month=" + str(self.event_open_info.event_open.month)
                    parameter += "&day=" + str(self.event_open_info.event_open.day)
        if self.sale_info:
            parameter += "&sale_start="
            if self.sale_info.sale_start:
                parameter += str(self.sale_info.sale_start)
            parameter += "&sale_end="
            if self.sale_info.sale_end:
                parameter += str(self.sale_info.sale_end)
        if self.perf_info:
            if self.perf_info.canceled:
                parameter += "&canceled_perf=y"
            if self.perf_info.closed:
                parameter += "&closed_perf=y"
        return parameter

    def get_genre_ids(self):
        ids = []
        if self.genre_music:
            ids += self.genre_music
        if self.genre_sports:
            ids += self.genre_sports
        if self.genre_stage:
            ids += self.genre_stage
        if self.genre_event:
            ids += self.genre_event
        return ids

class EventOpenInfo(object):
    def __init__(self, since_event_open, event_open):
        self.since_event_open = since_event_open
        self.event_open = event_open

class SaleInfo(object):
    def __init__(self, sale_start, sale_end):
        self.sale_start = sale_start
        self.sale_end = sale_end

class PerformanceInfo(object):
    def __init__(self, canceled, closed):
        self.canceled = canceled
        self.closed = closed
