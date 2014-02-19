#-*- coding: utf-8 -*-
import time
import datetime
from enum import Enum

class _ValueType(object):
    @classmethod
    def get(cls, value):
        return value # pragma: no cover

    @classmethod
    def validate(cls, value):
        cls.get(value)
        return value

class _ExtendEnum(Enum):
    @classmethod
    def get(cls, value):
        for entry in cls:
            if value == entry.value:
                return entry
        else:
            raise ValueError('Does not have value: {0}'.format(value))

    @classmethod
    def validate(cls, value):
        cls.get(value) # raise ValueError
        return value

class _TimeType(_ValueType):
    FORMAT = ''

    @classmethod
    def get(cls, value):
        try:
            return time.strptime(value, cls.FORMAT)
        except TypeError as err:
            pass

        try:
            time.strftime(cls.FORMAT, value)
            return value
        except TypeError as err:
            pass

        try:
            value.strftime(cls.FORMAT)
            return value
        except (AttributeError, TypeError) as err:
            raise TypeError('bad format: value={}, FORMAT="{}": {}'.format(repr(value), cls.FORMAT, repr(err)))

    @classmethod
    def now(cls):
        return time.strftime(cls.FORMAT)

class NumberType(_ValueType):
    @classmethod
    def get(cls, value):
        return int(value) # raise ValueError

class StringType(_ValueType):
    @classmethod
    def get(cls, value):
        try:
            return unicode(value)
        except (UnicodeEncodeError, UnicodeDecodeError) as err:
            raise err.__class__(repr(value), *err.args[1:])

class DateType(_TimeType):
    FORMAT = '%Y%m%d'

class HourMinType(_TimeType):
    FORMAT = '%H%M'

class DateTimeType(_TimeType):
    FORMAT = '%Y%m%d%H%M%S'


class PutbackType(_ExtendEnum):
    """返券区分
    """
    FINISH = 'F' # 最終返券
    ROUTE = 'R'  # 途中返券

class SeatTypeClassif(_ExtendEnum):
    """席種区分
    """
    SPEC = '1' # 指定席
    FREE = '2' # 自由席

class Status(_ExtendEnum):
    """状態フラグ
    """
    OK = '1' # OK
    NG = '2' # NG

class PutbackStatus(_ExtendEnum):
    """状態コード(返券)
    """
    CAN = '0'    # 返券可能
    CANNOT = '1' # 返券不可

class AchievementStatus(_ExtendEnum):
    RESERVE = '0' # 予約
    SOLD = '1'    # 販売済み
