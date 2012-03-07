# -*- coding:utf-8 -*-

WEEK =[u"月", u"火", u"水", u"木", u"金", u"土", u"日"]
def _to_jastr(d):
    datestr = d.strftime(u"%Y年%m月%d日".encode("utf-8")).decode("utf-8")
    return u"%s（%s）" % (datestr, unicode(WEEK[d.weekday()]))


def _to_term(p):
    r = []
    if p.open_on:
        r.append(u"%s開場" % p.open_on.strftime("%H:%M"))
    if p.close_on:
        r.append(u"%s開演" % p.close_on.strftime("%H:%M"))
    if p.end_on:
        r.append(u"%s終了" % p.end_on.strftime("%H:%M"))
    return u"／".join(r)

def _to_where(p):
    return p.venue

def performance_description(performance):
    """ performanceから講演場所や日時を表示する文字列を返す
    e.g.
    2012年6月3日（日）　16:30開場／17:00開演　岸和田市立浪切ホール　大ホール
    """
    return u"　".join([_to_jastr(performance.open_on), _to_term(performance) , _to_where(performance)])
