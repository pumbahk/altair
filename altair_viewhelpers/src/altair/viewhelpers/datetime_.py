# encoding: utf-8

from datetime import datetime

class DefaultDateTimeFormatter(object):
    WEEK =[u"月", u"火", u"水", u"木", u"金", u"土", u"日"]

    def _get_date_format(self, flavor):
        if flavor.get('without_year'):
            format = u"%-m月%-d日"
        else:
            format = u"%Y年%-m月%-d日"
        return format

    def _get_time_format(self, flavor):
        if flavor.get('without_second'):
            format = u'%-H:%M'
        else:
            format = u'%-H:%M:%-S'
        return format

    def format_datetime(self, dt, **flavor):
        format = self._get_date_format(flavor) + u' ' + self._get_time_format(flavor)
        base = dt.strftime(format.encode("utf-8")).decode("utf-8")
        if flavor.get('with_weekday'):
            base += u'(%s)' % self.WEEK[dt.weekday()]
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

    def term_datetime(self, beg, end):
        """ dateオブジェクトを受け取り期間を表す文字列を返す
        e.g. 2012年3月3日(土)〜7月12日(木) 
        """
        if beg is None:
            if end is None:
                return u""
            else:
                return u"〜 %s" % (self.formatter.format_datetime(end, with_weekday=True, without_second=True))
        else:
            if end is None:
                return u"%s 〜" % self.formatter.format_datetime(beg, with_weekday=True, without_second=True)
            else:
                end_flavor = dict(without_year=(beg.year == end.year))
                return u'%s 〜 %s' % (
                    self.formatter.format_datetime(beg, with_weekday=True, without_second=True),
                    self.formatter.format_datetime(beg, with_weekday=True, without_second=True, **end_flavor)
                    )

    def term(self, beg, end):
        """ dateオブジェクトを受け取り期間を表す文字列を返す
        e.g. 2012年3月3日(土)〜7月12日(木) 
        """
        if beg is None:
            if end is None:
                return u""
            else:
                return u"〜 %s" % (self.formatter.format_date(end, with_weekday=True))
        else:
            if end is None:
                return u"%s 〜" % self.formatter.format_date(beg, with_weekday=True)
            else:
                end_flavor = dict(without_year=(beg.year == end.year))
                return u'%s 〜 %s' % (
                    self.formatter.format_date(beg, with_weekday=True),
                    self.formatter.format_date(beg, with_weekday=True, **end_flavor)
                    )

    def date(self, d, **flavor):
        return self.formatter.format_date(d, **flavor) if d else u'-'

    def time(self, t, **flavor):
        return self.formatter.format_time(t, **flavor) if t else u'-'

    def datetime(self, dt, **flavor):
        return self.formatter.format_datetime(dt, **flavor) if dt else u'-'
