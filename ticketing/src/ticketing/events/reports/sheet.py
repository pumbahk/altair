# -*- coding: utf-8 -*-
import json
import re
from datetime import datetime
from itertools import groupby

from ticketing.models import DBSession
from ticketing.core.models import SeatStatusEnum, VenueArea
from ticketing.helpers.base import jdate, jtime

import logging

class SeatSource(object):
    """SeatRecordを作成する際に使うオブジェクト, Seatモデルには依存しない
    """
    def __init__(self, block=None, floor=None, line=None, seat=None, status=None, source=None):
        self.source = source
        self.block = block     # ex: プレミアム
        self.floor = floor     # ex: 1
        self.line = line       # ex: 2
        self.seat = seat       # ex: 10
        self.status = status

    def get_block_display(self):
        # 席番号から生成する
        if self.source and self.source.name:
            name = re.sub(u' [0-9]+番', '', self.source.name)
            name = re.sub(u' [0-9]+列', '', name)
            return name
        return ""

    def get_row_display(self):
        # 席番号から生成する
        if self.source and self.source.name:
            match = re.match(u'^.+ ([0-9]+)列 .+$', self.source.name)
            if match:
                return match.group(1)
        return ""


class SeatRecord(object):
    """帳票の一行分のレコード
    """
    def __init__(self, block=None, line=None, start=None, end=None,
            date=None, quantity=0, stock_type="stocks"):
        self.block = block
        self.line = line
        self.start = start
        self.end = end
        self.date = date
        self.quantity = quantity
        self.stock_type = stock_type

    def is_stocks(self):
        return self.stock_type == "stocks"

    def is_returns(self):
        return self.stock_type == "returns"

    def get_record(self):
        """Exporterが扱える形の一行分のレコードを返す
        """
        record = {
            "block": self.block or "",
            "line": self.line or "",
        }
        if self.is_stocks():
            record["stocks"] = [
                self.start or "",
                u"〜",
                self.end or "",
                str(self.quantity),
            ]
        else:
            record["returns"] = [
                self.start or "",
                u"〜",
                self.end or "",
                str(self.date),
                str(self.quantity),
            ]
        return record


class StockRecord(object):
    """席種ごとの帳票データ
    """
    def __init__(self, seat_type=None, stocks_label=None):
        self.stocks_label = stocks_label
        self.seat_type = seat_type
        self.records = []

    def get_seat_type_display(self):
        return u"■%s" % self.seat_type

    def get_total_stocks(self):
        """仕入席数の合計を返す
        """
        value = 0
        for record in self.records:
            if record.is_stocks():
                value += record.quantity
        return value

    def get_total_returns(self):
        """返券席数の合計を返す
        """
        value = 0
        for record in self.records:
            if record.is_returns():
                value += record.quantity
        return value

    def get_records(self):
        """Exporterに渡せる形式のレコードを返す
        """
        data = {
            "seattype": self.get_seat_type_display(),
            "stocks_label": self.stocks_label,
            "total1": str(self.get_total_stocks()),
            "total2": str(self.get_total_returns()),
            "records": [],
        }
        for record in self.records:
            data["records"].append(record.get_record())
        return data


def process_sheet(exporter, sheet, event, performance, stock_holder, stock_records, now=None):
    """シートの内容を埋める
    """
    today_stamp = jdate(now or datetime.now())
    exporter.set_id(sheet, performance.code or "")
    exporter.set_stock_holder_name(sheet, stock_holder.name or "")
    exporter.set_datetime(sheet, today_stamp)
    exporter.set_event_name(sheet, event.title or "")
    exporter.set_performance_name(sheet, performance.name or "")
    exporter.set_performance_datetime(sheet, jdate(performance.start_on))
    exporter.set_performance_open_at(sheet, jtime(performance.open_on))
    exporter.set_performance_start_at(sheet, jtime(performance.start_on))
    exporter.set_performance_venue(sheet, performance.venue.name or "")
    for stock_record in stock_records:
        exporter.add_records(sheet, stock_record.get_records())


def seat_source_from_seat(seat):
    """SeatからSeatSourceを作る
    """
    attributes = seat.attributes or {}
    seat_source = SeatSource(source=seat)
    
    # フロアは、SeatAttributeのを使う
    if 'floor' in attributes:
        seat_source.floor = attributes.get('floor')

    # ブロック名は、SeatAttributeには無い
#   if attributes:
#       if 'block' in attributes:
#           seat_source.block = attributes.get('block')

    # ブロック名は、VenueAreaを検索して使う
    area = DBSession.query(VenueArea).join(VenueArea.groups)\
        .filter_by(venue_id=seat.venue_id)\
        .filter_by(group_l0_id=seat.group_l0_id).one()
    seat_source.block = area.name
    
    # ブロック名は、席番号から切りだして使う（いまいち）
