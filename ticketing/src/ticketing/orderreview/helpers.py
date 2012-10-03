# encoding: utf-8

from markupsafe import Markup
from ticketing.cart.helpers import *
from pyramid.threadlocal import get_current_request

__all__ = ["error", "order_desc", "is_include_t_shirts", "sex_value"]
           

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

def order_desc(order):
    profile = None
    t_shirts = None

    for item in order.items:
        for ordered_product_item in item.ordered_product_items:
            if ordered_product_item.product_item.stock.stock_type.name != u'Tシャツ':
                profile =  ordered_product_item.attributes
            else:
                t_shirts = ordered_product_item.attributes

    return profile, t_shirts

def is_include_t_shirts(cart):
    for carted_product in cart.products:
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

def order_status(order):
    if order.status == 'refunded':
        return u"キャンセル (返金済)"
    elif order.status == 'canceled':
        return u"キャンセル"
    elif order.status == 'delivered':
        return u"配送済み"
    elif order.status == 'paid':
        return u"入金済み"
    else:
        return u"未入金"

def safe_strftime(s, format='%Y-%m-%d %H:%M'):
    return s and s.strftime(format) or ''
