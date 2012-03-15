# -*- coding:utf-8 -*-

WEEK =[u"月", u"火", u"水", u"木", u"金", u"土", u"日"]


def make_link(title, url):
    return u"<a href='%s'>%s</a>" % (url, title)

def nl_to_br(string):
    return string.replace("\n", "<br/>")

def jdate(d):
    """ dateオブジェクトを受け取り日本語の日付を返す
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
