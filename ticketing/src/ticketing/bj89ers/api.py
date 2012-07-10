# -*- coding:utf-8 -*-

import ticketing.orders.models as o_models
from .models import DBSession

SESSION_KEY = 'bj89ers.user_profile'

def store_user_profile(request, user_profile):
    request.session[SESSION_KEY] = user_profile

def load_user_profile(request):
    return request.session[SESSION_KEY]

def on_order_completed(event):
    order = event.order

    user_profile = load_user_profile(event.request)

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
    u'tel1_1',
    u'tel1_2',
    u'tel1_3',
    u'tel2_1',
    u'tel2_2',
    u'tel2_3',
    u'email',
    ]


def set_user_profile_for_order(request, order, bj89er_user_profile):
    member_type = bj89er_user_profile['member_type']
    # ordered_product = o_models.OrderedProduct.query.filter(
    #     o_models.OrderedProduct.order==order
    # ).filter(
    #     o_models.OrderedProduct.product_id==member_type
    # ).one()

    ordered_product_item = o_models.OrderedProductItem.query.filter(
        o_models.OrderedProduct.order==order
    ).filter(
        o_models.OrderedProduct.product_id==member_type
    ).filter(
        o_models.OrderedProductItem.ordered_product_id==o_models.OrderedProduct.id
    ).first()

    for attr_name in attr_names:
        o_models.OrderedProductAttribute(ordered_product_item=ordered_product_item,
            name=attr_name,
            value=bj89er_user_profile[attr_name])

