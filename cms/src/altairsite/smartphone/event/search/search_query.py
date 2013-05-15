# -*- coding:utf-8 -*-
from altairsite.smartphone.common.helper import SmartPhoneHelper

class SearchQuery(object):
    def __init__(self, word, genre, sale, sale_info):
        self.word = word
        self.genre = genre
        self.sale = sale
        self.sale_info = sale_info
    def create_query(self):
        helper=SmartPhoneHelper()
        query = []
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
        parameter = "?word=" + self.word + "&sale=" + str(self.sale)
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

class DetailSearchQuery(object):
    def __init__(self, word, cond, genre, prefectures, sales_segment, event_open_info, sale_info, perf_info):
        self.word = word
        self.cond = cond
        self.genre = genre
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
        if self.genre:
            query.append(u"ジャンル：" + self.genre.label)
        if self.sales_segment:
            query.append(helper.get_sales_segment_japanese(self.sales_segment))
        if self.event_open_info:
            if self.event_open_info.since_event_open and self.event_open_info.event_open:
                query.append(u"公演日：" + unicode(self.event_open_info.since_event_open) + u" 〜 " +  unicode(self.event_open_info.event_open))
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
        if self.genre:
            parameter += "&genre_id=" + str(self.genre.id)
        else:
            parameter += "&genre_id="
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
