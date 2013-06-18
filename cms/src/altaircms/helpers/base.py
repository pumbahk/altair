# -*- coding:utf-8 -*-
import datetime
from altaircms.datelib import get_now

class RawText(object):
    def __init__(self, v):
        self.value = v

    def __html__(self):
        return self.value

WEEK =[u"月", u"火", u"水", u"木", u"金", u"土", u"日"]
import urllib
def path_in_string(path, string):
    path = urllib.unquote_plus(path)
    return path.endswith(string)


def countdown_days_from(request, limit_date, today_fn=get_now):
    today = today_fn(request)
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

def nl_to_br(string, rawtext=True):
    return RawText(string.replace("\n", "<br/>"))

def text(string):
    return string if string  else u"-"

def truncated(string, n=142):
    v = text(string)
    return v if len(v) <= n else v + u".."

WEEK =[u"月", u"火", u"水", u"木", u"金", u"土", u"日"]
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
    if d:
        datestr = d.strftime(u"%Y年%-m月%-d日 %2H:%2M".encode("utf-8")).decode("utf-8")
        return u"%s（%s）" % (datestr, unicode(WEEK[d.weekday()]))
    else:
        return u"-"

def translate_longtext_to_simple_html(string):
    """
    abcdef
    xyz
    => <p>abcdef</p><p>xyz</p>


    abcdef

    xyz
    foo
    => <p>abcdef<br/></p><p>xyz</p><p>foo</p>
    """
    return u"<p>%s</p>" % u"</p><p>".join(string.replace("\n\n", "<br/>").split("\n"))

def hidden_input(name, value, id=None):
    fmt = '<input id="%s" name="%s" type="hidden" value="%s" />'
    return fmt % (id or name,  name, value)
        
def confirm_stage():
    return hidden_input("stage", "confirm")
def execute_stage():
    return hidden_input("stage", "execute")

def deal_limit(today, deal_open, deal_close):
    today_date = datetime.datetime(today.year, today.month, today.day)
    deal_open_date = datetime.datetime(deal_open.year, deal_open.month, deal_open.day)
    deal_close_date = datetime.datetime(deal_close.year, deal_close.month, deal_close.day)

    N = (deal_open_date - today_date).days
    if N > 0:
        return u"販売開始まであと%d日" % N
    elif N == 0:
        return u"本日販売"

    N = (deal_close_date - today_date).days
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

if __name__ == "__main__":
    import doctest
    doctest.testmod()
