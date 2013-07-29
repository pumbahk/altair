# -*- coding:utf-8 -*-

from datetime import timedelta
from altair.app.ticketing.core.models import (
    ReportFrequencyEnum,
    ReportPeriodEnum,
)

class ReportCondition(object):
    def __init__(self, setting, now):
        self.setting = setting
        self.now = now

    @property
    def from_date(self):
        
        if self.setting.frequency == ReportFrequencyEnum.Daily.v[0]:
            # 日単位では本日分のみ
            return self.to_date
        elif self.setting.frequency == ReportFrequencyEnum.Weekly.v[0]:
            # 週単位では本日から7日前からのもの
            return self.now - timedelta(days=7)
        else:
            return self.now # XXX?

    @property
    def to_date(self):
        if self.setting.period == ReportPeriodEnum.Normal.v[0]:
            return self.now - timedelta(days=1)
        return self.now

    @property
    def limited_from(self):
        from_date = self.from_date
        if self.setting.period == ReportPeriodEnum.Normal.v[0]:
            return from_date.strftime('%Y-%m-%d 00:00')
        return None

    @property
    def limited_to(self):
        to_date = self.to_date
        if self.setting.period == ReportPeriodEnum.Entire.v[0]:
            return to_date.strftime('%Y-%m-%d %H:%M')
        elif self.setting.period == ReportPeriodEnum.Normal.v[0]:
            return to_date.strftime('%Y-%m-%d 23:59')
        return None

    @property
    def need_total(self):
        return self.setting.period != ReportPeriodEnum.Entire.v[0]

        
