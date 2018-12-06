# -*- coding:utf-8 -*-
from markupsafe import Markup


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
        for pdmp in sales_segment.sales_segment_group.payment_delivery_method_pairs:
            if pdmp.issuing_start_at:
                return Markup(u"""<td class="span1">{0}</td>""".format(vh.datetime(pdmp.issuing_start_at)))
            else:
                return Markup(u"""<td class="span1">{0}日</td>""".format(pdmp.payment_period_days))
        return u"-"
