# encoding: utf-8

from datetime import datetime, date, time

class DefaultDateTimeFormatter(object):
    WEEK =[u"月", u"火", u"水", u"木", u"金", u"土", u"日"]

    def _get_date_format(self, flavor):
        if flavor.get('without_year'):
            format = u"%-m月%-d日"
        else:
            format = u"%Y年%-m月%-d日"
        return format

    def _get_time_format(self, flavor):
        if flavor.get('without_minute'):
            format = u'%-H時'
        elif flavor.get('without_second'):
            format = u'%-H:%M'
        else:
            format = u'%-H:%M:%S'
        return format

    def format_datetime(self, dt, **flavor):
        base = dt.strftime(self._get_date_format(flavor).encode("utf-8")).decode("utf-8")
        if flavor.get('with_weekday'):
            base += u'(%s)' % self.WEEK[dt.weekday()]
        base += u' ' + dt.strftime(self._get_time_format(flavor).encode("utf-8")).decode("utf-8")
        return base

    def format_date(self, d, **flavor):
        format = self._get_date_format(flavor)
        base = d.strftime(format.encode("utf-8")).decode("utf-8")
        if flavor.get('with_weekday'):
            base += u'(%s)' % self.WEEK[d.weekday()]
        return base

    def format_time(self, t, **flavor):
        format = self._get_time_format(flavor)
        return t.strftime(format.encode("utf-8")).decode("utf-8")

class DateTimeHelper(object):
    def __init__(self, formatter):
        self.formatter = formatter
        self.default_formatters = {
            datetime: self.datetime,
            date: self.date,
            time: self.time
            }

    def term(self, beg, end, none_label=u'指定なし', formatter=None, **flavor):
        """ dateオブジェクトを受け取り期間を表す文字列を返す
        e.g. 2012年3月3日(土)〜7月12日(木) 
        """
        with_weekday = flavor.pop('with_weekday', True)
        if formatter is None:
            formatter = self.default_formatters.get(type(beg or end), self.datetime)
        if beg is None:
            if end is None:
                return none_label
            else:
                return u"〜 %s" % (formatter(end, with_weekday=with_weekday, **flavor))
        else:
            if end is None:
                return u"%s 〜" % formatter(beg, with_weekday=with_weekday, **flavor)
            else:
                end_flavor = dict(without_year=(beg.year == end.year), **flavor)
                return u'%s 〜 %s' % (
                    formatter(beg, with_weekday=with_weekday, **flavor),
                    formatter(end, with_weekday=with_weekday, **end_flavor)
                    )

    term_datetime = term

    def date(self, d, **flavor):
        return self.formatter.format_date(d, **flavor) if d else u'-'

    def time(self, t, **flavor):
        without_second = flavor.pop('without_second', True)
        return self.formatter.format_time(t, without_second=without_second, **flavor) if t else u'-'

    def datetime(self, dt, **flavor):
        without_second = flavor.pop('without_second', True)
        return self.formatter.format_datetime(dt, without_second=without_second, **flavor) if dt else u'-'

def create_date_time_formatter(request):
    return DefaultDateTimeFormatter()
