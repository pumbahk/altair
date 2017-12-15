# encoding: utf-8

from sqlalchemy.orm.exc import NoResultFound
from .models import DiscountCodeSetting, UsedDiscountCodeCart, UsedDiscountCodeOrder


def is_enabled_discount_code_checked(context, request):
    """
    クーポン・割引コードの使用設定がONになっているか確認
    requestは使用できていないが、使用場所がcustom_predicatesのために必要。
    """
    return context.user.organization.setting.enable_discount_code


def get_discount_setting(context, request):
    """DiscountCodeSettingとそれに紐づくDiscountCodeのレコードの取得"""
    setting_id = request.matchdict['setting_id']

    query = context.session.query(DiscountCodeSetting).filter_by(
        organization_id=context.user.organization_id,
        id=setting_id
    )

    try:
        context.setting = query.one()
        return True
    except NoResultFound:
        return False


def get_code_type(order_like):
    from ..cart.api import _DummyCart
    from ..cart.models import Cart
    from ..orders.models import Order
    item_code_type = None
    if type(order_like) in [Cart, _DummyCart]:
        item_code_type = UsedDiscountCodeCart.carted_product_item_id
    if type(order_like) == Order:
        item_code_type = UsedDiscountCodeOrder.ordered_product_item_id
    return item_code_type


def get_used_discount_code_model(order_like):
    from ..cart.api import _DummyCart
    from ..cart.models import Cart
    from ..orders.models import Order
    model = None
    if type(order_like) in [Cart, _DummyCart]:
        model = UsedDiscountCodeCart
    if type(order_like) == Order:
        model = UsedDiscountCodeOrder
    return model


# order_likeには、cartと、_DummyCart、Orderが入る想定
def get_used_discount_codes(order_like):
    codes_list = list()
    model = get_used_discount_code_model(order_like)
    code_type = get_code_type(order_like)
    for item in order_like.items:
        for element in item.elements:
            used_codes = model.query.filter(code_type == element.id).all()
            for used_code in used_codes:
                codes_list.append(used_code)
    return codes_list


def get_used_discount_quantity(order_like):
    quantity = 0
    model = get_used_discount_code_model(order_like)
    code_type = get_code_type(order_like)
    for item in order_like.items:
        for element in item.elements:
            used_codes = model.query.filter(code_type == element.id).all()
            if used_codes:
                quantity = quantity + len(used_codes)
    return quantity


def get_discount_amount(order_like):
    discount_amount = 0
    model = get_used_discount_code_model(order_like)
    code_type = get_code_type(order_like)
    for item in order_like.items:
        for element in item.elements:
            used_codes = model.query.filter(code_type == element.id).all()
            if used_codes:
                discount_amount = discount_amount + element.product_item.price*len(used_codes)
    return discount_amount


def enable_discount_code(organization):
    return organization.setting.enable_discount_code


def temporarily_save_discount_code(codies):
    # carted_product_itemのIDと、使用したコードを保存する
    for code_dict in codies:
        if code_dict['code']:
            use_discount_code = UsedDiscountCodeCart()
            use_discount_code.code = code_dict['code']
            use_discount_code.carted_product_item_id = code_dict['carted_product_item'].id
            use_discount_code.add()
    return True


def save_discount_code(carted_product_item, ordered_product_item):
    # 対象のCartedProductItemにクーポンが使用されていたら、UsedDiscountCodeOrderにデータを記録する
    # TODO OKADA　クーポンを使用してるかの判定
    if True:
        used_discount_code_carts = UsedDiscountCodeCart.query.\
            filter(UsedDiscountCodeCart.carted_product_item_id == carted_product_item.id).all()

        for used_discount_code_cart in used_discount_code_carts:
            use_discount_code_order = UsedDiscountCodeOrder()
            use_discount_code_order.code = used_discount_code_cart.code
            use_discount_code_order.ordered_product_item_id = ordered_product_item.id
            use_discount_code_order.add()
    return True
