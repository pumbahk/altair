# encoding: utf-8

from markupsafe import Markup
from pyramid.threadlocal import get_current_request
from altair.app.ticketing.cart.helpers import *
from altair.app.ticketing.core.models import OrderCancelReasonEnum
from ..cart.helpers import japanese_date, japanese_datetime

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

def order_status(order):
    if order.status == 'canceled':
        return u"キャンセル"
    elif order.status == 'delivered':
        return u"配送済み"
    elif order.payment_status == 'refunded' and order.cancel_reason == str(OrderCancelReasonEnum.CallOff.v[0]):
        return u"払戻済み(中止)"
    elif order.payment_status == 'refunded':
        return u"払戻済み"
    elif order.payment_status in ['paid', 'refunding']:
        return u"入金済み"
    elif order.payment_status == 'unpaid':
        return u"未入金"

def safe_strftime(s, format='%Y-%m-%d %H:%M'):
    return s and s.strftime(format) or ''

def get_order_status(order):
    if order.status == 'canceled':
        return u"キャンセル"
    elif order.status == 'delivered':
        return u"配送済"
    else:
        return u"受付済"

def get_order_status_image(order):
    if order.status == 'canceled':
        return u"icon_cancel.gif"
    elif order.status == 'delivered':
        return u"icon_hassou.gif"
    else:
        return u"icon_uketsuke.gif"

def get_payment_status(order):
    if order.payment_status == 'refunded' and order.cancel_reason == str(OrderCancelReasonEnum.CallOff.v[0]):
        return u"払戻済(中止)"
    elif order.payment_status == 'refunded':
        return u"払戻済"
    elif order.payment_status in ['paid', 'refunding']:
        return u"入金済"
    elif order.payment_status == 'unpaid':
        return u"未入金"

def get_payment_status_image(order):
    if order.payment_status == 'refunded' and order.cancel_reason == str(OrderCancelReasonEnum.CallOff.v[0]):
        return u"icon_haraimodoshizumi_b.gif"
    elif order.payment_status == 'refunded':
        return u"icon_haraimodoshizumi.gif"
    elif order.payment_status in ['paid', 'refunding']:
        return u"icon_payment.gif"
    elif order.payment_status == 'unpaid':
        return u"icon_minyukin.gif"
    return ""

def get_print_status(order):
    if order.printed_at:
        return u"発券済"
    else:
        return u"未発券"

def get_entry_status(entry):
    if entry.is_ordered:
        return u"当選"
    elif entry.is_rejected:
        return u"落選"
    else:
        return u"結果抽選待ち"

def get_entry_status_image(entry):
    if entry.is_ordered:
        return u"icon_tousen.gif"
    elif entry.is_rejected:
        return u"icon_rakusen.gif"
    else:
        return u"icon_kekkachusenmachi.gif"
