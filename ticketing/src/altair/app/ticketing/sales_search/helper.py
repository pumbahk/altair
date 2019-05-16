# -*- coding:utf-8 -*-
from markupsafe import Markup

from .util import SaleSearchUtil


class SalesSearchHelper(object):
    """
    販売日程管理検索のヘルパー
    """

    @staticmethod
    def disp_performance_or_lot_name(request, sales_segment):
        """
        公演か抽選の題名をHTMLとして返却する

        Parameters
        ----------
        request : Request
            リクエスト
        sales_segment : SalesSegment
            販売区分

        Returns
        ----------
        html : Markup
            公演名、または抽選名のHTML
        """
        if sales_segment.performance:
            return Markup(u"""<td class="span2"><a href="{0}">{1}</a></td>""".format(
                request.route_path('performances.show', performance_id=sales_segment.performance.id),
                sales_segment.performance.name))
        else:
            return Markup(u"""<td class="span2"><a href="{0}">{1}</a></td>""".format(
                request.route_path('lots.show', lot_id=sales_segment.lots[0].id),
                sales_segment.lots[0].name))

    @staticmethod
    def disp_venue_name(sales_segment):
        """
        会場名があればHTMLとして返却する

        Parameters
        ----------
        sales_segment : SalesSegment
            販売区分

        Returns
        ----------
        html : Markup
            会場名のHTML
        """
        return Markup(u"""<td class="span1">{0}</td>""".format(
            sales_segment.performance.venue.name if sales_segment.performance else "-"))

    @staticmethod
    def disp_performance_start_or_lotting_announce_datetime(vh, sales_segment):
        """
        一般販売なら公演時刻を、抽選なら当選時刻をHTMLとして返却する

        Parameters
        ----------
        vh : ViewHelper
            ビューヘルパー
        sales_segment : SalesSegment
            販売区分

        Returns
        ----------
        html : Markup
            公演開始時刻、または抽選当落発表時刻のHTML
        """
        if sales_segment.performance:
            target_datetime = sales_segment.performance.start_on
        else:
            target_datetime = sales_segment.lots[0].lotting_announce_datetime
        return Markup(
            u"""<td class="span1">{0}</td>""".format(vh.datetime(target_datetime, with_weekday=True)))

    @staticmethod
    def disp_issuing_start_at(sales_segment):
        """
        発券開始時刻をHTMLとして返却する
        PDMPが複数登録されていても、発券開始時刻は同じになる運用となっている。
        なので、間違って登録されている場合は、オペレータにメッセージを出力する。
        １つ目のPDMPの発券開始時刻を返す
        決済引取方法が登録されていない場合は、発券開始時刻はなし

        Parameters
        ----------
        sales_segment : SalesSegment
            販売区分

        Returns
        ----------
        html : Markup
            発券開始時刻のHTML
        """
        issuing_start_at_dict = SaleSearchUtil.get_issuing_start_at_dict(sales_segment)
        if 'issuing_start_day_calculation_base' not in issuing_start_at_dict:
            # 決済引取方法の設定がない
            return Markup(u"""<td class="span1">-</td>""")

        calculated_issuing_start_at = SaleSearchUtil.get_calculated_issuing_start_at(
            issuing_start_at=issuing_start_at_dict['issuing_start_at'],
            issuing_start_day_calculation_base=issuing_start_at_dict['issuing_start_day_calculation_base'],
            issuing_interval_days=issuing_start_at_dict['issuing_interval_days'],
            issuing_interval_time=issuing_start_at_dict['issuing_interval_time'],
            with_weekday=True
        )

        if issuing_start_at_dict['differented_issuing_start_at']:
            # 発券開始時刻が違う決済引取方法がある
            issuing_start_at = u"""<td class="span1">{0}<br/><span style="color:red;">
            ※発券開始時刻が違う決済引取方法があります</span></td>""".format(
                calculated_issuing_start_at)
        else:
            # すべて同じ発券開始時刻
            issuing_start_at = u"""<td class="span1">{0}</td>""".format(calculated_issuing_start_at)

        return Markup(issuing_start_at)
