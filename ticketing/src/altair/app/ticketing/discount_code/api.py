# encoding: utf-8
from sqlalchemy.orm.exc import NoResultFound
from .models import DiscountCodeSetting, UsedDiscountCode


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


def get_used_discount_codes(order_like):
    # order_likeには、cartと、_DummyCart、Orderが入る想定
    codes_list = list()

    def get_code_type(order_like):
        item_code_type = UsedDiscountCode.carted_product_item_id
        if type(order_like) == "Order":
            item_code_type = UsedDiscountCode.ordered_product_item_id
        return item_code_type

    code_type = get_code_type(order_like)
    for item in order_like.items:
        for element in item.elements:
            used_codes = UsedDiscountCode.query.filter(code_type == element.id).all()
            for used_code in used_codes:
                codes_list.append(used_code)
    return codes_list


def calc_discount_quantity(order_like):
    # order_likeには、cartと、_DummyCart、Orderが入る想定
    quantity = 0

    def get_code_type(order_like):
        item_code_type = UsedDiscountCode.carted_product_item_id
        if type(order_like) == "Order":
            item_code_type = UsedDiscountCode.ordered_product_item_id
        return item_code_type

    code_type = get_code_type(order_like)
    for item in order_like.items:
        for element in item.elements:
            used_codes = UsedDiscountCode.query.filter(code_type == element.id).all()
            if used_codes:
                quantity = quantity + len(used_codes)
    return quantity


def calc_discount_amount(order_like):
    # order_likeには、cartと、_DummyCart、Orderが入る想定
    discount_amount = 0

    def get_code_type(order_like):
        item_code_type = UsedDiscountCode.carted_product_item_id
        if type(order_like) == "Order":
            item_code_type = UsedDiscountCode.ordered_product_item_id
        return item_code_type

    code_type = get_code_type(order_like)
    for item in order_like.items:
        for element in item.elements:
            used_codes = UsedDiscountCode.query.filter(code_type == element.id).all()
            if used_codes:
                discount_amount = discount_amount + element.product_item.price*len(used_codes)
    return discount_amount


def enable_discount_code(organization):
    return organization.setting.enable_discount_code


def save_discount_code(carted_product_item, ordered_product_item):
    # TODO OKADA　クーポンを使用してるかの判定
    if True:
        used_discount_code = UsedDiscountCode.query.filter(UsedDiscountCode.carted_product_item_id==carted_product_item.id).first()
        if used_discount_code:
            used_discount_code.ordered_product_item_id = ordered_product_item.id
    return True
