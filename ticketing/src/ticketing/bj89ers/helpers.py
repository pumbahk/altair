# encoding: utf-8

from markupsafe import Markup
from ticketing.cart.helpers import *
from pyramid.threadlocal import get_current_request

def japanese_date(date):
    return u"%d年%d月%d日(%s)" % (date.year, date.month, date.day, u"月火水木金土日"[date.weekday()])

def japanese_time(time):
    return u"%d時%d分" % (time.hour, time.minute)

def error(names):
    request = get_current_request()
    if not hasattr(request, 'errors'):
        return ''
    if not isinstance(names, list):
        names = [names]
    errs = dict()
    for name in names:
        for err in request.errors.get(name,[]):
            errs[err] = err
    if not errs:
        return u''
    errs = ", ".join(errs.values())
    if request.is_mobile:
        return Markup('<font color="red">%s</font><br />' % errs)
    else:
        return Markup('<p class="error">%s</p>' % errs)
