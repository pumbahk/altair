# -*- coding:utf-8 -*-

"""
TODO: cart取得はリソースの役目
"""
import functools
from decimal import Decimal
import logging
import json as _json
from markupsafe import Markup
from webhelpers.html.tags import *
from webhelpers.number import format_number as _format_number
from wtforms.fields import Field
from wtforms.widgets import ListWidget
from pyramid.view import render_view_to_response
from pyramid.compat import escape
from pyramid.threadlocal import get_current_request
from altair.mobile.interfaces import IMobileRequest, ISmartphoneRequest
from altair.formhelpers.widgets.checkbox import CheckboxMultipleSelect
from altair.formhelpers.widgets.list import OurListWidget
from altair.formhelpers.widgets.datetime import OurDateWidget, build_date_input_japanese_japan
from altair.app.ticketing.mails.helpers import render_delivery_finished_mail_viewlet, render_payment_finished_mail_viewlet
from altair.app.ticketing.mails.helpers import render_delivery_cancel_mail_viewlet, render_payment_cancel_mail_viewlet
from altair.app.ticketing.mails.helpers import render_delivery_lots_accepted_mail_viewlet, render_payment_lots_accepted_mail_viewlet
from altair.app.ticketing.mails.helpers import render_delivery_lots_elected_mail_viewlet, render_payment_lots_elected_mail_viewlet
from altair.app.ticketing.mails.helpers import render_delivery_lots_rejected_mail_viewlet, render_payment_lots_rejected_mail_viewlet
from altair.app.ticketing.core.models import FeeTypeEnum, SalesSegment, StockTypeEnum
from .resources import OrderDelivery, CartDelivery, OrderPayment, CartPayment
from . import api

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

cart_timeout = api.get_cart_expire_time

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

WEEK =[u"月", u"火", u"水", u"木", u"金", u"土", u"日"]
def create_time_label(start, end):
    only_start_format = u"{start.year}年{start.month}月{start.day}日({start_week}) {start:%H:%M}"
    range_format = u"{start.year}年{start.month}月{start.day}日({start_week}) - {end.year}年{end.month}月{end.day}日({end_week})"
    same_year_format = u"{start.year}年{start.month}月{start.day}日({start_week}) - {end.month}月{end.day}日({end_week})"

    date_format = only_start_format

    start_week = WEEK[start.weekday()]
    end_week = None

    if end:
        end_week = WEEK[end.weekday()]
        if start.year != end.year or start.month != end.month or start.day != end.day:
            date_format = range_format
            if start.year == end.year:
                date_format = same_year_format
    return date_format.format(start=start, end=end, start_week=start_week, end_week=end_week)

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
    return u"%d年%d月%d日(%s)" % (date.year, date.month, date.day, u"月火水木金土日"[date.weekday()])

def japanese_week(date):
    return u"%d年%d月%d日 %d時%02d分(%s)" % (date.year, date.month, date.day, date.hour, date.minute, u"月火水木金土日"[date.weekday()])

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
def error_list(request, form_or_field, name=None):
    if isinstance(form_or_field, Field):
        field = form_or_field
    else:
        if name is None:
            raise TypeError('name must be specified when the second parameter is Form')
        field = form_or_field[name]

    errors = field.errors
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
    # 複数枚の場合販売単位などは出さない
    return u"×{{num}}"

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


def get_availability_text(quantity, all_quantity, middle_stock_threshold, middle_stock_threshold_percent):
    if middle_stock_threshold_percent is None:
        middle_stock_threshold_percent = 50
    if middle_stock_threshold is None:
        middle_stock_threshold = 20

    if quantity <= 0:
        return u'×'

    if middle_stock_threshold_percent:
        if quantity < (Decimal(all_quantity) / 100 * middle_stock_threshold_percent):
            return u'△'

    if middle_stock_threshold:
        if quantity < middle_stock_threshold:
            return u'△'

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