#   seat_source.block = seat_source.get_block_display()
    
    # 列番号は、SeatAttributeのを使う
    seat_source.line = ''
    if 'row' in attributes:
       seat_source.line = attributes.get('row')

    # 列番号は、席番号から切りだして使う（いまいち）
#   seat_source.line = seat_source.get_row_display()
    
    seat_source.seat = seat.seat_no
    seat_source.status = seat.status
    return seat_source


def is_series_seat(seatsource1, seatsource2):
    """seatsource1とseatsource2が別の列、もしくは通路などを
    挟んで連続していない場合にTrueを返す
    """
    
    # いずれかのseatがNULLの時は違う列扱い
    if seatsource1.seat == None or seatsource2.seat == None:
        return False

    # 列IDが同じで、席番号の差が1の場合、連続
    if (seatsource1.source.row_l0_id == seatsource2.source.row_l0_id) and abs(int(seatsource1.seat)-int(seatsource2.seat)) == 1:
        return True
    
    return False


def seat_records_from_seat_sources(seat_sources, unsold=False):
    """SeatSourceのリストからSeatRecordのリストを返す
    サマリー作成
    """
    result = []
    # block,floor,line,seatの優先順でソートする
    sorted_seat_sources = sorted(
        seat_sources,
        key=lambda v: (v.block, v.floor, v.line, int(v.seat) if (v.seat!=None and v.seat!='') else None))
    # block,floor,lineでグループ化してSeatRecordを作る
    for key, generator in groupby(sorted_seat_sources, lambda v: (v.block, v.floor, v.line)):
        values = list(generator)
        # 連続した座席はまとめる
        lst_values = []
        def flush():
            seat_record = SeatRecord(
                    block=lst_values[0].block,
                    line=lst_values[0].line,
                    start=lst_values[0].seat,
                    end=lst_values[-1].seat,
                    quantity=len(lst_values),
                )
            result.append(seat_record)
            del lst_values[:]

        for value in values:
        #   print "b:%s r:%s s:%s" % (value.block, value.line, value.seat)
            # 1つ前の座席と連続していなければ結果に追加してlst_valuesをリセット
            if lst_values and not is_series_seat(lst_values[-1], value):
                flush()
            # 残席のみ
            if not unsold or value.status == SeatStatusEnum.Vacant.v:
                lst_values.append(value)
        # 残り
        if lst_values:
            flush()
    return result


class SalesScheduleRecord(object):
    """販売日程管理票の1シート分
    """
    def __init__(self, event_title=None, output_datetime=None, venue_name=None):
        self.event_title = event_title
        self.output_datetime = output_datetime
        self.venue_name = venue_name
        self.sales = []
        self.performances = []
        self.prices = []

    def get_record(self):
        record = dict(
            event_title=self.event_title or "",
            output_datetime=self.output_datetime or "",
            venue_name=self.venue_name or "",
            sales=[
                sales_record.get_record() for sales_record in self.sales
            ],
            performance=[
                performance_record.get_record() for performance_record in self.performances
            ],
            prices=[
                price_record.get_record() for price_record in self.prices
            ]
        )
        return record


class SalesScheduleSalesRecord(object):
    """販売日程管理票のSalesSegment部分
    """
    def __init__(self, sales_seg=None, sales_start=None, sales_end=None):
        self.sales_seg = sales_seg
        self.sales_start = sales_start
        self.sales_end = sales_end

    def get_record(self):
        record = dict(
            sales_seg=self.sales_seg or "",
            sales_start=self.sales_start or "",
            sales_end=self.sales_end or "",
        )
        return record


class SalesSchedulePerformanceRecord(object):
    """販売日程管理票のパフォーマンス部分
    """
    def __init__(self, datetime_=None, open_=None, start=None,
            price_name=None, sales_end=None, submit_order=None,
            submit_pay=None, pay_datetime=None):
        self.datetime = datetime_
        self.open_ = open_
        self.start = start
        self.price_name = price_name
        self.sales_end = sales_end

    def get_record(self):
        record = dict(
            datetime=self.datetime_ or "",
            open=self.open_ or "",
            start=self.start or "",
            price_name=self.price_name or "",
            sales_end = self.sales_end or "",
        )
        return record


class SalesSchedulePriceRecord(object):
    """販売日程管理票のprices
    """
    def __init__(self, name=None):
        self.name = name
        self.records = []

    def get_record(self):
        record = dict(
            name=self.name or "",
            records=[
                price_record.get_record() for price_record in self.records
            ],
        )
        return record


class SalesSchedulePriceRecordRecord(object):
    """販売日程管理票のpricesのrecordsの中身
    sheet_record['prices'][0]['records'][0]
    """
    def __init__(self, seat_type=None, ticket_type=None, price=None):
        self.seat_type = seat_type
        self.ticket_type = ticket_type
        self.price = price

    def get_record(self):
        record = dict(
            seat_type=self.seat_type or "",
            ticket_type=self.ticket_type or "",
            price=self.price is None and "" or self.price,
        )
        return record
