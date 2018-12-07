# -*- coding:utf-8 -*-
from .const import SalesKindEnum, SalesTermEnum
from altair.app.ticketing.core.models import SalesSegmentKindEnum
from sqlalchemy import between
from sqlalchemy import or_
from altair.app.ticketing.core.models import Event, EventSetting, Performance, SalesSegment, SalesSegmentGroup
from altair.app.ticketing.operators.models import Operator
from altair.app.ticketing.lots.models import Lot
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


class SalesSearcher(object):
    """
    販売日程管理検索の検索クラス

    Attributes
    ----------
    session : SessionMaker
        slaveセッション
    """

    def __init__(self, session):
        """
        Parameters
        ----------
        session : SessionMaker
            slaveセッション
        """
        self.session = session

    @staticmethod
    def __create_term(sales_term):
        """
        検索する対象の、期間を作成する

        Parameters
        ----------
        sales_term: unicode
            検索期間の区分

        Returns
        ----------
        (term_start, term_end) : tuple(term_start, term_end)
            検索する開始時刻と、検索の終了時刻のタプル
        """
        today_datetime = datetime.now()
        if sales_term == SalesTermEnum.TODAY.v:
            term_start_str = '{0}/{1}/{2} 00:00'.format(today_datetime.year, today_datetime.month, today_datetime.day)
            term_end_str = '{0}/{1}/{2} 23:59'.format(today_datetime.year, today_datetime.month, today_datetime.day)
            term_start = datetime.strptime(term_start_str, '%Y/%m/%d %H:%M')
            term_end = datetime.strptime(term_end_str, '%Y/%m/%d %H:%M')
        elif sales_term == SalesTermEnum.TOMORROW.v:
            tomorrow = today_datetime + timedelta(days=1)
            term_start_str = '{0}/{1}/{2} 00:00'.format(tomorrow.year, tomorrow.month, tomorrow.day)
            term_end_str = '{0}/{1}/{2} 23:59'.format(tomorrow.year, tomorrow.month, tomorrow.day)
            term_start = datetime.strptime(term_start_str, '%Y/%m/%d %H:%M')
            term_end = datetime.strptime(term_end_str, '%Y/%m/%d %H:%M')
        elif sales_term == SalesTermEnum.THIS_WEEK.v:
            monday = today_datetime + timedelta(days=-today_datetime.weekday())
            sunday = monday + timedelta(days=6)
            term_start_str = '{0}/{1}/{2} 00:00'.format(monday.year, monday.month, monday.day)
            term_end_str = '{0}/{1}/{2} 23:59'.format(sunday.year, sunday.month, sunday.day)
            term_start = datetime.strptime(term_start_str, '%Y/%m/%d %H:%M')
            term_end = datetime.strptime(term_end_str, '%Y/%m/%d %H:%M')
        elif sales_term == SalesTermEnum.THIS_WEEK_PLUS_MONDAY.v:
            monday = today_datetime + timedelta(days=-today_datetime.weekday())
            next_monday = monday + timedelta(days=7)
            term_start_str = '{0}/{1}/{2} 00:00'.format(monday.year, monday.month, monday.day)
            term_end_str = '{0}/{1}/{2} 23:59'.format(next_monday.year, next_monday.month, next_monday.day)
            term_start = datetime.strptime(term_start_str, '%Y/%m/%d %H:%M')
            term_end = datetime.strptime(term_end_str, '%Y/%m/%d %H:%M')
        elif sales_term == SalesTermEnum.NEXT_WEEK.v:
            next_monday = today_datetime + timedelta(days=-today_datetime.weekday() + 7)
            next_sunday = next_monday + timedelta(days=6)
            term_start_str = '{0}/{1}/{2} 00:00'.format(next_monday.year, next_monday.month, next_monday.day)
            term_end_str = '{0}/{1}/{2} 23:59'.format(next_sunday.year, next_sunday.month, next_sunday.day)
            term_start = datetime.strptime(term_start_str, '%Y/%m/%d %H:%M')
            term_end = datetime.strptime(term_end_str, '%Y/%m/%d %H:%M')
        elif sales_term == SalesTermEnum.NEXT_WEEK_PLUS_MONDAY.v:
            next_monday = today_datetime + timedelta(days=-today_datetime.weekday() + 7)
            week_after_next_monday = next_monday + timedelta(days=7)
            term_start_str = '{0}/{1}/{2} 00:00'.format(next_monday.year, next_monday.month, next_monday.day)
            term_end_str = '{0}/{1}/{2} 23:59'.format(week_after_next_monday.year, week_after_next_monday.month,
                                                      week_after_next_monday.day)
            term_start = datetime.strptime(term_start_str, '%Y/%m/%d %H:%M')
            term_end = datetime.strptime(term_end_str, '%Y/%m/%d %H:%M')
        elif sales_term == SalesTermEnum.THIS_MONTH.v:
            first_day = today_datetime + timedelta(days=-today_datetime.day + 1)
            last_day = first_day + relativedelta(months=1) + timedelta(days=-1)
            term_start_str = '{0}/{1}/1 00:00'.format(today_datetime.year, today_datetime.month)
            term_end_str = '{0}/{1}/{2} 23:59'.format(last_day.year, last_day.month,
                                                      last_day.day)
            term_start = datetime.strptime(term_start_str, '%Y/%m/%d %H:%M')
            term_end = datetime.strptime(term_end_str, '%Y/%m/%d %H:%M')

        elif sales_term == SalesTermEnum.TERM.v:
            term = datetime.now()

        return term_start, term_end

    @staticmethod
    def __create_kind(salessegment_group_kind):
        """
        検索する対象の、期間を作成する

        Parameters
        ----------
        salessegment_group_kind: unicode
            販売区分グループの区分

        Returns
        ----------
        [salessegment_group_kind] : list(salessegment_group_kind)
            検索する販売区分グループの区分のリスト
        """
        kind = []
        if SalesSegmentKindEnum.normal.k in salessegment_group_kind:
            kind.extend([SalesSegmentKindEnum.normal.k, SalesSegmentKindEnum.added_sales.k, SalesSegmentKindEnum.same_day.k, SalesSegmentKindEnum.vip.k, SalesSegmentKindEnum.sales_counter.k, SalesSegmentKindEnum.other.k])
        if SalesSegmentKindEnum.early_firstcome.k in salessegment_group_kind:
            kind.extend([SalesSegmentKindEnum.early_firstcome.k])
        if SalesSegmentKindEnum.early_lottery.k in salessegment_group_kind:
            kind.extend([SalesSegmentKindEnum.early_lottery.k, SalesSegmentKindEnum.added_lottery.k, SalesSegmentKindEnum.first_lottery.k])
        return kind

    def search(self, organization_id, sales_kind, sales_term, salessegment_group_kind, operators):
        """
        販売日程を検索する

        Parameters
        ----------
        organization_id: unicode
            ORGのID
        sales_kind: unicode
            一般発売か、抽選かの文字列
        sales_term: unicode
            検索期間の文字列
        salessegment_group_kind: unicode
            販売区分グループの区分の文字列
        operators: unicode
            オペレータのID（複数）

        Returns
        ----------
        [sales_segment] : list(sales_segment)
            検索結果のジェネレータ
        """

        if not salessegment_group_kind or not operators:
            return None

        # 販売区分の種別
        kind = self.__create_kind(salessegment_group_kind)

        # 販売期間
        term_start, term_end = self.__create_term(sales_term)

        if sales_kind == SalesKindEnum.SALES_START.v:
            # 一般発売
            ret = self.session.query(SalesSegment)\
                .join(SalesSegmentGroup, Event, EventSetting)\
                .filter(Event.organization_id == organization_id)\
                .filter(or_(EventSetting.event_operator_id.in_(operators), EventSetting.sales_person_id.in_(operators))) \
                .filter(SalesSegmentGroup.kind.in_(kind))\
                .filter(SalesSegment.start_at >= term_start)\
                .filter(SalesSegment.start_at <= term_end)\
                .filter(SalesSegmentGroup.kind.in_(salessegment_group_kind))
        else:
            # 抽選
            ret = self.session.query(SalesSegment)\
                .join(SalesSegmentGroup, Event, EventSetting)\
                .join(Lot, Lot.event_id == Event.id)\
                .filter(Event.organization_id == organization_id) \
                .filter(or_(EventSetting.event_operator_id.in_(operators), EventSetting.sales_person_id.in_(operators))) \
                .filter(SalesSegmentGroup.kind.in_(kind))\
                .filter(Lot.lotting_announce_datetime >= term_start)\
                .filter(Lot.lotting_announce_datetime <= term_end)\
                .filter(SalesSegmentGroup.kind.in_(salessegment_group_kind))\
                .filter(SalesSegment.performance_id == None)
        return ret
