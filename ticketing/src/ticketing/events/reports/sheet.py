# -*- coding: utf-8 -*-
import json
from datetime import datetime
from ticketing.helpers.base import jdate, jdatetime


class SeatSource(object):
    def __init__(self, block=None, floor=None, line=None, seat=None):
        self.block = block
        self.floor = floor
        self.line = line
        self.seat = seat

    def get_block_display(self):
        return "%s %s" % (self.block, self.floor)


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
    def __init__(self, seat_type=None):
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
            "total1": str(self.get_total_stocks()),
            "total2": str(self.get_total_returns()),
            "records": [],
        }
        for record in self.records:
            data["records"].append(record.get_record())
        return data


def process_sheet(exporter, sheet, event, performance, stock_records, now=None):
    """シートの内容を埋める
    """
    today_stamp = jdate(now or datetime.now())
    exporter.set_id(sheet, performance.code or "")
    exporter.set_datetime(sheet, today_stamp)
    exporter.set_event_name(sheet, event.title or "")
    exporter.set_performance_name(sheet, performance.name or "")
    exporter.set_performance_datetime(sheet, jdatetime(performance.start_on))
    for stock_record in stock_records:
        exporter.add_records(sheet, stock_record.get_records())


def seat_source_from_seat(seat):
    """SeatからSeatSourceを作る
    seat.venue.attributesにはjsonデコード可能な値が入る
    {
      "display_name_format": "%(block)s %(floor)s %(row)s %(seat)s",
      "scale": ["block", "floor", "row", "seat"]
    }
    """
    # TODO:モデルから取得
    #venue_attributes = seat.venue.attributes
    venue_attributes = """{
"display_name_format": "%(block)s %(floor)s %(row)s %(seat)s",
"scale": ["block", "floor", "row", "seat"]
}"""
    if venue_attributes:
        venue_attributes_dict = json.loads(venue_attributes)
    else:
        venue_attributes_dict = {}
    scales_keys = venue_attributes_dict.get("scale")
    seat_source = SeatSource()
    if scales_keys:
        if "block" in scales_keys:
            seat_source.block = seat["block"]
        if "floor" in scales_keys:
            seat_source.floor = seat["floor"]
        if "row" in scales_keys:
            seat_source.line = seat["row"]
        if "seat" in scales_keys:
            seat_source.seat = seat["seat"]
    return seat_source


def seat_records_from_seat_sources(seat_sources):
    """SeatSourceのリストからSeatRecordを返す
    """
