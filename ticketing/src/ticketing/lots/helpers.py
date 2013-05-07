# encoding: utf-8

import re
from webob.multidict import MultiDict
import itertools
import json
from sqlalchemy.orm.exc import NoResultFound
from markupsafe import Markup
from ticketing.formhelpers.widgets.list import OurListWidget
from wtforms.validators import Required
from .models import LotEntryStatusEnum
from ticketing.users.helpers import format_sex
from cgi import escape
from ticketing.core.models import (
    ShippingAddress,
    Product,
    Performance,
)

from ticketing.cart.helpers import (
    japanese_date,
    japanese_time,
    japanese_datetime,
    fee_type,
    format_number,
    format_currency,
    get_nickname,
    error_list,
)

SHIPPING_ATTRS = (
    "email_1",
    "email_2",
    "nick_name",
    "first_name",
    "last_name",
    "first_name_kana",
    "last_name_kana",
    "sex",
    "zip",
    "country",
    "prefecture",
    "city",
    "address_1",
    "address_2",
    "tel_1",
    "tel_2",
    "fax",
)

wished_performance_id_pt = r"^performanceDate-(?P<wish_order>\d+)$"
wished_product_id_pt = r"^product-id-(?P<wish_order>\d+)-(?P<wished_product_order>\d+)$"
wished_product_quantity_pt = r"^product-quantity-(?P<wish_order>\d+)-(?P<wished_product_order>\d+)$"
wished_performance_id_re = re.compile(wished_performance_id_pt)
wished_product_id_re = re.compile(wished_product_id_pt)
wished_product_quantity_re = re.compile(wished_product_quantity_pt)

# def convert_wishes(params, limit):
#     """ wish_order, product_id, quantity
#     """
# 
#     q = ((wished_product_re.match(p), params[p]) for p in params)
#     aggregated = itertools.groupby(sorted(((int(m.groupdict()['wish_order']), m.groupdict()['product_id'], int(v)) for m, v in q if m is not None)), 
#         key=lambda r: r[0])
#     return [list(v) for _, v in aggregated][:limit]

def convert_wishes(params, limit):
    performances  = ((wished_performance_id_re.match(p), params[p]) for p in params)
    products  = ((wished_product_id_re.match(p), params[p]) for p in params)
    quantities = ((wished_product_quantity_re.match(p), params[p]) for p in params)

    performance_ids = {}
    for m, param_value in performances:
        if m is None:
            continue
        gdict = m.groupdict()
        key = int(gdict['wish_order'])
        performance_ids[key] = param_value


    product_ids = {}
    for m, param_value in products:
        if m is None:
            continue
        gdict = m.groupdict()
        key = (int(gdict['wish_order']), gdict['wished_product_order'])
        product_ids[key] = param_value

    wished_quantities = {}
    for m, param_value in quantities:
        if m is None:
            continue
        if not param_value:
            continue
        gdict = m.groupdict()
        key = (int(gdict['wish_order']), gdict['wished_product_order'])
        wished_quantities[key] = int(param_value)

    results = {}
    for key, product_id in product_ids.items():
        wish_order = key[0]
        performance_id = performance_ids[wish_order]
        if key not in wished_quantities:
            continue
        quantity = wished_quantities[key]
        wishset = results.get(wish_order, [])
        wishset.append(dict(wish_order=wish_order, product_id=product_id, quantity=quantity))
        results[wish_order] = wishset
        
    return [dict(performance_id=performance_ids[x], wished_products=results[x]) for x in sorted(results)]

def decorate_options_mobile(options):
    options = [
        dict(
            performance=Performance.query.filter_by(id=data['performance_id']).one(),
            wished_products=[
                dict(
                    product=Product.query.filter_by(id=rec['product_id']).one(),
                    **rec
                    )
                for rec in data['wished_products']
                ]
            )
        for data in options
        ]

    for option in options:
        for wished_product in option['wished_products']:
            wished_product['subtotal'] = wished_product['product'].price * wished_product['quantity']

    for data in options:
        data['total_amount_without_fee'] = sum(rec['product'].price * rec['quantity'] for rec in data['wished_products'])
    return options

def build_wishes_dicts_from_entry(entry):
    result = []
    for wish in entry.wishes:
        result.append(dict(
            performance=wish.performance,
            wish_order=wish.wish_order,
            wished_products=[
                dict(product=rec.product, quantity=rec.quantity)
                for rec in wish.products
                ]
            ))
    return result

def convert_shipping_address(params):
    shipping_address = ShippingAddress()
    for attr in SHIPPING_ATTRS:
        if attr in params:
            setattr(shipping_address, attr, params[attr])
    return shipping_address

def shipping_address_form_data(shipping_address, gender=None):
    s = shipping_address
    return MultiDict({
        "first_name": s.first_name,
        "last_name": s.last_name,
        "first_name_kana": s.first_name_kana,
        "last_name_kana": s.last_name_kana,
        "zip": s.zip,
        "prefecture": s.prefecture,
        "city": s.city,
        "address_1": s.address_1,
        "address_2": s.address_2,
        "email_1": s.email_1,
        "email_1_confirm": s.email_1,
        "sex": gender,
        "tel_1": s.tel_1,
        "tel_2": s.tel_2,
        "fax": s.fax,
    })

def validate_token(request):

    # begin token check
    entry = request.session.get('lots.entry')
    if not entry:
        return False

    session_token = entry.get('token')
    remote_token = request.params.get('token')

    if remote_token is None or session_token is None:
        return False

    if session_token != request.params['token']:
        return False

    return True

def render_mobile_error(msg):
    return u'<font color="red">・%s</font><br />' % msg

def mobile_error_list(request, form, name, with_label=False):
    errors = form[name].errors
    if not errors:
        return ""
    
    html = u'<div>'
    html += u"".join([render_mobile_error((u'%s:' % form[name].label.text if with_label else u'') + e)  for e in errors])
    html += u'</div>'
    return Markup(html)

def mobile_list_widget(request):
    return OurListWidget(outer_html_tag=None, inner_html_tag=None, inner_html_post='<br />', prefix_label=False)

def lot_entry_status_as_string(request, status):
    if status == LotEntryStatusEnum.New:
        return u'抽選待ち'
    elif status == LotEntryStatusEnum.Elected:
        return u'当選'
    elif status == LotEntryStatusEnum.Rejected:
        return u'落選'
    elif status == LotEntryStatusEnum.Ordered:
        return u'注文済み'
    return u'???' # never get here

def _enclose_if(content, tag, condition, **kwargs):
    buf = []
    if condition:
        buf.append(u'<')
        buf.append(tag)
        if kwargs:
            buf.append(u' ')
            for k, v in kwargs.items():
                buf.append(escape(k))
                buf.append(u'="')
                buf.append(escape(v))
                buf.append(u'"')
        buf.append(u'>')
    buf.append(content)
    buf.append(u'</')
    buf.append(tag)
    buf.append(u'>')
    return Markup(u''.join(buf))

# see cms/src/altairsite/mobile/core/disphelper.py
def nl2br(s):
    buf = []
    for line in re.finditer(u'^.*$', s, re.MULTILINE):
        buf.append(line.group(0))
        buf.append(u'<br />')
    return Markup(u''.join(buf))

format_gender = format_sex

def tojson(obj):
    return json.dumps(obj) 

def performance_date_label(performance):
    return u'%s %s' % (japanese_date(performance.start_on), performance.venue.name)

def is_required(field):
    required = False
    for v in field.validators:
        if isinstance(v, Required):
            required = True
    return required

def mobile_required_mark():
    return Markup('<sup><font color="#f00">*</font></sup>')