def sensible_widget(request, widget):
    if IMobileRequest.providedBy(request):
        if isinstance(widget, ListWidget):
            return OurListWidget(outer_html_tag=None, inner_html_tag=None, inner_html_post='<br />', prefix_label=widget.prefix_label)
        elif isinstance(widget, OurListWidget):
            return OurListWidget(outer_html_tag=None, inner_html_tag=None, inner_html_post='<br />', prefix_label=widget.prefix_label, rendrant_factory=widget.rendrant_factory, subfield_id_formatter=widget.subfield_id_formatter)
        elif isinstance(widget, CheckboxMultipleSelect):
            return CheckboxMultipleSelect(multiple=widget.multiple, inner_html_post='<br />')
        elif isinstance(widget, OurDateWidget):
            return OurDateWidget(input_builder=build_date_input_japanese_japan, class_prefix=widget.class_prefix, placeholders=None)
    elif ISmartphoneRequest.providedBy(request):
        if isinstance(widget, ListWidget):
            return OurListWidget(outer_html_tag=None, inner_html_tag=None, inner_html_post='<br />', prefix_label=widget.prefix_label)
        elif isinstance(widget, OurListWidget):
            return OurListWidget(outer_html_tag=None, inner_html_tag=None, inner_html_post='<br />', prefix_label=widget.prefix_label, rendrant_factory=widget.rendrant_factory, subfield_id_formatter=widget.subfield_id_formatter)
        elif isinstance(widget, CheckboxMultipleSelect):
            return CheckboxMultipleSelect(multiple=widget.multiple, inner_html_post='<br />')
    return widget

def sensible_coerce(request, value):
    if value is None:
        return u'(未回答)'
    elif isinstance(value, list):
        if len(value) == 0:
            return u'(選択なし)'
        if IMobileRequest.providedBy(request) or ISmartphoneRequest.providedBy(request):
            return u', '.join(value)
        else:
            return Markup(u''.join(
                [u'<ul>'] \
                + [u'<li>%s</li>' % escape(v) for v in value] \
                + ['</ul>'])
                )
    return value

def safe_get_contact_url(request, default=""):
    try:
        return api.get_contact_url(request, Exception)
    except Exception as e:
        logger.warn(str(e))
        return default

class SwitchingMarkup(object):
    def __init__(self, pc_or_smartphone_text, mobile_text):
        self.pc_or_smartphone_text = pc_or_smartphone_text
        self.mobile_text = mobile_text

    def __html__(self):
        from pyramid.threadlocal import get_current_request
        if IMobileRequest.providedBy(get_current_request()):
            return self.mobile_text
        else:
            return self.pc_or_smartphone_text

def error(names):
    request = get_current_request()
    if not isinstance(names, list):
        names = [names]
    errs = dict()
    for name in names:
        if isinstance(name, Field):
            for err in name.errors:
                errs[err] = err
        else:
            comps = name.split('.')
            if not hasattr(request, 'errors'):
                return ''
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
    return render_errors(request, errs.values())

def render_errors(request, errors):
    if not errors:
        return u''
    if IMobileRequest.providedBy(request):
        return Markup('<font color="red">%s</font><br />' % u', '.join(errors))
    else:
        return Markup('<p class="error">%s</p>' % u', '.join(errors))

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

from altair.app.ticketing.helpers.base import is_required

### 
from collections import namedtuple
import re

rgba = namedtuple('rgba', ('r', 'g', 'b', 'a'))

