# encoding: utf-8
from datetime import datetime
from markupsafe import Markup
from pyramid.threadlocal import get_current_request
from altair.now import get_now
from altair.mobile.api import is_mobile_request
from altair.app.ticketing.cart.helpers import *
from altair.app.ticketing.orders.models import OrderCancelReasonEnum
from altair.app.ticketing.cart.helpers import japanese_date, japanese_datetime
from altair.formhelpers.widgets.generic import GenericHiddenInput


__all__ = [
    "japanese_date",
    "japanese_datetime",
    "error",
    "order_desc",
    "is_include_t_shirts",
    "sex_value",
    "order_status",
    "safe_strftime",
    "get_order_status",
    "get_order_status_image",
    "get_payment_status",
    "get_payment_status_image",
    "get_print_status",
    "generic_hidden_input",
    "is_disabled_order",
    "get_entry_status",
    "get_entry_status_image",
    "safe_get_contact_url", # from altair.app.ticketing.cart.api
    ]

generic_hidden_input = GenericHiddenInput()

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

def order_status(order, sent=False):
    if order.status == 'canceled':
        return u"無効"
    elif order.status == 'delivered':
        return u"発送済" if sent else u"配送済み"
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

def get_order_status(order, sent=False):
    if order.status == 'canceled':
        return u"無効"
    elif order.status == 'delivered':
        return u"発送済" if sent else u"配送済み"
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

def is_disabled_order(entry):
    if entry.canceled_at:
        return True
    return False

def get_entry_status(request, entry):
    now = get_now(request)
    if entry.canceled_at and entry.lot.lotting_announce_datetime <= now:
        return u"無効"
    elif entry.is_ordered and entry.lot.lotting_announce_datetime <= now:
        return u"当選"
    elif entry.is_rejected and entry.lot.lotting_announce_datetime <= now:
        return u"落選"
    elif entry.withdrawn_at:
        return u"ユーザー取消"
    else:
        return u"結果抽選待ち"

def get_entry_status_image(request, entry):
    now = get_now(request)
    if entry.withdrawn_at:
        return u"icon_withdraw.gif"
    if entry.canceled_at:
        return u"icon_cancel.gif"
    elif entry.is_ordered and entry.lot.lotting_announce_datetime <= now:
        return u"icon_tousen.gif"
    elif entry.is_rejected and entry.lot.lotting_announce_datetime <= now:
        return u"icon_rakusen.gif"
    else:
        return u"icon_kekkachusenmachi.gif"
