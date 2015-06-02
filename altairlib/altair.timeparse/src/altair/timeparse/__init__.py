import parsedatetime
from dateutil.parser import parse as parsedate
from datetime import datetime, date, time, timedelta
from .duration import parse_duration, build_duration

__all__ = (
    'parse_time_spec',
    'parse_date_or_time',
    'parse_duration',
    'build_duration',
    'LazyDateTime',
    )

def parse_time_spec(spec):
    s = datetime(1900, 1, 1, 0, 0, 0)
    result, _ = parsedatetime.Calendar().parse(spec, s)
    return datetime(
        year=result.tm_year,
        month=result.tm_mon,
        day=result.tm_mday,
        hour=result.tm_hour,
        minute=result.tm_min,
        second=result.tm_sec
        ) - s

class LazyDateTime(object):
    def __init__(self, year=None, month=None, day=None, hour=None, minute=None, second=None, microsecond=None, tzinfo=None):
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.minute = minute
        self.second = second
        self.microsecond = microsecond
        self.tzinfo = tzinfo

    def replace(self, year=None, month=None, day=None, hour=None, minute=None, second=None, microsecond=None, tzinfo=None):
        if year is None:
            year = self.year
        if month is None:
            month = self.month
        if day is None:
            day = self.day
        if hour is None:
            hour = self.hour
        if minute is None:
            minute = self.minute
        if second is None:
            second = self.second
        if microsecond is None:
            microsecond = self.microsecond
        if tzinfo is None:
            tzinfo = self.tzinfo
        return LazyDateTime(
            year=year,
            month=month,
            day=day,
            hour=hour,
            minute=minute,
            second=second,
            microsecond=microsecond,
            tzinfo=tzinfo
            )

    def as_date_datetime_or_time(self, default=None, to_datetime=False, to_time=False):
        if default is None:
            default = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        hour = default.hour if self.hour is None else self.hour
        minute = default.minute if self.minute is None else self.minute
        second = default.second if self.second is None else self.second
        microsecond = default.microsecond if self.microsecond is None else self.microsecond
        tzinfo = default.tzinfo if self.tzinfo is None else self.tzinfo

        if not to_datetime and self.year is None and self.month is None and self.day is None:
            if to_time:
                return time(hour=hour, minute=minute, second=second, microsecond=microsecond, tzinfo=tzinfo)

        year = default.year if self.year is None else self.year
        month = default.month if self.month is None else self.month
        day = default.day if self.day is None else self.day

        if not to_datetime and self.hour is None and self.minute is None and self.second is None:
            return date(
                year=year,
                month=month,
                day=day
                )
        return datetime(
            year=year,
            month=month,
            day=day,
            hour=hour,
            minute=minute,
            second=second,
            microsecond=microsecond,
            tzinfo=tzinfo
            )

    def __repr__(self):
        return 'LazyDateTime(year={year}, month={month}, day={day}, hour={hour}, minute={minute}, second={second}, microsecond={microsecond}, tzinfo={tzinfo})'.format(**self.__dict__)


def parse_date_or_time(s, default=None, ignoretz=False, tzinfos=None, **kwargs):
    if default is not None:
        if not isinstance(default, LazyDateTime):
            default = LazyDateTime(
                year=default.year if hasattr(default, 'year') else None,
                month=default.month if hasattr(default, 'month') else None,
                day=default.day if hasattr(default, 'day') else None,
                hour=default.hour if hasattr(default, 'hour') else None,
                minute=default.minute if hasattr(default, 'minute') else None,
                second=default.second if hasattr(default, 'second') else None,
                microsecond=default.microsecond if hasattr(default, 'microsecond') else None,
                tzinfo=default.tzinfo if hasattr(default, 'tzinfo') else None
                )
    else:
        default = LazyDateTime()
    return parsedate(s, default=default, ignoretz=ignoretz, tzinfos=tzinfos, **kwargs)
