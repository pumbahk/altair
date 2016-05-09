# -*- coding:utf-8 -*-
import datetime
from altaircms.datelib import get_now
from altair.viewhelpers.string import RawText, nl_to_br, truncate
from altair.viewhelpers.datetime_ import DefaultDateTimeFormatter, DateTimeHelper

date_time_formatter = DefaultDateTimeFormatter()
date_time_helper = DateTimeHelper(date_time_formatter)

jdate = date_time_helper.date
jdatetime = date_time_helper.datetime

import urllib
def path_in_string(path, string):
    path = urllib.unquote_plus(path)
    return path.endswith(string)


def countdown_days_from(request, limit_date, today_fn=get_now):
    today = today_fn(request)
    today = datetime.date(today.year, today.month, today.day)
    limit_date = datetime.date(limit_date.year, limit_date.month, limit_date.day)

    if today > limit_date:
        return 0
    else:
        return (limit_date-today).days


def list_to_attibutes(attr_list):
    """
    >>> attr_list = [("id", "foo"), ("class", "bar")]
    >>> list_to_attibutes(attr_list)
    u'id="foo" class="bar"'
    """
    return u" ".join(u'%s="%s"' % (k, v) for k, v in attr_list)
    

def make_link(title, url):
    """
    >>> make_link("foo", "http://example.com")
    u'<a href="http://example.com">foo</a>'
    """
    return u'<a href="%s">%s</a>' % (url, title)

def text(string):
    return string if string  else u"-"

def truncated(string, n=142):
    return truncate(text(string), n)

def translate_longtext_to_simple_html(string):
    return u"<br/>".join(string.replace("\n\n", "<br/>").split("\n"))

def hidden_input(name, value, id=None):
    fmt = '<input id="%s" name="%s" type="hidden" value="%s" />'
    return fmt % (id or name,  name, value)
        
def confirm_stage():
    return hidden_input("stage", "confirm")
def execute_stage():
    return hidden_input("stage", "execute")

def deal_limit(today, deal_open, deal_close, in_preparation):
    today_date = datetime.datetime(today.year, today.month, today.day)
    deal_open_date = datetime.datetime(deal_open.year, deal_open.month, deal_open.day)

    if in_preparation:
        return u"準備中"

    N = (deal_open_date - today_date).days
    if N > 0:
        return u"販売開始まであと%d日" % N
    elif N == 0:
        return u"本日販売"

    N = (deal_close - today).days
    if N > 0:
        return u"販売終了まであと%d日" % N
    elif N == 0:
        S = (deal_close - today).seconds
        H = S / 3600 + 1
        if H > 1:
            return u"販売終了まであと%d時間" % H
        elif H == 1:
            M = S / 60 + 1
            return u"販売終了まであと%d分" % M
    else:
        return u"販売終了"

def get_genres(request, genre_id):
    from altaircms.models import Genre
    genre = request.allowable(Genre).filter(Genre.id==genre_id).first()

    gs = genre.ancestors_include_self
    gs.pop()

    genres = []
    for g in reversed(gs):
        genres.append(g)
    return genres

def deal_limit_class(limit):
    limit_class = "searchRemainingOnsale"
    if limit == u"本日販売":
        limit_class = "searchRemainingToday"
    if limit == u"販売終了":
        limit_class = "searchRemainingSalesTermination"
    if limit.find(u"販売開始") != -1 or limit == u"準備中":
        limit_class = "searchRemaining"
    return limit_class

if __name__ == "__main__":
    import doctest
    doctest.testmod()
