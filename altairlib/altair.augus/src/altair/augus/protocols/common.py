#-*- coding: utf-8 -*-
import re
import time
from enum import Enum
from ..errors import ProtocolFormatError
from ..types import (
    NumberType,
    StringType,
    DateType,
    HourMinType,
    DateTimeType,
    PutbackType,
    SeatTypeClassif,
    Status,
    PutbackStatus,
    AchievementStatus,
    )

_sjis2unicode = lambda msg: msg #msg.decode('sjis').encode('utf8')

class RecordAttribute(object):
    @property
    def achievement_status(self):
        return self._achievement_status

    @achievement_status.setter
    def achievement_status(self, value):
        self._achievement_status = AchievementStatus.validate(value)

    @property
    def area_code(self):
        """エリアコード
        """
        return self._area_code

    @area_code.setter
    def area_code(self, value):
        self._area_code = NumberType.validate(value)

    @property
    def area_name(self):
        """エリア名
        """
        return self._area_name

    @area_name.setter
    def area_name(self, value):
        self._area_name = StringType.validate(value)

    @property
    def block(self):
        """ブロックNo.
        自由席の場合は 0 になる。
        """
        return self._block

    @block.setter
    def block(self, value):
        self._block = NumberType.validate(value)

    @property
    def column(self):
        """列
        """
        return self._column

    @column.setter
    def column(self, value):
        self._column = StringType.validate(value)

    @property
    def coordx(self):
        """座標X
        自由席の場合は 0 になる
        """
        return self._coordx

    @coordx.setter
    def coordx(self, value):
        self._coordx = NumberType.validate(value)

    @property
    def coordx_whole(self):
        """全体座標X
        自由席の場合は 0 になる。
        """
        return self._coordx_whole

    @coordx_whole.setter
    def coordx_whole(self, value):
        self._coordx_whole = NumberType.validate(value)

    @property
    def coordy(self):
        """座標Y
        自由席の場合は 0 になる。
        """
        return self._coordy

    @coordy.setter
    def coordy(self, value):
        self._coordy = NumberType.validate(value)

    @property
    def coordy_whole(self):
        """全体座標Y
        自由席の場合は 0 になる。
        """
        return self._coordy_whole

    @coordy_whole.setter
    def coordy_whole(self, value):
        self._coordy_whole = NumberType.validate(value)

    @property
    def date(self):
        """公演日
        """
        return self._date

    DATE_FORMAT = '%Y%m%d' # 公演日
    @date.setter
    def date(self, value):
        self._date = DateType.validate(value)

    @property
    def distribution_code(self):
        """配券コード
        """
        return self._distribution_code

    @distribution_code.setter
    def distribution_code(self, value):
        self._distribution_code = NumberType.validate(value)

    @property
    def doorway_code(self):
        """出入り口コード
        """
        return self._doorway_code

    @doorway_code.setter
    def doorway_code(self, value):
        self._doorway_code = NumberType.validate(value)

    @property
    def doorway_name(self):
        """出入り口名
        """
        return self._doorway_name

    @doorway_name.setter
    def doorway_name(self, value):
        self._doorway_name = StringType.validate(value)

    @property
    def event_code(self):
        """事業コード
        """
        return self._event_code

    @event_code.setter
    def event_code(self, value):
        self._event_code = NumberType.validate(value)

    @property
    def event_name(self):
        """事業名
        """
        return self._event_name

    @event_name.setter
    def event_name(self, value):
        self._event_name = StringType.validate(value)

    @property
    def floor(self):
        """階
        """
        return self._floor

    @floor.setter
    def floor(self, value):
        self._floor = StringType.validate(value)

    @property
    def info_code(self):
        """付加情報コード
        """
        return self._info_code

    @info_code.setter
    def info_code(self, value):
        self._info_code = NumberType.validate(value)

    @property
    def info_name(self):
        """付加情報名
        """
        return self._info_name

    @info_name.setter
    def info_name(self, value):
        self._info_name = StringType.validate(value)

    @property
    def processed_at(self):
        """処理年月日時分秒
        """
        return self._processed_at

    @processed_at.setter
    def processed_at(self, value):
        self._processed_at = DateTimeType.validate(value)

    @property
    def number(self):
        """番
        """
        return self._number

    @number.setter
    def number(self, value):
        self._number = StringType.validate(value)

    @property
    def open_on(self):
        """開場時間
        """
        return self._open_on

    @open_on.setter
    def open_on(self, value):
        self._open_on = HourMinType.validate(value)

    @property
    def performance_code(self):
        """公演コード
        """
        return self._performance_code

    @performance_code.setter
    def performance_code(self, value):
        self._performance_code = NumberType.validate(value)

    @property
    def performance_name(self):
        """公演名
        """
        return self._performance_name

    @performance_name.setter
    def performance_name(self, value):
        self._performance_name = StringType.validate(value)

    @property
    def priority(self):
        """優先順位
        """
        return self._priority

    @priority.setter
    def priority(self, value):
        self._priority = NumberType.validate(value)

    @property
    def putback_status(self):
        return self._putback_status

    @putback_status.setter
    def putback_status(self, value):
        value = str(value)
        self._putback_status = PutbackStatus.validate(value)

    @property
    def putback_type(self):
        """返券区分

        ==== ===================
        値   意味
        ---- -------------------
        R    途中返券
        F    最終返券
        """
        return self._putback_type

    @putback_type.setter
    def putback_type(self, value):
        value = str(value)
        self._putback_type = PutbackType.validate(value)

    @property
    def putback_code(self):
        """返券コード
        """
        return self._putback_code

    @putback_code.setter
    def putback_code(self, value):
        self._putback_code = NumberType.validate(value)

    @property
    def reservation_number(self):
        """予約番号
        """
        return self._reservation_number

    @reservation_number.setter
    def reservation_number(self, value):
        self._reservation_number = StringType.validate(value)

    @property
    def seat_type_classif(self):
        """席種区分
        """
        return self._seat_type_classif

    @seat_type_classif.setter
    def seat_type_classif(self, value):
        self._seat_type_classif = SeatTypeClassif.validate(value)


    @property
    def seat_type_code(self):
        """席種コード
        """
        return self._seat_type_code

    @seat_type_code.setter
    def seat_type_code(self, value):
        self._seat_type_code = NumberType.validate(value)

    @property
    def seat_type_name(self):
        """席種名
        """
        return self._seat_type_name

    @seat_type_name.setter
    def seat_type_name(self, value):
        self._seat_type_name = StringType.validate(value)

    @property
    def start_on(self):
        return self._start_on

    @start_on.setter
    def start_on(self, value):
        self._start_on = HourMinType.validate(value)

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        self._status = Status.validate(value)

    @property
    def seat_count(self):
        """席数
        指定席の場合はからなず1になる。
        自由席の場合はその席数が入る。
        """
        return self._seat_count

    @seat_count.setter
    def seat_count(self, value):
        self._seat_count = NumberType.validate(value)

    @property
    def trader_code(self):
        """業者コード
        """
        return self._trader_code

    @trader_code.setter
    def trader_code(self, value):
        self._trader_code = NumberType.validate(value)

    @property
    def unit_value_code(self):
        """単価コード
        定価の場合は0
        """
        return self._unit_value_code

    @unit_value_code.setter
    def unit_value_code(self, value):
        self._unit_value_code = NumberType.validate(value)

    @property
    def unit_value_name(self):
        """単価名称
        定価の場合は空文字
        """
        return self._unit_value_name

    @unit_value_name.setter
    def unit_value_name(self, value):
        self._unit_value_name = StringType.validate(value)

    @property
    def unit_value(self):
        """単価
        定価か単価かどちらかと同じ
        """
        return self._unit_value

    @unit_value.setter
    def unit_value(self, value):
        self._unit_value = NumberType.validate(value)

    @property
    def value(self):
        """売価
        定価か単価かどちらかと同じ
        """
        return self._value

    @value.setter
    def value(self, value):
        self._value = NumberType.validate(value)

    @property
    def venue_code(self):
        """会場コード
        """
        return self._venue_code

    @venue_code.setter
    def venue_code(self, value):
        self._venue_code = NumberType.validate(value)

    @property
    def venue_name(self):
        """会場名
        """
        return self._venue_name

    @venue_name.setter
    def venue_name(self, value):
        self._venue_name = StringType.validate(value)

    @property
    def venue_version(self):
        """会場バージョン
        会場が更新されると必ずバージョンが上がる
        会場バージョンがかわると再度連携が必要
        """
        return self._venue_version

    @venue_version.setter
    def venue_version(self, value):
        self._venue_version = NumberType.validate(value)


