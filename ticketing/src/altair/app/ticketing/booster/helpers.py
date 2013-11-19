# encoding: utf-8

from markupsafe import Markup
from altair.app.ticketing.cart.helpers import *
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
        comps = name.split('.')
        ns = request.errors
        for comp in comps:
            if ns is None:
                break
            if not isinstance(ns, dict):
                raise TypeError
            ns = ns.get(comp)
        if ns:
            for err in ns:
                errs[err] = err
    if not errs:
        return u''
    errs = ", ".join(errs.values())
    if request.is_mobile:
        return Markup('<font color="red">%s</font><br />' % errs)
    else:
        return Markup('<p class="error">%s</p>' % errs)

def is_include_t_shirts(cart):
    for carted_product in cart.items:
        product = carted_product.product
        for item in product.items:
            if item.stock.stock_type.name == u'Tシャツ':
                return True
    return False


def sex_value(value):
    if value == u'male':
        return 1
    elif value == u'female':
        return 2
    else:
        return 0

