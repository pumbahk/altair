# -*- coding:utf-8 -*-
import datetime

WEEK =[u"月", u"火", u"水", u"木", u"金", u"土", u"日"]
import urllib
def path_in_string(path, string):
    path = urllib.unquote_plus(path)
    return path.endswith(string)


def countdown_days_from(limit_date, today_fn=datetime.datetime.now):
    today = today_fn()
    if today > limit_date:
        return 0
    else:
        return (limit_date-today).days

COUNTDOWN_KIND_MAPPING = dict(event_open=u"公演開始", 
                              event_close=u"公演終了", 
                              deal_open=u"販売開始", 
                              deal_close=u"販売終了")

def countdown_kind_ja(kind):
    return COUNTDOWN_KIND_MAPPING[kind]

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

def nl_to_br(string):
    return string.replace("\n", "<br/>")

def jdate(d):
    """ dateオブジェクトを受け取り日本語の日付を返す
    >>> from datetime import date
    >>> jdate(date(2011, 1, 1))
    u'2011\u5e7401\u670801\u65e5'
    """
    return d.strftime(u"%Y年%m月%d日".encode("utf-8")).decode("utf-8")

def term(beg, end):
    """ dateオブジェクトを受け取り期間を表す文字列を返す
    e.g. 2012年3月3日(土)〜7月12日(木) 
    """
    beg_str = beg.strftime(u"%Y年%m月%d日".encode("utf-8")).decode("utf-8")
    if beg.year == end.year:
        end_str = end.strftime(u"%m月%d日".encode("utf-8")).decode("utf-8")
    else:
        end_str = end.strftime(u"%Y年%m月%d日".encode("utf-8")).decode("utf-8")
    return u"%s(%s) 〜 %s(%s)" % (beg_str, WEEK[beg.weekday()], end_str, WEEK[end.weekday()])

def hidden_input(name, value, id=None):
    fmt = '<input id="%s" name="%s" type="hidden" value="%s" />'
    return fmt % (id or name,  name, value)
        
def confirm_stage():
    return hidden_input("stage", "confirm")
def execute_stage():
    return hidden_input("stage", "execute")

if __name__ == "__main__":
    import doctest
    doctest.testmod()
