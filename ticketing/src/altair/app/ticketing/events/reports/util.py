# encoding: utf-8
class DateTimeFormatter(object):
    WEEK =[u"月", u"火", u"水", u"木", u"金", u"土", u"日"]
    DATE_FORMAT = u"%Y年%-m月%-d日"
    TIME_FORMAT = u'%-H:%M'

    def format_datetime(self, dt):
        return dt.strftime(self.DATE_FORMAT.encode("utf-8")).decode("utf-8") +\
            u'(%s)' % self.WEEK[dt.weekday()] + \
            dt.strftime(self.TIME_FORMAT.encode("utf-8")).decode("utf-8")

    def format_datetime_for_sheet_name(self, dt):
        format = u"%Y.%m.%d-%H%M%S"
        return dt.strftime(format.encode("utf-8")).decode("utf-8")

    def format_date(self, d):
        format = self.DATE_FORMAT
        return d.strftime(format.encode("utf-8")).decode("utf-8") + u'(%s)' % self.WEEK[d.weekday()]

    def format_time(self, t):
        format =self.TIME_FORMAT
        return t.strftime(format.encode("utf-8")).decode("utf-8")
