# -*- coding: utf-8 -*-

from datetime import datetime
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from .models import DiscountCodeSetting, DiscountCodeCode, UsedDiscountCodeCart, UsedDiscountCodeOrder
from altair.app.ticketing.orders.exceptions import OrderCancellationError
from altair.app.ticketing.cart.exceptions import OwnDiscountCodeDuplicateError
from communicators.utils import get_communicator
from pyramid.i18n import TranslationString as _


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


def release_cart(cart):
    codes = get_used_discount_codes(cart)
    for code in codes:
        code.finished_at = datetime.now()
    return True


def check_used_discount_code(code, organizatoin):
    used_code = UsedDiscountCodeOrder.query.\
        filter(UsedDiscountCodeOrder.code==code).\
        filter(UsedDiscountCodeOrder.deleted_at==None).\
        filter(UsedDiscountCodeOrder.canceled_at==None).\
        filter(UsedDiscountCodeOrder.refunded_at==None). \
        order_by(UsedDiscountCodeOrder.created_at.desc()).\
        first()

    if used_code:
        return used_code

    # バックエンドで使用済みにされた場合を考慮
    own_used_code = None
    try:
        own_used_code = DiscountCodeCode.query.\
        filter(DiscountCodeCode.code==code).\
        filter(DiscountCodeCode.used_at!=None).\
        filter(DiscountCodeCode.organization_id==organizatoin.id).\
        one()
    except MultipleResultsFound, e:
        raise OwnDiscountCodeDuplicateError()
    except NoResultFound, e:
        pass

    return own_used_code


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


def temporarily_save_discount_code(codes, organization):
    # carted_product_itemのIDと、使用したコードを保存する
    for code_dict in codes:
        code = code_dict['form'].code.data
        if code:
            use_discount_code = UsedDiscountCodeCart()
            use_discount_code.code = code
            use_discount_code.carted_product_item_id = code_dict['carted_product_item'].id
            own_code = DiscountCodeCode.query.filter(
                DiscountCodeCode.code == code_dict['code'],
                DiscountCodeCode.organization_id == organization.id,
                DiscountCodeCode.used_at.is_(None)
            ).first()
            if own_code:
                # 自社コードの場合のみ存在
                use_discount_code.discount_code_id = own_code.id
            use_discount_code.add()
    return True


def save_discount_code(carted_product_item, ordered_product_item):
    # 対象のCartedProductItemにクーポンが使用されていたら、UsedDiscountCodeOrderにデータを記録する
    used_discount_code_carts = carted_product_item.used_discount_codes
    now = datetime.now()

    for index, used_discount_code_cart in enumerate(used_discount_code_carts):
        use_discount_code_order = UsedDiscountCodeOrder()
        use_discount_code_order.code = used_discount_code_cart.code
        use_discount_code_order.ordered_product_item = ordered_product_item
        use_discount_code_order.ordered_product_item_token = ordered_product_item.tokens[index]

        # クーポン・割引コードテーブルに使用日時を記載
        if used_discount_code_cart.discount_code_id:
            use_discount_code_order.discount_code_id = used_discount_code_cart.discount_code_id
            available_code = DiscountCodeCode.query.filter_by(id=used_discount_code_cart.discount_code_id).first()
            available_code.used_at = now
            available_code.save()
        use_discount_code_order.add()

        # UsedDiscountCodeCartテーブルにカート処理日時を記載
        used_discount_code_cart.finished_at = now
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


def confirm_discount_code_status(request, codes, available_fanclub_discount_code_settings):
    if not available_fanclub_discount_code_settings:
        return None

    # イーグルスクーポンの状態確認
    comm = get_communicator(request, 'eagles')
    fc_member_id = request.altair_auth_info['authz_identifier']

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
    result = comm.confirm_discount_code_status(data)

    if not result['status'] == u'OK' and result['usage_type'] == u'1010':
        return False

    return result


def use_discount_codes(request, codes, available_fanclub_discount_code_settings):
    if not available_fanclub_discount_code_settings:
        return None

    # イーグルスクーポンの使用
    comm = get_communicator(request, 'eagles')
    fc_member_id = request.altair_auth_info['authz_identifier']

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
    result = comm.use_discount_code(data)

    if not result['status'] == u'OK' and result['usage_type'] == u'1010':
        return False

    return result


def cancel_used_discount_codes(request, order, now=None):
    """
    使用された割引コードを未使用に戻す。（自社コード、スポーツサービス開発コード）
    :param request: リクエスト
    :param order: キャンセル対象
    :param now: キャンセル時刻
    """
    now = now or datetime.now()
    own_settings = order.cart.available_own_discount_code_settings
    fanclub_settings = order.cart.available_fanclub_discount_code_settings
    api_request_coupons = []

    try:
        for code in order.used_discount_codes:
            # UsedDiscountCodeOrderの更新
            if order.status == 'refunded':
                code.refunded_at = now
            elif order.status == 'canceled':
                code.canceled_at = now
            else:
                raise SystemError('order status must be refunded or canceled.')
            code.save()

            first_4_degits = code.code[:4]

            # 自社発行の割引コード
            # DiscountCodeテーブルのused_atをNullに更新する
            for o_setting in own_settings:
                if first_4_degits == o_setting.first_4_digits:
                    code.discount_code.used_at = None
                    code.discount_code.save()

            # スポーツサービス開発発行の割引コード
            for f_setting in fanclub_settings:
                if first_4_degits == f_setting.first_4_digits:
                    api_request_coupons.append({'coupon_cd': code.code})

        # スポーツサービス開発に割引コードを未使用に戻すAPIリクエストを送る
        if not api_request_coupons:
            return None

        comm = get_communicator(request, 'eagles')
        data = {
            'usage_type': '1010',
            'coupons': api_request_coupons
        }

        result = comm.cancel_used_discount_code(data)
        for coupon in result['coupons']:
            if coupon['reason_cd'][:2] != '10':
                raise SystemError('inappropriate response returned.')

    except:
        import sys
        exc_info = sys.exc_info()
        raise OrderCancellationError(
            order.order_no,
            _(u'used discount code can not be canceled.').interpolate(),
            nested_exc_info=exc_info
        )
