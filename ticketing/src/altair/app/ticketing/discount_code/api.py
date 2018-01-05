# -*- coding: utf-8 -*-

from datetime import datetime

from sqlalchemy.orm.exc import NoResultFound
from .models import DiscountCodeSetting, DiscountCodeCode, UsedDiscountCodeCart, UsedDiscountCodeOrder
from communicators.utils import get_communicator


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


def check_used_discount_code(code):
    return UsedDiscountCodeOrder.query.\
        filter(UsedDiscountCodeOrder.code==code).\
        filter(UsedDiscountCodeOrder.deleted_at==None).\
        first()


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
    setting = DiscountCodeSetting.\
        filter(DiscountCodeSetting.first_4_digits == used_discount_code_cart.code[:4]).\
        filter(DiscountCodeSetting.is_valid==True).all()
    return setting


def get_discount_code_settings(used_discount_code_carts):
    code_first_4_digits = list(set([code.code[:4] for code in used_discount_code_carts]))
    settings = DiscountCodeSetting.\
        filter(DiscountCodeSetting.first_4_digits.in_(code_first_4_digits)).\
        filter(DiscountCodeSetting.is_valid==True).all()
    return settings


def used_discount_code_groups(cart):
    codes = get_used_discount_codes(cart)
    settings = get_discount_code_settings(codes)

    code_groups = {}
    for code in codes:
        if code.code[:4] in code_groups:
            code_list = code_groups[code.code[:4]]
            code_list.append(code)
        else:
            code_groups[code.code[:4]] = [code]

    groups = []
    for setting in settings:
        group_dict = dict()
        group_dict['discount_code_setting'] = setting
        group_dict['code'] = code_groups[setting.first_4_digits]
        group_dict['discount_price'] = sum([code.carted_product_item.price for code in code_groups[setting.first_4_digits]])
        groups.append(group_dict)
    return groups


def confirm_coupon_status(request, codes, available_fanclub_discount_code_settings):
    if not available_fanclub_discount_code_settings:
        return None

    # イーグルスクーポンの状態確認
    comm = get_communicator(request, 'eagles')
    fc_member_id = request.altair_auth_info['auth_identifier']

    # ファンクラブのもので先頭4桁が合致するものだけ実施
    coupons = []
    for code in codes:
        for setting in available_fanclub_discount_code_settings:
            if code['code'][:4] == setting.first_4_digits:
                coupons.append({'coupon_cd': code['code']})

    if not coupons:
        return None

    data = {
        'usage_type': '1010',
        'fc_member_id': fc_member_id,
        'coupons': coupons
    }
    result = comm.confirm_coupon_status(data)

    if not result['status'] == u'OK' and result['usage_type'] == u'1010':
        return False

    return result

# # APIのテスト使用
# from ..discount_code.communicators.utils import get_communicator
# comm = get_communicator(self.request, 'eagles')
# fc_member_id = self.request.altair_auth_info['auth_identifier']
#
# # イーグルスクーポンの状態確認
# data = {
#     'usage_type': '1010',
#     'fc_member_id': fc_member_id,
#     'coupons': [{'coupon_cd': code['code']} for code in codes]
# }
# result = comm.confirm_coupon_status(data)
#
# # イーグルスクーポンの使用
# data = {
#     'usage_type': '1010',
#     'fc_member_id': fc_member_id,
#     'coupons': [{'coupon_cd': code['code']} for code in codes]
# }
# result2 = comm.use_coupon(data)
#
# # イーグルスクーポンを未使用に戻す（キャンセル）
# data = {
#     'usage_type': '1010',
#     'coupons': [{'coupon_cd': code['code']} for code in codes]
# }
# result3 = comm.cancel_used_coupon(data)
