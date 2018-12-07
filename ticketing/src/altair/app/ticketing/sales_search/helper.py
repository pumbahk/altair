# -*- coding:utf-8 -*-
from markupsafe import Markup
from altair.app.ticketing.core.models import DateCalculationBase

date_calculation_str_dict = {
    DateCalculationBase.OrderDate.v: u"予約日から", DateCalculationBase.OrderDateTime.v: u"予約日時から",
    DateCalculationBase.PerformanceStartDate.v: u"公演開始から", DateCalculationBase.PerformanceEndDate.v: u"公演終了から",
    DateCalculationBase.SalesStartDate.v: u"販売開始から", DateCalculationBase.SalesEndDate.v: u"販売終了から"
}


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
        会場名があればHTMLとして返却する

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
    def disp_issuing_start_at(vh, sales_segment):
        """
        発券開始時刻をHTMLとして返却する
        PDMPが複数登録されていても、発券開始時刻は同じになる運用となっている。
        なので、間違って登録されている場合は、オペレータにメッセージを出力する。
        １つ目のPDMPの発券開始時刻を返す
        PDMPが登録されていない場合は、発券開始時刻はなし

        Parameters
        ----------
        vh : ViewHelper
            ビューヘルパー
        sales_segment : SalesSegment
            販売区分

        Returns
        ----------
        html : Markup
            発券開始時刻のHTML
        """
        issuing_start_at_list = []
        for pdmp in sales_segment.sales_segment_group.payment_delivery_method_pairs:
            if pdmp.issuing_start_at:
                issuing_start_at_list.append(
                    u"""<td class="span1">{0}</td>""".format(vh.datetime(pdmp.issuing_start_at, with_weekday=True)))
            else:
                issuing_start_at_list.append(u"""<td class="span1">{0}{1}日後</td>""".format(
                    date_calculation_str_dict[pdmp.issuing_start_day_calculation_base], pdmp.payment_period_days))

        if not issuing_start_at_list:
            # 決済引取方法の設定がない
            return Markup(u"-")

        if len(list(set(issuing_start_at_list))) > 1:
            # 発券開始時刻が違う決済引取方法がある
            issuing_start_at = issuing_start_at_list[0].replace(u"</td>",
                                                                u"""<br/><span style="color:red;">※発券開始時刻が違う決済引取方法があります</span></td>""")
            return Markup(issuing_start_at)

        # すべて同じ発券開始時刻
        return Markup(issuing_start_at_list[0])