color_code_table = {
    'aliceblue': rgba(240, 248, 255, 1.), 
    'antiquewhite': rgba(250, 235, 215, 1.), 
    'aqua': rgba(0, 255, 255, 1.), 
    'aquamarine': rgba(127, 255, 212, 1.), 
    'azure': rgba(240, 255, 255, 1.), 
    'beige': rgba(245, 245, 220, 1.), 
    'bisque': rgba(255, 228, 196, 1.), 
    'black': rgba(0, 0, 0, 1.), 
    'blanchedalmond': rgba(255, 235, 205, 1.), 
    'blue': rgba(0, 0, 255, 1.), 
    'blueviolet': rgba(138, 43, 226, 1.), 
    'brown': rgba(165, 42, 42, 1.), 
    'burlywood': rgba(222, 184, 135, 1.), 
    'cadetblue': rgba(95, 158, 160, 1.), 
    'chartreuse': rgba(127, 255, 0, 1.), 
    'chocolate': rgba(210, 105, 30, 1.), 
    'coral': rgba(255, 127, 80, 1.), 
    'cornflowerblue': rgba(100, 149, 237, 1.), 
    'cornsilk': rgba(255, 248, 220, 1.), 
    'crimson': rgba(220, 20, 60, 1.), 
    'cyan': rgba(0, 255, 255, 1.), 
    'darkblue': rgba(0, 0, 139, 1.), 
    'darkcyan': rgba(0, 139, 139, 1.), 
    'darkgoldenrod': rgba(184, 134, 11, 1.), 
    'darkgray': rgba(169, 169, 169, 1.), 
    'darkgreen': rgba(0, 100, 0, 1.), 
    'darkgrey': rgba(169, 169, 169, 1.), 
    'darkkhaki': rgba(189, 183, 107, 1.), 
    'darkmagenta': rgba(139, 0, 139, 1.), 
    'darkolivegreen': rgba(85, 107, 47, 1.), 
    'darkorange': rgba(255, 140, 0, 1.), 
    'darkorchid': rgba(153, 50, 204, 1.), 
    'darkred': rgba(139, 0, 0, 1.), 
    'darksalmon': rgba(233, 150, 122, 1.), 
    'darkseagreen': rgba(143, 188, 143, 1.), 
    'darkslateblue': rgba(72, 61, 139, 1.), 
    'darkslategray': rgba(47, 79, 79, 1.), 
    'darkslategrey': rgba(47, 79, 79, 1.), 
    'darkturquoise': rgba(0, 206, 209, 1.), 
    'darkviolet': rgba(148, 0, 211, 1.), 
    'deeppink': rgba(255, 20, 147, 1.), 
    'deepskyblue': rgba(0, 191, 255, 1.), 
    'dimgray': rgba(105, 105, 105, 1.), 
    'dimgrey': rgba(105, 105, 105, 1.), 
    'dodgerblue': rgba(30, 144, 255, 1.), 
    'firebrick': rgba(178, 34, 34, 1.), 
    'floralwhite': rgba(255, 250, 240, 1.), 
    'forestgreen': rgba(34, 139, 34, 1.), 
    'fuchsia': rgba(255, 0, 255, 1.), 
    'gainsboro': rgba(220, 220, 220, 1.), 
    'ghostwhite': rgba(248, 248, 255, 1.), 
    'gold': rgba(255, 215, 0, 1.), 
    'goldenrod': rgba(218, 165, 32, 1.), 
    'gray': rgba(128, 128, 128, 1.), 
    'green': rgba(0, 128, 0, 1.), 
    'greenyellow': rgba(173, 255, 47, 1.), 
    'grey': rgba(128, 128, 128, 1.), 
    'honeydew': rgba(240, 255, 240, 1.), 
    'hotpink': rgba(255, 105, 180, 1.), 
    'indianred': rgba(205, 92, 92, 1.), 
    'indigo': rgba(75, 0, 130, 1.), 
    'ivory': rgba(255, 255, 240, 1.), 
    'khaki': rgba(240, 230, 140, 1.), 
    'lavender': rgba(230, 230, 250, 1.), 
    'lavenderblush': rgba(255, 240, 245, 1.), 
    'lawngreen': rgba(124, 252, 0, 1.), 
    'lemonchiffon': rgba(255, 250, 205, 1.), 
    'lightblue': rgba(173, 216, 230, 1.), 
    'lightcoral': rgba(240, 128, 128, 1.), 
    'lightcyan': rgba(224, 255, 255, 1.), 
    'lightgoldenrodyellow': rgba(250, 250, 210, 1.), 
    'lightgray': rgba(211, 211, 211, 1.), 
    'lightgreen': rgba(144, 238, 144, 1.), 
    'lightgrey': rgba(211, 211, 211, 1.), 
    'lightpink': rgba(255, 182, 193, 1.), 
    'lightsalmon': rgba(255, 160, 122, 1.), 
    'lightseagreen': rgba(32, 178, 170, 1.), 
    'lightskyblue': rgba(135, 206, 250, 1.), 
    'lightslategray': rgba(119, 136, 153, 1.), 
    'lightslategrey': rgba(119, 136, 153, 1.), 
    'lightsteelblue': rgba(176, 196, 222, 1.), 
    'lightyellow': rgba(255, 255, 224, 1.), 
    'lime': rgba(0, 255, 0, 1.), 
    'limegreen': rgba(50, 205, 50, 1.), 
    'linen': rgba(250, 240, 230, 1.), 
    'magenta': rgba(255, 0, 255, 1.), 
    'maroon': rgba(128, 0, 0, 1.), 
    'mediumaquamarine': rgba(102, 205, 170, 1.), 
    'mediumblue': rgba(0, 0, 205, 1.), 
    'mediumorchid': rgba(186, 85, 211, 1.), 
    'mediumpurple': rgba(147, 112, 219, 1.), 
    'mediumseagreen': rgba(60, 179, 113, 1.), 
    'mediumslateblue': rgba(123, 104, 238, 1.), 
    'mediumspringgreen': rgba(0, 250, 154, 1.), 
    'mediumturquoise': rgba(72, 209, 204, 1.), 
    'mediumvioletred': rgba(199, 21, 133, 1.), 
    'midnightblue': rgba(25, 25, 112, 1.), 
    'mintcream': rgba(245, 255, 250, 1.), 
    'mistyrose': rgba(255, 228, 225, 1.), 
    'moccasin': rgba(255, 228, 181, 1.), 
    'navajowhite': rgba(255, 222, 173, 1.), 
    'navy': rgba(0, 0, 128, 1.), 
    'oldlace': rgba(253, 245, 230, 1.), 
    'olive': rgba(128, 128, 0, 1.), 
    'olivedrab': rgba(107, 142, 35, 1.), 
    'orange': rgba(255, 165, 0, 1.), 
    'orangered': rgba(255, 69, 0, 1.), 
    'orchid': rgba(218, 112, 214, 1.), 
    'palegoldenrod': rgba(238, 232, 170, 1.), 
    'palegreen': rgba(152, 251, 152, 1.), 
    'paleturquoise': rgba(175, 238, 238, 1.), 
    'palevioletred': rgba(219, 112, 147, 1.), 
    'papayawhip': rgba(255, 239, 213, 1.), 
    'peachpuff': rgba(255, 218, 185, 1.), 
    'peru': rgba(205, 133, 63, 1.), 
    'pink': rgba(255, 192, 203, 1.), 
    'plum': rgba(221, 160, 221, 1.), 
    'powderblue': rgba(176, 224, 230, 1.), 
    'purple': rgba(128, 0, 128, 1.), 
    'red': rgba(255, 0, 0, 1.), 
    'rosybrown': rgba(188, 143, 143, 1.), 
    'royalblue': rgba(65, 105, 225, 1.), 
    'saddlebrown': rgba(139, 69, 19, 1.), 
    'salmon': rgba(250, 128, 114, 1.), 
    'sandybrown': rgba(244, 164, 96, 1.), 
    'seagreen': rgba(46, 139, 87, 1.), 
    'seashell': rgba(255, 245, 238, 1.), 
    'sienna': rgba(160, 82, 45, 1.), 
    'silver': rgba(192, 192, 192, 1.), 
    'skyblue': rgba(135, 206, 235, 1.), 
    'slateblue': rgba(106, 90, 205, 1.), 
    'slategray': rgba(112, 128, 144, 1.), 
    'slategrey': rgba(112, 128, 144, 1.), 
    'snow': rgba(255, 250, 250, 1.), 
    'springgreen': rgba(0, 255, 127, 1.), 
    'steelblue': rgba(70, 130, 180, 1.), 
    'tan': rgba(210, 180, 140, 1.), 
    'teal': rgba(0, 128, 128, 1.), 
    'thistle': rgba(216, 191, 216, 1.), 
    'tomato': rgba(255, 99, 71, 1.), 
    'turquoise': rgba(64, 224, 208, 1.), 
    'violet': rgba(238, 130, 238, 1.), 
    'wheat': rgba(245, 222, 179, 1.), 
    'white': rgba(255, 255, 255, 1.), 
    'whitesmoke': rgba(245, 245, 245, 1.), 
    'yellow': rgba(255, 255, 0, 1.), 
    'yellowgreen': rgba(154, 205, 50, 1.),
    };

