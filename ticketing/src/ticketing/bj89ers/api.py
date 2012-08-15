# -*- coding:utf-8 -*-

import ticketing.core.models as c_models
from .models import DBSession

SESSION_KEY = 'bj89ers.user_profile'

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

def on_order_completed(event):
    order = event.order

    user_profile = load_user_profile(event.request)
    print user_profile
    set_user_profile_for_order(event.request, order, user_profile)


attr_names = [
    u'cont',
    u'old_id_number',
    u'member_type',
    u't_shirts_size',
    u'first_name',
    u'last_name',
    u'first_name_kana',
    u'last_name_kana',
    u'year',
    u'month',
    u'day',
    u'sex',
    u'zipcode1',
    u'zipcode2',
    u'prefecture',
    u'city',
    u'address1',
    u'address2',
    u'tel_1',
    u'tel_2',
    u'email',
    u'mail_permission',
    ]


def set_user_profile_for_order(request, order, bj89er_user_profile):
    member_type = bj89er_user_profile['member_type']
    # ordered_product = c_models.OrderedProduct.query.filter(
    #     c_models.OrderedProduct.order==order
    # ).filter(
    #     c_models.OrderedProduct.product_id==member_type
    # ).one()

    ordered_product_item = c_models.OrderedProductItem.query.filter(
        c_models.OrderedProduct.order==order
    ).filter(
        c_models.OrderedProduct.product_id==member_type
    ).filter(
        c_models.OrderedProductItem.ordered_product_id==c_models.OrderedProduct.id
    ).first()

    for attr_name in attr_names:
        c_models.OrderedProductAttribute(ordered_product_item=ordered_product_item,
            name=attr_name,
            value=bj89er_user_profile.get(attr_name))

