# -*- coding: utf-8 -*-
from cmsmobile.solr import helper
from pyramid.httpexceptions import HTTPNotFound
from altaircms.models import Performance
from altaircms.event.models import Event
from altaircms.models import Genre
from cmsmobile.core.const import get_prefecture
from cmsmobile.core.helper import exist_value
from cmsmobile.core.const import SalesEnum
from sqlalchemy import or_, and_, asc
from datetime import datetime, date, timedelta

import logging

logger = logging.getLogger(__file__)

class EventSearcher(object):

    # フリーワード、ジャンル検索
    def get_events_from_freeword(self, request, form):

        search_word = ""
        if exist_value(form.word.data):
            search_word = form.word.data

        if hasattr(form, "sub_genre"): # formが2種類入ってくるため
            if exist_value(form.sub_genre.data):
                genre = request.allowable(Genre).filter(Genre.id==form.genre.data).first()
                search_word = search_word + " " + genre.label
        elif exist_value(form.genre.data):
            subgenre = request.allowable(Genre).filter(Genre.id==form.genre.data).first()
            search_word = search_word + " " + subgenre.label

        qs = None
        if search_word != "":
            try:
                events = helper.searchEvents(request, search_word)
                ids = _create_ids(events)
                qs = self._create_common_qs()\
                        .filter(Event.id.in_(ids))
            except Exception, e:
                logger.exception(e)
                raise HTTPNotFound
        return qs

    # 地域検索
    def get_events_from_area(self, form, qs=None):

        if exist_value(form.area.data):
            prefectures = get_prefecture(form.area.data)
            # 絞り込み
            if qs:
                qs = qs.filter(Performance.prefecture.in_(prefectures))

            # 新規検索
            else:
                qs = self._create_common_qs()\
                        .filter(Performance.prefecture.in_(prefectures))
        return qs

    # 今週発売検索
    def get_events_week_sale(self, form, qs=None):

        if form.week_sale.data:
            qs = self._get_events_week_sale(form, qs)
        return qs

    # まもなく開演
    def get_events_soon_act(self, form, qs=None):

        if form.soon_act.data:
            # 絞り込み
            if qs:
                qs = qs.filter(datetime.now() < Performance.open_on) \
                    .filter(Performance.open_on < datetime.now() + timedelta(days=1))
            # 新規検索
            else:
                qs = self._create_common_qs()\
                        .filter(datetime.now() < Performance.open_on) \
                        .filter(Performance.open_on < datetime.now() + timedelta(days=1))
        return qs


    # 発売状況
    def get_events_from_sale(self, form, qs=None):
        if form.sale.data == str(SalesEnum.ON_SALE):
            qs = self._get_events_on_sale(form, qs)
        elif form.sale.data == str(SalesEnum.WEEK_SALE):
            qs = self._get_events_week_sale(date.today(), None, qs)
        elif form.sale.data == str(SalesEnum.NEAR_SALE_END):
            qs = self._get_events_near_sale_end(date.today(), 7, qs)
        return qs

    # 販売中
    def _get_events_on_sale(self, form, qs=None):
        # 絞り込み
        if qs:
            qs = qs.filter(datetime.now() >= Event.deal_open) \
                    .filter(datetime.now() <= Event.deal_close)
        # 新規検索
        else:
            qs = self._create_common_qs()\
                    .filter(datetime.now() >= Event.deal_open) \
                    .filter(datetime.now() <= Event.deal_close)
        return qs

    # 今週発売検索(月曜日を週のはじめとする)
    def _get_events_week_sale(self, today, offset=None, qs=None):
        start_day  = today + timedelta(days=offset or -today.weekday())
        where = (Event.deal_open >= start_day) & (Event.deal_open <= start_day+timedelta(days=7))
        if qs: # 絞り込み
            qs = qs.filter(where)
        else: # 新規作成
            qs = self._create_common_qs().filter(where)
        return qs

    # 販売終了間近
    def _get_events_near_sale_end(self, today, N=7, qs=None):
        limit_day = today + timedelta(days=N)
        where = (Event.deal_open <= today) & (today <= Event.deal_close) & (Event.deal_close <= limit_day)
        if qs:
            qs = qs.filter(where)
        else:
            qs = self._create_common_qs().filter(where)
        return qs

    # 共通クエリ部分
    def _create_common_qs(self):
        qs = Event.query \
            .join(Performance).filter(Event.id == Performance.event_id) \
            .filter(Event.is_searchable == True)
        return qs

def _create_ids(events):
    ids = []
    for event in events:
        ids.append(event.id)
    return ids