def parse_color(s):
    rt = color_code_table.get(s)
    if rt is not None:
        return rt
    g = re.match(ur'^\s*(?:#(?:([0-9A-Fa-f])([0-9A-Fa-f])([0-9A-Fa-f])|([0-9A-Fa-f]{2})([0-9A-Fa-f]{2})([0-9A-Fa-f]{2})([0-9A-Fa-f]{2})?)|rgb\(([^)]*)\)|rgba\(([^)]*)\))\s*$', s)
    if not g:
        raise ValueError("Invalid color specifier: " + s);

    rt = [0, 0, 0, 1.];
    if g.group(1) is not None:
        for i in range(1, 4):
            v = int(g.group(i), 16)
            rt[i - 1] = v | (v << 4)
    elif g.group(4) is not None:
        for i in range(4, 7):
            v = g.group(i)
            rt[i - 4] = int(v, 16)
        if g.group(7) is not None:
            rt[3] = float(int(g.group(7), 16)) / 255.
    elif g.group(8) is not None:
        s = g.group(8).split(',')
        if s.length != 3:
            raise ValueError("Invalid color specifier: " + s)
        for i, v in enumerate(s):
            rt[i] = int(v.strip())
    elif g.group(9) is not None:
        s = g.group(9).split(',')
        if s.length != 4:
            raise ValueError("Invalid color specifier: " + s)
        for i, v in enumerate(s[0:3]):
            rt[i] = int(v.strip())
        rt[3] = float(s[3].strip())
    return rgba(*rt)

def to_hex_color(c):
    return u'#%02x%02x%02x' % c[0:3]

def _blend(a, b, r):
    ir = 1.0 - r
    return rgba(
        int(min(max(a[0] * ir + b[0] * r, 0.), 255.)),
        int(min(max(a[1] * ir + b[1] * r, 0.), 255.)),
        int(min(max(a[2] * ir + b[2] * r, 0.), 255.)),
        float(min(max(a[3] * ir + b[3] * r, 0.), 1.))
        )

def _natural_blend(a, b, r):
    mu = ((a.r + a.g + a.b) - (b.r + b.g + b.b)) / 765.
    ir = (1 - mu) * r * r + mu * r
    return _blend(a, b, ir)

def blend(a, b, r):
    if isinstance(a, basestring):
        a = parse_color(a)
    if isinstance(b, basestring):
        b = parse_color(b)
    return _natural_blend(a, b, r)

def darken(a, r):
    if isinstance(a, basestring):
        a = parse_color(a)
    return _natural_blend(a, rgba(0, 0, 0, 1.), r)

def lighten(a, r):
    if isinstance(a, basestring):
        a = parse_color(a)
    return _natural_blend(a, rgba(255, 255, 255, 1.), r)
