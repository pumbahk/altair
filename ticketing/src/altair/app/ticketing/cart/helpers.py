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
import json as _json

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

def create_date_label(start, end):
    only_start_format = u"{start.year}年{start.month}月{start.day}日"
    range_format = u"{start.year}年{start.month}月{start.day}日 - {end.year}年{end.month}月{end.day}日"
    same_year_format = u"{start.year}年{start.month}月{start.day}日 - {end.month}月{end.day}日"

    date_format = only_start_format

    if end:
        if start.year != end.year or start.month != end.month or start.day != end.day:
            date_format = range_format
            if start.year == end.year:
                date_format = same_year_format

    return date_format.format(start=start, end=end)

def create_time_label(start, end):
    only_start_format = u"{start.year}年{start.month}月{start.day}日 {start:%H:%M}"
    range_format = u"{start.year}年{start.month}月{start.day}日 - {end.year}年{end.month}月{end.day}日"
    same_year_format = u"{start.year}年{start.month}月{start.day}日 - {end.month}月{end.day}日"

    date_format = only_start_format

    if end:
        if start.year != end.year or start.month != end.month or start.day != end.day:
            date_format = range_format
            if start.year == end.year:
                date_format = same_year_format

    return date_format.format(start=start, end=end)

def create_time_only_label(start, end):
    time_format = u"{start:%H:%M}"

    if end:
        if start.year != end.year or start.month != end.month or start.day != end.day:
            return ""

    return time_format.format(start=start)

def performance_date(performance):
    return create_date_label(performance.start_on, performance.end_on)

def performance_datetime(performance):
    """Return date and time of the performance.
    """
    return create_time_label(performance.start_on, performance.end_on)

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
    plugin_id = cart.payment_delivery_pair.delivery_method.delivery_plugin_id
    logger.debug("plugin_id:%d" % plugin_id)

    cart = CartDelivery(cart)
    response = render_view_to_response(cart, request, name="delivery-%d" % plugin_id, secure=False)
    if response is None:
        raise ValueError
    return Markup(response.text)

def render_payment_confirm_viewlet(request, cart):
    plugin_id = cart.payment_delivery_pair.payment_method.payment_plugin_id
    logger.debug("plugin_id:%d" % plugin_id)

    cart = CartPayment(cart)
    response = render_view_to_response(cart, request, name="payment-%d" % plugin_id, secure=False)
    if response is None:
        raise ValueError('could not render payment_confirm_viewlet for payment plugin id=%d' % plugin_id)
    return Markup(response.text)

def render_delivery_finished_viewlet(request, order):
    plugin_id = order.payment_delivery_pair.delivery_method.delivery_plugin_id
    logger.debug("plugin_id:%d" % plugin_id)

    order = OrderDelivery(order)
    response = render_view_to_response(order, request, name="delivery-%d" % plugin_id, secure=False)
    if response is None:
        raise ValueError('could not render delivery_finished_viewlet for delivery plugin id=%d' % plugin_id)
    return Markup(response.text)

def render_payment_finished_viewlet(request, order):
    plugin_id = order.payment_delivery_pair.payment_method.payment_plugin_id
    logger.debug("plugin_id:%d" % plugin_id)

    order = OrderPayment(order)
    response = render_view_to_response(order, request, name="payment-%d" % plugin_id, secure=False)
    if response is None:
        raise ValueError('could not render payment_finished_viewlet for payment plugin id=%d' % plugin_id)
    return Markup(response.text)


def product_name_with_unit(product_items):
    if len(product_items) == 1:
        return None
    else:
        return u"(%s)" % (u" + ".join(
            u"%s:%d枚" % (escape(product_item.stock_type.name), product_item.quantity)
            for product_item in product_items))

def get_availability_text(quantity):
    if quantity <= 0:
        return u'×'
    elif quantity < 20:
        return u'△'
    else:
        return u'◎'

def cart_url(request, event=None, performance=None, sales_segment=None):
    if sales_segment is not None:
        extra = {}
        if sales_segment.performance_id is not None:
            extra['_query'] = {'performance': sales_segment.performance_id}
        return request.route_path('cart.index', event_id=sales_segment.event_id, **extra)
    elif performance is not None:
        return request.route_path('cart.index', event_id=performance.event_id, _query={'performance': performance.id})
    elif event is not None:
        return request.route_path('cart.index', event_id=event.id)
    else:
        raise ValueError()

def format_performance_name(request, performance):
    return u'%s (%s %d時公演)' % (performance.name, japanese_date(performance.start_on), performance.start_on.hour)

def format_name(request, event=None, performance=None, sales_segment=None):
    out = []
    if sales_segment is not None:
        if sales_segment.performance_id:
            out.append(format_performance_name(request, sales_segment.performance))
        else:
            out.append(sales_segment.event.title)
        out.extend([u' [', sales_segment.name, u']'])
    elif performance is not None:
        out.append(format_performance_name(request, performance))
    elif event is not None:
        out.append(event.title)
    else:
        raise ValueError()
    return u''.join(out)

def json_encode(value):
    return _json.dumps(value)

def get_nickname(request):
    return None
