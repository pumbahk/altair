# encoding: utf-8

from .interfaces import IBoosterSettings

def get_booster_settings(request):
    return request.registry.getUtility(IBoosterSettings)

## old:
import ticketing.core.models as c_models

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

def on_order_completed(event):
    order = event.order

    user_profile = load_user_profile(event.request)
    set_user_profile_for_order(event.request, order, user_profile)

def get_order_desc(order):
    shipping = order.shipping_address
    return shipping, get_main_ordered_product_from_order(order).attributes

def get_main_ordered_product_from_order(order):
    return order.items[0].ordered_product_items[0]

attr_names = [
    u'cont',
    u'old_id_number',
    u'member_type',
    u't_shirts_size',
    u'year',
    u'month',
    u'day',
    u'sex',
    u'mail_permission', ###
    u'publicity'
    u'fax', 
    u'product_delivery_method_name', 
    ]


def set_user_profile_for_order(request, order, bj89er_user_profile):
    member_type = bj89er_user_profile['member_type']
    ordered_product_item = c_models.OrderedProductItem.query.filter(
        c_models.OrderedProduct.order==order
    ).filter(
        c_models.OrderedProduct.product_id==member_type
    ).filter(
        c_models.OrderedProductItem.ordered_product_id==c_models.OrderedProduct.id
    ).first()

    for attr_name in attr_names:
        if attr_name in bj89er_user_profile:
            c_models.OrderedProductAttribute(
                ordered_product_item=ordered_product_item,
                name=attr_name,
                value=bj89er_user_profile.get(attr_name))

def filtering_data_by_products_and_member_type(data, products):
    k = data.get("member_type")
    product = products.get(str(k))
    if not len(product.items) > 1:
        data["t_shirts_size"] = None
    return data

def product_item_is_t_shirt(product_item):
    return product_item.stock.stock_type.name == u'Tシャツ'

def product_includes_t_shirt(product):
    return any(product_item_is_t_shirt(product_item) for product_item in product.items)
