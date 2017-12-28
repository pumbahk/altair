# -*- coding: utf-8 -*-

from datetime import datetime

from sqlalchemy.orm.exc import NoResultFound
from .models import DiscountCodeSetting, DiscountCodeCode, UsedDiscountCodeCart, UsedDiscountCodeOrder


def is_enabled_discount_code_checked(context, request):
    """
    クーポン・割引コードの使用設定がONになっているか確認
    requestは使用できていないが、使用場所がcustom_predicatesのために必要。
    """
    return context.user.organization.setting.enable_discount_code


def get_discount_setting_related_data(context, request):
    """DiscountCodeSettingとそれに紐づく関連テーブルのレコードを取得"""
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


# order_likeには、cartと、_DummyCart、Orderが入る想定
def get_used_discount_codes(order_like):
    codes_list = list()
    for item in order_like.items:
        for element in item.elements:
            codes_list.extend(element.used_discount_codes)
    return codes_list


def get_used_discount_quantity(order_like):
    quantity = 0
    for item in order_like.items:
        for element in item.elements:
            used_codes = element.used_discount_codes
            if used_codes:
                quantity = quantity + len(used_codes)
    return quantity


def get_discount_amount(order_like):
    discount_amount = 0
    for item in order_like.items:
        for element in item.elements:
            used_codes = element.used_discount_codes
            if used_codes:
                discount_amount = discount_amount + element.product_item.price * len(used_codes)
    return discount_amount


def enable_discount_code(organization):
    return organization.setting.enable_discount_code


def temporarily_save_discount_code(codes):
    # carted_product_itemのIDと、使用したコードを保存する
    for code_dict in codes:
        if code_dict['form'].code.data:
            # TODO イーグルス発行のコードの場合は使えない
            #available_code = DiscountCodeCode.query.filter(
            #    DiscountCodeCode.code == code_dict['code'],
            #    DiscountCodeCode.used_at.is_(None)
            #).one()

            use_discount_code = UsedDiscountCodeCart()
            #use_discount_code.discount_code_id = available_code.id
            use_discount_code.code = code_dict['form'].code.data
            use_discount_code.carted_product_item_id = code_dict['carted_product_item'].id
            use_discount_code.add()
    return True


def save_discount_code(carted_product_item, ordered_product_item):
    # 対象のCartedProductItemにクーポンが使用されていたら、UsedDiscountCodeOrderにデータを記録する
    used_discount_code_carts = carted_product_item.used_discount_codes

    for index, used_discount_code_cart in enumerate(used_discount_code_carts):
        use_discount_code_order = UsedDiscountCodeOrder()
        #use_discount_code_order.discount_code_id = used_discount_code_carts[0].discount_code_id
        use_discount_code_order.code = used_discount_code_cart.code
        use_discount_code_order.ordered_product_item = ordered_product_item
        use_discount_code_order.ordered_product_item_token = ordered_product_item.tokens[index]
        use_discount_code_order.add()

        # クーポン・割引コードテーブルに使用日時を記載
        # TODO イーグルス発行のコードの場合は使えない
        #available_code = DiscountCodeCode.query.filter_by(id=used_discount_code_cart.discount_code_id).one()
        #available_code.used_at = datetime.now()
        #available_code.save()
    return True


def get_discount_code_setting(used_discount_code_cart):
    settings = DiscountCodeSetting.\
        filter(DiscountCodeSetting.first_4_digits == used_discount_code_cart.code[:4]).\
        filter(DiscountCodeSetting.is_valid==True).all()
    return settings
