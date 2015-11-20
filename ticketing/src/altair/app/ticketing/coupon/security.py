# -*- coding:utf-8 -*-
__author__ = 'ts-keiichi.okada'
from math import fabs
import datetime


def main():
    cs = CouponSecurity()
    for num in range(1, 50000):
        cs.today = datetime.date.today() - datetime.timedelta(days=num)
        print cs.security_number


class CouponSecurity(object):
    _COLOR_MAX = 7
    _COLOR_CODE = [u'red', u'blue', u'green', u'orange', u'pink', u'aqua', u'lime']
    _SECULITY_MAX = 1000

    def __init__(self, today=None):
        self._today = datetime.date.today()
        if today:
            self._today = today
        self._yesterday = self._today - datetime.timedelta(days=1)

    @property
    def today(self):
        return self._today

    @today.setter
    def today(self, today):
        self._today = today
        self._yesterday = self._today - datetime.timedelta(days=1)

    @today.getter
    def today(self):
        return self._today

    @property
    def color(self):
        yesterday_num = self.__calc_color_index(self._yesterday)
        today_num = self.__calc_color_index(self._today)
        if yesterday_num == today_num:
            today_num = (yesterday_num + 1) % self._COLOR_MAX
        return self._COLOR_CODE[today_num]

    def __calc_color_index(self, one_day):
        if one_day.day % 2 == 0:
            return int((one_day.year + one_day.month + one_day.day) % self._COLOR_MAX)
        return int((fabs(one_day.year + one_day.month - one_day.day)) % self._COLOR_MAX)

    @property
    def security_number(self):
        yesterday_num = self.__calc_security_number(self._yesterday)
        today_num = self.__calc_security_number(self._today)
        if yesterday_num == today_num:
            today_num = (yesterday_num + 1) % self._SECULITY_MAX
        return str(today_num).zfill(3)

    def __calc_security_number(self, one_day):
        seed = int(one_day.year + one_day.month + one_day.day)
        result = (pow(seed, 3) + one_day.day) % self._SECULITY_MAX
        if result == 0:
            result = seed % self._SECULITY_MAX
        return result


if __name__ == '__main__':
    main()
