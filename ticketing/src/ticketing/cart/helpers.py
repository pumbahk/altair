from webhelpers.number import format_number as _format_number
from .models import Cart

def format_number(num, thousands=","):
    return _format_number(int(num), thousands)

def set_cart(request, cart):
    request.session['ticketing.cart_id'] = cart.id
    request._cart = cart

def get_cart(request):
    if hasattr(request, '_cart'):
        return request._cart

    cart_id = request.session.get('ticketing.cart_id')
    if cart_id is None:
        return None

    request._cart = Cart.query.filter(Cart.id==cart_id).first()
    return request._cart

def remove_cart(request):
    if hasattr(request, '_cart'):
        delattr(request, '_cart')
    del request.session['ticketing.cart_id']

def has_cart(request):
    return 'ticketing.cart_id' in request.session or hasattr(request, '_cart')

def get_item_name(request, performance):
    base_item_name = request.registry.settings['cart.item_name']
    return maybe_encoded(base_item_name) + " " + performance.name

def maybe_encoded(s, encoding='utf-8'):
    if isinstance(s, unicode):
        return s
    return s.decode(encoding)