class RecordIF(object):
    attributes = []

    def dump(self):
        return [getattr(self, name)for name in self.attributes]

    def load(self, row):
        try:
            for ii, name in enumerate(self.attributes):
                data = row[ii]
                setattr(self, name, data)
        except IndexError:
            raise ProtocolFormatError('Illegal format: length={0} (need={1})'\
                                      .format(len(row), len(self.attributes)))

class RecordBase(RecordIF, RecordAttribute):
    pass

class ProtocolBase(list):
    record = RecordBase
    pattern = ''
    fmt = ''

    def __init__(self, customer_id=None, event_code=None, venue_code=None):
        self.customer_id = customer_id
        self.event_code = event_code
        self.venue_code = venue_code
        self._date = None
        self._created_at = None
        self.set_now()

    @classmethod
    def match_name(cls, name):
        regx = re.compile(cls.pattern, re.I)
        return regx.match(name)

    @property
    def name(self):
        try:
            return self.fmt.format(customer_id=self.customer_id,
                                   event_code=self.event_code,
                                   venue_code=self.venue_code,
                                   date=self.date,
                                   created_at=self.created_at,
                                   start_on=self.date,
                                   )
        except ValueError as err:
            raise ValueError('illegal format: FORMAT={}, data: customer_id={}, event_code={}, venue_code={}, date={}, created_at={}, start_on={}'
                             .format(self.fmt, repr(self.customer_id), repr(self.event_code), repr(self.venue_code),
                                     repr(self.date), repr(self.created_at), repr(self.date))) # date == start_on


    DATE_FORMAT = '%Y%m%d%H%M'
    @property
    def date(self):
        return time.strftime(self.DATE_FORMAT, self._date)

    @date.setter
    def date(self, value):
        try:
            self._date = time.strptime(value, self.DATE_FORMAT)
            return
        except (TypeError, ValueError):
            pass

        try:
            time.strftime(self.DATE_FORMAT, value)
            self._date = value
            return
        except (TypeError, ValueError):
            pass

        raise ValueError('Illegal data: {}'.format(value))


    CREATED_AT_FORMAT = '%Y%m%d%H%M%S'
    @property
    def created_at(self):
        return time.strftime(self.CREATED_AT_FORMAT, self._created_at)

    @created_at.setter
    def created_at(self, value):
        try:
            self._created_at = time.strptime(value, self.CREATED_AT_FORMAT)
            return
        except (TypeError, ValueError):
            pass

        try:
            time.strftime(self.CREATED_AT_FORMAT, value)
            self._created_at = value
            return
        except (TypeError, ValueError):
            pass

        raise ValueError('Illegal data: {}'.format(value))

    @property
    def created_at_str(self):
        return self.created_at

    def iterdump(self):
        yield self.customer_id, self.created_at_str, str(len(self))
        for record in self:
            yield record.dump()

    def dump(self):
        return [row for row in self.iterdump()]

    def load(self, rows):
        rows = iter(rows)
        header = rows.next()
        self.customer_id = header[0]
        self.created_at = header[1]
        self.length = header[2]
        self.load_records(rows)

    def load_records(self, rows):
        for row in rows:
            record = self.create_record()
            record.load(row)
            self.append(record)

    @classmethod
    def create_record(cls):
        return cls.record()

    def set_now(self):
        self.date = time.localtime()
        self.created_at = self.date
