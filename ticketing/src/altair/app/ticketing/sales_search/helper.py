# -*- coding:utf-8 -*-
from markupsafe import Markup


class SalesSearchHelper(object):

    @staticmethod
    def disp_performance_or_lot_name(request, sales_segment):
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
        return Markup(u"""<td class="span1">{0}</td>""".format(
            sales_segment.performance.venue.name if sales_segment.performance else "-"))

    @staticmethod
    def disp_performance_start_or_lotting_announce_datetime(vh, sales_segment):
        if sales_segment.performance:
            target_datetime = sales_segment.performance.start_on
        else:
            target_datetime = sales_segment.lots[0].lotting_announce_datetime
        return Markup(
            u"""<td class="span1">{0}</td>""".format(vh.datetime(target_datetime, with_weekday=True)))

    @staticmethod
    def disp_issuing_start_at(vh, sales_segment):
        for pdmp in sales_segment.sales_segment_group.payment_delivery_method_pairs:
            if pdmp.issuing_start_at:
                return Markup(u"""<td class="span1">{0}</td>""".format(vh.datetime(pdmp.issuing_start_at)))
            else:
                return Markup(u"""<td class="span1">{0}日</td>""".format(pdmp.payment_period_days))
        return u"-"
