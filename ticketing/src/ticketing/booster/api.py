# encoding: utf-8
from pyramid.interfaces import IRequest
from .interfaces import IBoosterSettings
from .interfaces import IPertistentProfileFactory

def get_booster_settings(request):
    return request.registry.getUtility(IBoosterSettings)

SESSION_KEY = 'booster.89ers.user_profile'

def remove_user_profile(request):
    if SESSION_KEY in request.session:
        del request.session[SESSION_KEY]

def store_user_profile(request, user_profile):
    request.session[SESSION_KEY] = user_profile

def load_user_profile(request):
    return request.session.get(SESSION_KEY)

def clear_user_profile(request):
    if SESSION_KEY in request.session:
        del request.session[SESSION_KEY]

def get_order_desc(request, order):
    shipping = order.shipping_address
    return shipping, get_user_profile_from_order(request, order)

def get_persistent_userprofile(request):
    factory = request.registry.adapters.lookup([IRequest], IPertistentProfileFactory, "")
    return factory(request)

def set_user_profile_for_order(request, order, user_profile):
    return get_persistent_userprofile(request).set_user_profile(order, user_profile)

def get_user_profile_from_order(request, order):
    return get_persistent_userprofile(request).get_user_profile(order)
