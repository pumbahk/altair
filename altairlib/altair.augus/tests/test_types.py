#-*- coding: utf-8 -*-
from unittest import TestCase, skip
import time
import string
import datetime
from altair.augus.types import (
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

class NumberTypeTest(TestCase):
    def test_it(self):
        for ch in string.digits:
            self.assertEqual(int(ch), NumberType.get(ch))
        
class StringTypeTest(TestCase):
    def test_it(self):
        for ch in string.printable:
            self.assertEqual(ch, StringType.get(ch))

class _TimeTypeTest(object):
    FORMAT = '' # need override
    target = None # need override
    delta = datetime.timedelta(days=1)
    count = 0 # 1 year

    def test_it(self):
        today = datetime.date.today()
        for ii in range(self.count):
            today += self.delta
            txt = today.strftime(self.FORMAT)
            data = self.target.get(txt)
            self.assertEqual(txt, time.strftime(self.FORMAT, data))

class DateTypeTest(_TimeTypeTest, TestCase):
    FORMAT = '%Y%m%d'
    target = DateType
    delta = datetime.timedelta(days=1) # per day
    count = 365 # 1 year
    
class HourMinTypeTest(_TimeTypeTest, TestCase):
    FORMAT = '%H%M'
    target = HourMinType
    delta = datetime.timedelta(seconds=60) # per min
    count = 24 * 60 # 1 day

class DateTimeTypeTest(_TimeTypeTest, TestCase):
    FORMAT = '%Y%m%d%H%M%S'
    target = DateTimeType
    delta = datetime.timedelta(seconds=1) # per sec
    count = 30 * 60 # 30 min


class _EnumTest(object):
    target = None # need orverride
    NO_EXISTS = ['NO_EXIST',]
    
    def test_it(self):
        for data in self.target:
            self.assertEqual(data, self.target.get(data.value))

    def test_no_exist_data(self):
        for no_exist in self.NO_EXISTS:
            with self.assertRaises(ValueError):
                self.target.get(no_exist)
        
class PutbackTypeTest(_EnumTest, TestCase):
    target = PutbackType

class SeatTypeClassifTest(_EnumTest, TestCase):
    target = SeatTypeClassif

class StatusTest(_EnumTest, TestCase):
    target = Status

class PutbackStatusTest(_EnumTest, TestCase):
    target = PutbackStatus

class AchievementStatusTest(_EnumTest, TestCase):
    target = AchievementStatus

