from .interfaces import IURLBuilder
from . import BUILDERS

def get_event_cart_url_builder(request, name=BUILDERS.cart_events):
    return request.registry.getUtility(IURLBuilder, name=name)

def get_performance_cart_url_builder(request, name=BUILDERS.cart_performances):
    return request.registry.getUtility(IURLBuilder, name=name)

def get_performance_spa_cart_url_builder(request, name=BUILDERS.spa_cart_performances):
    return request.registry.getUtility(IURLBuilder, name=name)

def get_cart_now_url_builder(request, name=BUILDERS.cart_now):
    return request.registry.getUtility(IURLBuilder, name=name)

def get_lots_cart_url_builder(request, name=BUILDERS.lots_cart):
    return request.registry.getUtility(IURLBuilder, name=name)

def get_agreement_cart_url_builder(request, name=BUILDERS.agreement_cart):
    return request.registry.getUtility(IURLBuilder, name=name)

def get_agreement_spa_cart_url_builder(request, name=BUILDERS.agreement_spa_cart):
    return request.registry.getUtility(IURLBuilder, name=name)

def get_agreement_lots_cart_url_builder(request, name=BUILDERS.agreement_lots_cart):
    return request.registry.getUtility(IURLBuilder, name=name)

def get_orderreview_qr_url_builder(request, name=BUILDERS.orderreview_qr):
    return request.registry.getUtility(IURLBuilder, name=name)

def get_orderreview_skidata_qr_url_builder(request, name=BUILDERS.orderreview_skidata_qr):
    return request.registry.getUtility(IURLBuilder, name=name)
