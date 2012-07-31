# -*- coding:utf-8 -*-
import datetime


WEEK = [u"月", u"火", u"水", u"木", u"金", u"土", u"日"]
def jdate(d):
    """ dateオブジェクトを受け取り日本語の日付を返す
    >>> from datetime import date
    >>> jdate(date(2011, 1, 1))
    u'2011\u5e7401\u670801\u65e5'
    """
    if d:
        datestr = d.strftime(u"%Y年%-m月%-d日".encode("utf-8")).decode("utf-8")
        return u"%s（%s）" % (datestr, unicode(WEEK[d.weekday()]))
    else:
        return u"-"


def jdatetime(d):
    """datetimeオブジェクトを受け取り日本語の時刻を返す
    """
    if d:
        datestr = jdate(d)
        timestr = d.strftime(u"%H時%M分".encode("utf-8")).decode("utf-8")
        return u"%s%s" % (datestr, timestr)
    else:
        return u"-"
