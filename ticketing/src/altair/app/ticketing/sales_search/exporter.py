# -*- coding:utf-8 -*-

import logging
from collections import OrderedDict

from .util import SaleSearchUtil

logger = logging.getLogger(__name__)


class CSVExporter(object):
    """
    販売日程管理検索のCSVファイル出力用クラス

    Attributes
    ----------
    sales_segments : [SalesSegment]
        sales_segmentのリスト
    """

    def __init__(self, sales_segments):
        """
        Parameters
        ----------
        sales_segments : [SalesSegment]
            sales_segmentのリスト
        """
        self.sales_segments = sales_segments

    def __iter__(self):
        """
        検索する対象の、期間を作成する
        ----------

        Returns
        ----------
        orderedDict : OrderedDict
            CSVの一行（販売区分から、必要な行のデータを作成する）
        """
        for sales_segment in self.sales_segments:
            ordered_dict = OrderedDict()
            ordered_dict[u"イベント名"] = sales_segment.event.title
            if sales_segment.performance:
                ordered_dict[u"公演名（抽選名）"] = sales_segment.performance.name
            else:
                ordered_dict[u"公演名（抽選名）"] = sales_segment.lots[0].name
            ordered_dict[u"販売区分名"] = sales_segment.sales_segment_group.name
            ordered_dict[u"会場名"] = sales_segment.performance.venue.name if sales_segment.performance else "-"
            if sales_segment.performance:
                ordered_dict[u"公演日（抽選当選日）"] = sales_segment.performance.start_on
            else:
                ordered_dict[u"公演日（抽選当選日）"] = sales_segment.lots[0].lotting_announce_datetime
            ordered_dict[u"販売開始"] = sales_segment.start_at
            ordered_dict[u"販売終了"] = sales_segment.end_at
            issuing_start_at_dict = SaleSearchUtil.get_issuing_start_at_dict(sales_segment)
            if issuing_start_at_dict:
                ordered_dict[u"発券開始日時"] = SaleSearchUtil.get_calculated_issuing_start_at(
                    issuing_start_at_dict['issuing_start_at'],
                    issuing_start_at_dict['issuing_start_day_calculation_base'],
                    issuing_start_at_dict['issuing_interval_days'],
                    issuing_start_at_dict['issuing_interval_time']
                )
            else:
                ordered_dict[u"発券開始日時"] = u""
            ordered_dict[u"営業担当"] = sales_segment.event.setting.sales_person
            ordered_dict[u"登録担当"] = sales_segment.event.setting.event_operator
            yield ordered_dict
