# -*- coding: utf-8 -*-

"""スポーツサービス開発発行の割引コードを操作するメソッド群"""

from datetime import datetime

from altair.app.ticketing.orders.exceptions import OrderCancellationError
from communicators.utils import get_communicator
from pyramid.i18n import TranslationString as _


def confirm_discount_code_status(request, entries, fc_member_id):
    """
    APIを叩いてスポーツサービス開発管理の割引コードの使用可否確認
    :param Request request: リクエスト
    :param list entries: 割引コード入力フォーム（FormField）情報のリスト
    :param unicode fc_member_id: イーグルスファンクラブ会員ID
    :return dict result: APIレスポンス
    """
    comm = get_communicator(request, 'disc_code_eagles')
    coupons = [{'coupon_cd': entry.data['code']} for entry in entries]

    data = {
        'usage_type': '1010',
        'fc_member_id': fc_member_id,
        'coupons': coupons
    }
    result = comm.confirm_discount_code_status_api(data)

    return result


def use_discount_codes(request, codes, fc_member_id):
    """スポーツサービス開発発行による割引コードの使用"""
    coupons = [{'coupon_cd': c} for c in codes]
    data = {
        'usage_type': '1010',
        'fc_member_id': fc_member_id,
        'coupons': coupons
    }

    comm = get_communicator(request, 'disc_code_eagles')
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

            code_setting = code.discount_code_setting
            if not code_setting:
                raise SystemError(
                    'could not find discount code setting for {}. was the related data deleted?'.format(code.code)
                )

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
                raise SystemError('inappropriate reason_cd {} returned.'.format(coupon['reason_cd']))

    except:
        import sys
        exc_info = sys.exc_info()
        raise OrderCancellationError(
            order.order_no,
            _(u'used discount code can not be canceled.').interpolate(),
            nested_exc_info=exc_info
        )
