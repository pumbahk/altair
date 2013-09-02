# -*- coding:utf-8 -*-

"""
TODO: cart取得はリソースの役目
"""
import functools
from pyramid.view import render_view_to_response
from pyramid.compat import escape
from markupsafe import Markup
from webhelpers.html.tags import *
from webhelpers.number import format_number as _format_number
from .resources import OrderDelivery, CartDelivery, OrderPayment, CartPayment
from ..core.models import FeeTypeEnum, SalesSegment, StockTypeEnum
from altair.app.ticketing.mails.helpers import render_delivery_finished_mail_viewlet, render_payment_finished_mail_viewlet
from altair.app.ticketing.mails.helpers import render_delivery_cancel_mail_viewlet, render_payment_cancel_mail_viewlet
from altair.app.ticketing.mails.helpers import render_delivery_lots_accepted_mail_viewlet, render_payment_lots_accepted_mail_viewlet
from altair.app.ticketing.mails.helpers import render_delivery_lots_elected_mail_viewlet, render_payment_lots_elected_mail_viewlet
from altair.app.ticketing.mails.helpers import render_delivery_lots_rejected_mail_viewlet, render_payment_lots_rejected_mail_viewlet
import logging
from .api import get_nickname

logger = logging.getLogger(__name__)

# これはcart以外でも使うのではないだろうか
def form_log(request, message):
    """ フォーム内容をログ書き出し
    """
    values = request.params.items()
    from pprint import pprint
    from StringIO import StringIO
    buff = StringIO()
    pprint(values, buff)
    values = buff.getvalue()

    logger.info("%s: \n%s" % (message, values))

def cart_timeout(request):
    return request.registry.settings['altair_cart.expire_time']

def performance_date(performance):
    date_format = u'{s.month}月{s.day}日 {s.hour:02}:{s.minute:02}'
    date_range_format = u'{s.month}月{s.day}日 {s.hour:02}:{s.minute:02} - {e.month}月{e.day}日'
    s = performance.start_on
    e = performance.end_on
    if e:
        if not (s.year == e.year and s.month == e.month and s.day == e.day):
            return date_range_format.format(s=s, e=e)
    return date_format.format(s=s) if s else u"-"

def performance_end_date(performance):
    s = performance.start_on
    return u'{s.month}月{s.day}日 {s.hour:02}:{s.minute:02}'.format(s=s) if s else u"-"

def japanese_date(date):
    return u"%d年%d月%02d日(%s)" % (date.year, date.month, date.day, u"月火水木金土日"[date.weekday()])

def japanese_time(time):
    return u"%d時%02d分" % (time.hour, time.minute)

def japanese_datetime(dt):
    try:
        return japanese_date(dt)+japanese_time(dt)
    except:
        logger.warn("dt is None")
        return ""

def mail_date(date):
    return u'{d.year}年 {d.month}月 {d.day}日 {d.hour:02}時 {d.minute:02}分'.format(d=date)


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

def build_unit_template(product_items):
    if len(product_items) == 1:
        if product_items[0].quantity == 1:
            return u"{{num}}枚"
        else:
            return u"%d×{{num}}枚" % product_items[0].quantity
    else:
        stock_type_dict = dict()
        for product_item in product_items:
            id = product_item.stock_type.id
            if id in stock_type_dict:
                stock_type = stock_type_dict[id]
                stock_type['quantity'] += product_item.quantity
            else:
                stock_type = dict(name=escape(product_item.stock_type.name), quantity=product_item.quantity)
            stock_type_dict[id] = stock_type
        return u"(%s)×{{num}}" % u" + ".join(
            u"%s:%d枚" % (stock_type.get('name'), stock_type.get('quantity'))
            for stock_type in stock_type_dict.values())

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


def product_name_with_unit(product_items):
    if len(product_items) == 1:
        return None
    else:
        return u"(%s)" % (u" + ".join(
            u"%s:%d枚" % (escape(product_item.stock_type.name), product_item.quantity)
            for product_item in product_items))

def get_availability_text(quantity):
    if quantity == 0:
        return u'×'
    elif quantity < 20: 
        return u'△'
    else:
        return u'◎'

