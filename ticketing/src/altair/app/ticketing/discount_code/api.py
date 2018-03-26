# -*- coding: utf-8 -*-

from datetime import datetime

from altair.app.ticketing.cart.exceptions import OwnDiscountCodeDuplicateError, NotAllowedBenefitUnitError, NotExistingOwnDiscountCodeError
from altair.app.ticketing.orders.exceptions import OrderCancellationError
from altair.sqlahelper import get_db_session
from communicators.utils import get_communicator
from pyramid.httpexceptions import HTTPFound
from pyramid.i18n import TranslationString as _
from sqlalchemy import func
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from .models import (
    DiscountCodeSetting,
    DiscountCodeCode,
    UsedDiscountCodeCart,
    UsedDiscountCodeOrder
)


def check_discount_code_functions_available(context, request):
    """
    管理画面のクーポン・割引コード関連機能が使用できる状態か判定
    :param context: Resourceオブジェクト
    :param request: requestは使用できていないが、使用場所がcustom_predicatesのために必要。
    :return: Boolean
    """
    # ログアウト状態
    if not context.user:
        return False

    # 組織設定でクーポン・割引コード設定がOFF
    if not context.user.organization.setting.enable_discount_code:
        return False

    # 割引コード設定のIDがGETで渡されている場合
    if 'setting_id' in request.matchdict:
        setting_id = request.matchdict['setting_id']
        try:
            # 成功時はcontextに設定情報を渡しておく
            context.setting = context.session.query(DiscountCodeSetting).filter_by(
                organization_id=context.user.organization_id,
                id=setting_id
            ).one()
        except NoResultFound:
            return False
        except MultipleResultsFound:
            request.session.flash(u'登録データに不整合が発生しています。開発部に調査を依頼してください。')
            raise HTTPFound(location=request.route_path('discount_code.settings_index'))

    return True


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


def is_exist_duplicate_codes(code, code_str_list):
    """
    入力されたコードの中で重複があればTrueを返す
    :param code: 割引コード文字列
    :param code_str_list: 入力された全割引コード文字列のリスト
    :return:
    """
    n = sum(code == x for x in code_str_list)
    return n > 1


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
                for used in used_codes:
                    discount_amount = discount_amount + used.applied_amount
    return discount_amount


def get_discount_price(ordered_product_item_token):
    price = 0
    used_codes = ordered_product_item_token.used_discount_codes
    if used_codes:
        for used in used_codes:
            price = price + used.applied_amount
    return price


def get_discount_price_from_carted_product(request, cp):
    """
    :param request: リクエストオブジェクト
    :param cp: CartedProductオブジェクト
    :return: discount_price: 商品ごとの割引金額。
    """
    from altair.app.ticketing.cart.models import CartedProductItem
    result = get_db_session(request, 'slave').query(
        func.sum(UsedDiscountCodeCart.applied_amount).label('discount_price')
    ).join(
        CartedProductItem
    ).filter(
        CartedProductItem.carted_product_id == cp.id
    ).one()

    return result.discount_price if result.discount_price else 0


def get_discount_price_from_ordered_product(op):
    """
    :param op: OrderedProductオブジェクト
    :return: discount_price: 商品ごとの割引金額。
    """
    from altair.app.ticketing.orders.models import OrderedProductItem
    from pyramid.threadlocal import get_current_request
    result = get_db_session(get_current_request(), 'slave').query(
        func.sum(UsedDiscountCodeOrder.applied_amount).label('discount_price')
    ).join(
        OrderedProductItem
    ).filter(
        OrderedProductItem.ordered_product_id == op.id
    ).one()

    return result.discount_price if result.discount_price else 0


def enable_discount_code(organization):
    return organization.setting.enable_discount_code


def calc_applied_amount(code_dict):
    """
    割引コードによる適用金額（値引き額）を計算する。
    :param code_dict: cartのviewで使用されたcreate_codes（）の結果
    :return: 計算された金額
    """
    setting = code_dict['discount_code_setting']
    item = code_dict['carted_product_item']
    if setting.benefit_unit == u'%':
        amount = float(item.price) * (setting.benefit_amount / 100.00)
    elif setting.benefit_unit == u'yen':
        amount = item.price - setting.benefit_amount
    else:
        raise NotAllowedBenefitUnitError()

    return int(amount)


