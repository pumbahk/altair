import re
from webob.multidict import MultiDict
import itertools
from sqlalchemy.orm.exc import NoResultFound
from ticketing.core.models import (
    ShippingAddress,
    Product,
    Performance,
)

SHIPPING_ATTRS = (
    "email", 
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

wished_performance_id_pt = r"^performance-(?P<wish_order>\d+)$"
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

def add_wished_product_names(wishes):
    results = []
    for wish in wishes:
        reversed_wish = []
        performance_id = wish['performance_id']
        for w in wish['wished_products']:
            p = Product.query.filter(Product.id==w['product_id']).one()
            perf = Performance.query.filter(Performance.id==performance_id).one()
            reversed_wish.append(dict(wish_order=w['wish_order'], quantity=w['quantity'], product=p, performance=perf))

        results.append(reversed_wish)
    return results

def convert_shipping_address(params):
    shipping_address = ShippingAddress()
    for attr in SHIPPING_ATTRS:
        if attr in params:
            setattr(shipping_address, attr, params[attr])
    return shipping_address

def shipping_address_form_data(shipping_address):
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
        "mail_address": s.email,
        "tel": s.tel_1,
        "mobile_tel": s.tel_2,
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

