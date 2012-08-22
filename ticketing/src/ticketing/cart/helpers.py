# -*- coding:utf-8 -*-

"""
TODO: cart取得はリソースの役目
"""

from pyramid.view import render_view_to_response
from pyramid.compat import escape
from markupsafe import Markup
from webhelpers.html.tags import *
from webhelpers.number import format_number as _format_number
from markupsafe import Markup
from zope.interface import implementer
from .resources import OrderDelivery, CartDelivery, OrderPayment, CartPayment, CompleteMailDelivery, CompleteMailPayment
from ..core.models import FeeTypeEnum, SalesSegment, StockTypeEnum
import logging
from .api import get_nickname

logger = logging.getLogger(__name__)

def performance_date(performance):
    s = performance.start_on
    return u'{0.month}月{0.day}日 {0.hour:02}:{0.minute:02}'.format(s)

def japanese_date(date):
    return u"%d年%d月%d日(%s)" % (date.year, date.month, date.day, u"月火水木金土日"[date.weekday()])

def japanese_time(time):
    return u"%d時%d分" % (time.hour, time.minute)

def mail_date(date):
    return u'{d.year}年 {d.month}月 {d.day}日 {d.hour}時 {d.minute}分'.format(d=date)

# TODO: requestをパラメータから排除
def error_list(request, form, name):
    errors = form[name].errors
    if not errors:
        return ""
    
    html = '<ul class="error-list">'
    html += "".join(['<li>%s</li>' % e for e in errors])
    html += '</ul>'
    return Markup(html)

def fee_type(type_enum):
    if type_enum == int(FeeTypeEnum.Once.v[0]):
        return u"1件ごと"
    if type_enum == int(FeeTypeEnum.PerUnit.v[0]):
        return u"1枚ごと"

def format_number(num, thousands=","):
    return _format_number(int(num), thousands)

def format_currency(num, thousands=","):
    return u"￥" + format_number(num, thousands)

def build_unit_template(product, performance_id):
    items = product.items_by_performance_id(performance_id)
    if len(items) == 1:
        if items[0].quantity == 1:
            return u"{{num}}枚"
        else:
            return u"%d×{{num}}枚" % items[0].quantity
    else:
        return u"(%s)×{{num}}" % u" + ".join(
            u"%s:%d枚" % (escape(item.stock_type.name), item.quantity)
            for item in items)

def products_filter_by_salessegment(products, sales_segment):
    if sales_segment is None:
        logger.debug("debug: products_filter -- salessegment is none")
    if sales_segment:
        return products.filter_by(sales_segment=sales_segment)
    return products


# TODO: requestをパラメータから排除
def error_list(request, form, name):
    errors = form[name].errors
    if not errors:
        return ""
    
    html = '<ul class="error-list">'
    html += "".join(['<li>%s</li>' % e for e in errors])
    html += '</ul>'
    return Markup(html)

def fee_type(type_enum):
    if type_enum == int(FeeTypeEnum.Once.v[0]):
        return u"1申込当り"
    if type_enum == int(FeeTypeEnum.PerUnit.v[0]):
        return u"1枚ごと"

def format_number(num, thousands=","):
    return _format_number(int(num), thousands)

def format_currency(num, thousands=","):
    return u"￥" + format_number(num, thousands)

def build_unit_template(product, performance_id):
    items = product.items_by_performance_id(performance_id)
    if len(items) == 1:
        if items[0].quantity == 1:
            return u"{{num}}枚"
        else:
            return u"%d×{{num}}枚" % items[0].quantity
    else:
        return u"(%s)×{{num}}" % u" + ".join(
            u"%s:%d枚" % (escape(item.stock_type.name), item.quantity)
            for item in items)

def products_filter_by_salessegment(products, sales_segment):
    if sales_segment is None:
        logger.debug("debug: products_filter -- salessegment is none")
    if sales_segment:
        return products.filter_by(sales_segment=sales_segment)
    return products

def render_delivery_confirm_viewlet(request, cart):
    logger.debug("*" * 80)
    plugin_id = cart.payment_delivery_pair.delivery_method.delivery_plugin_id
    logger.debug("plugin_id:%d" % plugin_id)

    cart = CartDelivery(cart)
    response = render_view_to_response(cart, request, name="delivery-%d" % plugin_id, secure=False)
    if response is None:
        raise ValueError
    return Markup(response.text)

def render_payment_confirm_viewlet(request, cart):
    logger.debug("*" * 80)
    plugin_id = cart.payment_delivery_pair.payment_method.payment_plugin_id
    logger.debug("plugin_id:%d" % plugin_id)

    cart = CartPayment(cart)
    response = render_view_to_response(cart, request, name="payment-%d" % plugin_id, secure=False)
    if response is None:
        raise ValueError
    return Markup(response.text)

def render_delivery_finished_viewlet(request, order):
    logger.debug("*" * 80)
    plugin_id = order.payment_delivery_pair.delivery_method.delivery_plugin_id
    logger.debug("plugin_id:%d" % plugin_id)

    order = OrderDelivery(order)
    response = render_view_to_response(order, request, name="delivery-%d" % plugin_id, secure=False)
    if response is None:
        raise ValueError
    return Markup(response.text)

def render_payment_finished_viewlet(request, order):
    logger.debug("*" * 80)
    plugin_id = order.payment_delivery_pair.payment_method.payment_plugin_id
    logger.debug("plugin_id:%d" % plugin_id)

    order = OrderPayment(order)
    response = render_view_to_response(order, request, name="payment-%d" % plugin_id, secure=False)
    if response is None:
        raise ValueError
    return Markup(response.text)


def product_name_with_unit(product, performance_id):
    items = product.items_by_performance_id(performance_id)
    if len(items) == 1:
        return None
    else:
        return u"(%s)" % (u" + ".join(
            u"%s:%d枚" % (escape(item.stock_type.name), item.quantity)
            for item in items))

def render_delivery_finished_mail_viewlet(request, order):
    logger.debug("*" * 80)
    plugin_id = order.payment_delivery_pair.delivery_method.delivery_plugin_id
    logger.debug("plugin_id:%d" % plugin_id)

    order = CompleteMailDelivery(order)
    response = render_view_to_response(order, request, name="delivery-%d" % plugin_id, secure=False)
    if response is None:
        logger.debug("*complete mail*: %s is not found" % "delivery-%d" % plugin_id)
        return u""
    return Markup(response.text)

def render_payment_finished_mail_viewlet(request, order):
    logger.debug("*" * 80)
    plugin_id = order.payment_delivery_pair.payment_method.payment_plugin_id
    logger.debug("plugin_id:%d" % plugin_id)

    order = CompleteMailPayment(order)
    response = render_view_to_response(order, request, name="payment-%d" % plugin_id, secure=False)
    if response is None:
        logger.debug("*complete mail*: %s is not found" % "payment-%d" % plugin_id)
        return ""
    return Markup(response.text)