def temporarily_save_discount_code(code_dict_list, organization, session):
    # carted_product_itemのIDと、使用したコードを保存する
    for code_dict in code_dict_list:
        code = code_dict['form'].code.data
        if code:
            use_discount_code = UsedDiscountCodeCart()
            use_discount_code.code = code
            use_discount_code.carted_product_item_id = code_dict['carted_product_item'].id

            # 自社コードの利用時
            if code_dict['discount_code_setting'].issued_by == u'own':
                own_code = session.query(DiscountCodeCode.id).filter(
                    DiscountCodeCode.code == code_dict['code'],
                    DiscountCodeCode.organization_id == organization.id,
                    DiscountCodeCode.used_at.is_(None)
                ).first()
                if own_code:
                    use_discount_code.discount_code_id = own_code.id
                else:
                    raise NotExistingOwnDiscountCodeError()

            use_discount_code.applied_amount = calc_applied_amount(code_dict)
            use_discount_code.discount_code_setting_id = code_dict['discount_code_setting'].id
            use_discount_code.benefit_amount = code_dict['discount_code_setting'].benefit_amount
            use_discount_code.benefit_unit = code_dict['discount_code_setting'].benefit_unit

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
        use_discount_code_order.discount_code_setting_id = used_discount_code_cart.discount_code_setting_id
        use_discount_code_order.applied_amount = used_discount_code_cart.applied_amount
        use_discount_code_order.benefit_amount = used_discount_code_cart.benefit_amount
        use_discount_code_order.benefit_unit = used_discount_code_cart.benefit_unit

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


def get_discount_code_settings(codes):
    """
    使用された割引コード文字列から割引コード設定を取得する
    使用後のコード設定を取得することが目的なので、有効フラグや有効期間などは無視する。
    :param codes: 割引コード文字列のリスト
    :return setting_list: 割引コード設定のリスト
    """
    setting_list = []
    code_set = set(code.code[:4] for code in codes)

    for code in code_set:
        first_digit = code[:1]
        following_2to4_digits = code[1:4]
        setting = DiscountCodeSetting \
            .filter(DiscountCodeSetting.first_digit == first_digit) \
            .filter(DiscountCodeSetting.following_2to4_digits == following_2to4_digits) \
            .one()
        setting_list.append(setting)

    return setting_list


def used_discount_code_groups(cart_or_order):
    """
    使用された割引コードを頭4桁でグループ化し、その合計金額や設定内容をまとめている
    :param cart_or_order: OrderやCartオブジェクト
    :return: 頭4桁の入力文字でグループ化されたdict
    """
    groups = []

    codes = get_used_discount_codes(cart_or_order)
    settings = get_discount_code_settings(codes)
    if not settings:
        return groups

    code_groups = {}
    for code in codes:
        if code.code[:4] in code_groups:
            code_list = code_groups[code.code[:4]]
            code_list.append(code)
        else:
            code_groups[code.code[:4]] = [code]

    for setting in settings:
        group_dict = dict()
        group_dict['discount_code_setting'] = setting
        group_dict['code'] = code_groups[setting.first_4_digits]
        group_dict['discount_price'] = 0
        for code in code_groups[setting.first_4_digits]:
            if code.applied_amount:
                group_dict['discount_price'] = group_dict['discount_price'] + code.applied_amount

        groups.append(group_dict)

    return groups


def confirm_discount_code_status(request, codes):
    # イーグルスクーポンの状態確認
    comm = get_communicator(request, 'disc_code_eagles')
    fc_member_id = request.altair_auth_info['authz_identifier']

    # ファンクラブのもので先頭4桁が合致するものだけ実施
    coupons = []
    for code in codes:
        coupons.append({'coupon_cd': code['code']})

    data = {
        'usage_type': '1010',
        'fc_member_id': fc_member_id,
        'coupons': coupons
    }
    result = comm.confirm_discount_code_status_api(data)

    return result


def use_discount_codes(request, codes, available_fanclub_discount_code_settings):
    if not available_fanclub_discount_code_settings:
        return None

    # イーグルスクーポンの使用
    comm = get_communicator(request, 'disc_code_eagles')
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
    result = comm.use_discount_code_api(data)

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

            first_4_digits = code.code[:4]
            code_setting = order.cart.performance.find_available_target_settings(first_4_digits=first_4_digits,
                                                                                 refer_all=True,
                                                                                 now=now)
            if code_setting.issued_by == u'own':
                code.discount_code.used_at = None
            elif code_setting.issued_by == u'sports_service':
                api_request_coupons.append({'coupon_cd': code.code})
            else:
                raise SystemError('code {} is not issued properly'.format(code.code))

        # スポーツサービス開発に割引コードを未使用に戻すAPIリクエストを送る
        if not api_request_coupons:
            return None

        comm = get_communicator(request, 'disc_code_eagles')
        data = {
            'usage_type': '1010',
            'coupons': api_request_coupons
        }

        result = comm.cancel_used_discount_code_api(data)
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


def validate_to_delete_all_codes(setting, session):
    err = []
    try:
        if DiscountCodeSetting.is_valid_checked(setting.id, session):
            err.append(u'設定の有効フラグにチェックが入っている')
    except NoResultFound:
        err.append(u'削除対象の割引設定（ID: {} {}）が存在しません。'.format(setting.id, setting.name))
    except MultipleResultsFound:
        err.append(u'複数の割引設定（ID: {} {}）が検出されました。開発部に調査を依頼してください。'.format(setting.id, setting.name))

    valid_order_cnt = UsedDiscountCodeOrder.count_exists_valid_order(setting.first_4_digits, session)
    if valid_order_cnt:
        err.append(u'コードが使用された有効な予約が{}件ある'.format(valid_order_cnt))

    return err
