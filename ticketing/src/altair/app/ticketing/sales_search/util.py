# -*- coding:utf-8 -*-

import logging

from altair.app.ticketing.core.models import DateCalculationBase
from altair.viewhelpers.datetime_ import DefaultDateTimeFormatter, DateTimeHelper

logger = logging.getLogger(__name__)


class SaleSearchUtil(object):
    """
    販売日程管理検索のユーティリティクラス

    """

    @staticmethod
    def get_issuing_start_at_dict(sales_segment):
        """
        販売区分に紐づく決済引取方法から発券開始日時の情報を取得する
        ----------
        sales_segment : SalesSegment
            販売区分

        Returns
        ----------
        issuing_start_at_dict : Dict
            issuing_start_at（発券開始日時）, issuing_start_day_calculation_base（発券開始の種別）,
            payment_period_days（発券開始日時の相対）, differented_issuing_start_at（発券開始が違う、決済引取方法があるか）
        """
        issuing_start_at_dict = {}
        one_issuing_start_at_dict = {}
        for pdmp in sales_segment.sales_segment_group.payment_delivery_method_pairs:
            if not issuing_start_at_dict:
                issuing_start_at_dict['issuing_start_at'] = pdmp.issuing_start_at
                issuing_start_at_dict['issuing_start_day_calculation_base'] = pdmp.issuing_start_day_calculation_base
                issuing_start_at_dict['issuing_interval_days'] = pdmp.issuing_interval_days
                issuing_start_at_dict['issuing_interval_time'] = pdmp.issuing_interval_time
                issuing_start_at_dict['differented_issuing_start_at'] = False
            else:
                one_issuing_start_at_dict['issuing_start_at'] = pdmp.issuing_start_at
                one_issuing_start_at_dict[
                    'issuing_start_day_calculation_base'] = pdmp.issuing_start_day_calculation_base
                one_issuing_start_at_dict['issuing_interval_days'] = pdmp.issuing_interval_days
                one_issuing_start_at_dict['issuing_interval_time'] = pdmp.issuing_interval_time
                one_issuing_start_at_dict['differented_issuing_start_at'] = False
                if issuing_start_at_dict != one_issuing_start_at_dict:
                    # 1つ目の決済引取方法の発券開始時刻の辞書と、他の決済引取方法の発券開始時刻の辞書を比較し
                    # 違うものが１つでもあればフラグを立てる
                    issuing_start_at_dict['differented_issuing_start_at'] = True
        return issuing_start_at_dict

    @staticmethod
    def get_calculated_issuing_start_at(issuing_start_at, issuing_start_day_calculation_base, issuing_interval_days,
                                        issuing_interval_time, with_weekday=False):
        """
        発券開始日時の情報から計算された日付の文字列を返す。または、相対日付の場合は、相対とわかる文字列を返す。
        ----------
        issuing_start_at : Datetime
            発券開始時刻
        issuing_start_day_calculation_base : int
            発券開始の相対種別（公演開始からなど）
        issuing_interval_days : int
            発券開始の相対日付
        issuing_interval_time : sqlalchemy.types.Time
            発券開始の相対時間
        with_weekday : bool
            Trueにすると曜日を表示する

        Returns
        ----------
        str : unicode
            発券開始日時、相対の発券開始日時
        """
        date_calculation_str_dict = {
            DateCalculationBase.OrderDate.v: u"予約日から", DateCalculationBase.OrderDateTime.v: u"予約日時から",
            DateCalculationBase.PerformanceStartDate.v: u"公演開始から", DateCalculationBase.PerformanceEndDate.v: u"公演終了から",
            DateCalculationBase.SalesStartDate.v: u"販売開始から", DateCalculationBase.SalesEndDate.v: u"販売終了から"
        }

        if issuing_start_at:
            if with_weekday:
                formatter = DefaultDateTimeFormatter()
                helper = DateTimeHelper(formatter)
                return helper.datetime(issuing_start_at, with_weekday=True)
            return issuing_start_at

        if issuing_start_day_calculation_base == DateCalculationBase.OrderDateTime.v:
            return u"""{0}{1}日後""".format(
                date_calculation_str_dict[issuing_start_day_calculation_base],
                issuing_interval_days
            )
        else:
            return u"""{0}{1}日後の{2}:{3:02d}""".format(
                date_calculation_str_dict[issuing_start_day_calculation_base],
                issuing_interval_days,
                issuing_interval_time.hour,
                issuing_interval_time.minute
            )
