from .interfaces import IURLBuilder
from . import BUILDERS

def get_cart_url_builder(request, name=BUILDERS.cart):
    return request.registry.getUtility(IURLBuilder, name=name)

def get_cart_now_url_builder(request, name=BUILDERS.cart_now):
    return request.registry.getUtility(IURLBuilder, name=name)
