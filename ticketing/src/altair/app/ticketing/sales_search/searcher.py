# -*- coding:utf-8 -*-
from .const import SalesKindEnum, SalesTermEnum
from sqlalchemy import between
from altair.app.ticketing.core.models import Event, EventSetting, Performance, SalesSegment, SalesSegmentGroup
from altair.app.ticketing.operators.models import Operator
from altair.app.ticketing.lots.models import Lot
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


class SalesSearcher(object):

    def __init__(self, session):
        self.session = session

    @staticmethod
    def __create_term(sales_term):
        today_datetime = datetime.now()
        if sales_term == u"today":
            term_start_str = '{0}/{1}/{2} 00:00'.format(today_datetime.year, today_datetime.month, today_datetime.day)
            term_end_str = '{0}/{1}/{2} 23:59'.format(today_datetime.year, today_datetime.month, today_datetime.day)
            term_start = datetime.strptime(term_start_str, '%Y/%m/%d %H:%M')
            term_end = datetime.strptime(term_end_str, '%Y/%m/%d %H:%M')
        elif sales_term == u"tomorrow":
            tomorrow = today_datetime + timedelta(days=1)
            term_start_str = '{0}/{1}/{2} 00:00'.format(tomorrow.year, tomorrow.month, tomorrow.day)
            term_end_str = '{0}/{1}/{2} 23:59'.format(tomorrow.year, tomorrow.month, tomorrow.day)
            term_start = datetime.strptime(term_start_str, '%Y/%m/%d %H:%M')
            term_end = datetime.strptime(term_end_str, '%Y/%m/%d %H:%M')
        elif sales_term == u"this_week":
            monday = today_datetime + timedelta(days=-today_datetime.weekday())
            sunday = monday + timedelta(days=6)
            term_start_str = '{0}/{1}/{2} 00:00'.format(monday.year, monday.month, monday.day)
            term_end_str = '{0}/{1}/{2} 23:59'.format(sunday.year, sunday.month, sunday.day)
            term_start = datetime.strptime(term_start_str, '%Y/%m/%d %H:%M')
            term_end = datetime.strptime(term_end_str, '%Y/%m/%d %H:%M')
        elif sales_term == u"this_week_plus_monday":
            monday = today_datetime + timedelta(days=-today_datetime.weekday())
            next_monday = monday + timedelta(days=7)
            term_start_str = '{0}/{1}/{2} 00:00'.format(monday.year, monday.month, monday.day)
            term_end_str = '{0}/{1}/{2} 23:59'.format(next_monday.year, next_monday.month, next_monday.day)
            term_start = datetime.strptime(term_start_str, '%Y/%m/%d %H:%M')
            term_end = datetime.strptime(term_end_str, '%Y/%m/%d %H:%M')
        elif sales_term == u"next_week":
            next_monday = today_datetime + timedelta(days=-today_datetime.weekday() + 7)
            next_sunday = next_monday + timedelta(days=6)
            term_start_str = '{0}/{1}/{2} 00:00'.format(next_monday.year, next_monday.month, next_monday.day)
            term_end_str = '{0}/{1}/{2} 23:59'.format(next_sunday.year, next_sunday.month, next_sunday.day)
            term_start = datetime.strptime(term_start_str, '%Y/%m/%d %H:%M')
            term_end = datetime.strptime(term_end_str, '%Y/%m/%d %H:%M')
        elif sales_term == u"next_week_plus_monday":
            next_monday = today_datetime + timedelta(days=-today_datetime.weekday() + 7)
            week_after_next_monday = next_monday + timedelta(days=7)
            term_start_str = '{0}/{1}/{2} 00:00'.format(next_monday.year, next_monday.month, next_monday.day)
            term_end_str = '{0}/{1}/{2} 23:59'.format(week_after_next_monday.year, week_after_next_monday.month,
                                                      week_after_next_monday.day)
            term_start = datetime.strptime(term_start_str, '%Y/%m/%d %H:%M')
            term_end = datetime.strptime(term_end_str, '%Y/%m/%d %H:%M')
        elif sales_term == u"this_month":
            first_day = today_datetime + timedelta(days=-today_datetime.day + 1)
            last_day = first_day + relativedelta(months=1) + timedelta(days=-1)
            term_start_str = '{0}/{1}/1 00:00'.format(today_datetime.year, today_datetime.month)
            term_end_str = '{0}/{1}/{2} 23:59'.format(last_day.year, last_day.month,
                                                      last_day.day)
            term_start = datetime.strptime(term_start_str, '%Y/%m/%d %H:%M')
            term_end = datetime.strptime(term_end_str, '%Y/%m/%d %H:%M')

        elif sales_term == u"term":
            term = datetime.now()

        return term_start, term_end

    @staticmethod
    def __create_kind(salessegment_group_kind):
        # 販売区分の種別
        kind = []
        if u"normal" in salessegment_group_kind:
            kind.extend([u'normal', u'added_sales', u'same_day', u'vip', u'sales_counter', u'other'])
        if u"early_firstcome" in salessegment_group_kind:
            kind.extend([u"early_firstcome"])
        if u"early_lottery" in salessegment_group_kind:
            kind.extend([u"early_lottery", u"added_lottery", u"first_lottery"])
        return kind

    def search(self, organization_id, sales_kind, sales_term, salessegment_group_kind, operators):
        # 販売区分の種別
        kind = self.__create_kind(salessegment_group_kind)

        # 販売期間
        term_start, term_end = self.__create_term(sales_term)

        if sales_kind == u"sales_start":
            # 一般発売
            ret = self.session.query(SalesSegment)\
                .join(SalesSegmentGroup, Event, EventSetting)\
                .filter(Event.organization_id == organization_id)\
                .filter(EventSetting.event_operator_id.in_(operators))\
                .filter(SalesSegmentGroup.kind.in_(kind))\
                .filter(SalesSegment.start_at >= term_start)\
                .filter(SalesSegment.start_at <= term_end)\
                .filter(SalesSegmentGroup.kind.in_(salessegment_group_kind))\
                .all()
        else:
            # 抽選
            ret = self.session.query(SalesSegment)\
                .join(SalesSegmentGroup, Event, EventSetting)\
                .join(Lot, Lot.event_id == Event.id)\
                .filter(Event.organization_id == organization_id)\
                .filter(EventSetting.event_operator_id.in_(operators))\
                .filter(SalesSegmentGroup.kind.in_(kind))\
                .filter(Lot.lotting_announce_datetime >= term_start)\
                .filter(Lot.lotting_announce_datetime <= term_end)\
                .filter(SalesSegmentGroup.kind.in_(salessegment_group_kind))\
                .filter(SalesSegment.performance_id == None)\
                .all()

        return ret
