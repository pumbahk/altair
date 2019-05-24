# -*- coding: utf-8 -*-
import altair.pgw.api as pgw_api


class PGWPayment(object):
    def __init__(self, request, sub_service_id, payment_id, gross_amount,
                 card_amount, card_token, cvv_token, email, three_d_secure_authentication_result=None):
        self.request = request
        self.sub_service_id = sub_service_id
        self.payment_id = payment_id
        self.gross_amount = gross_amount
        self.card_amount = card_amount
        self.card_token = card_token
        self.cvv_token = cvv_token
        self.email = email
        self.three_d_secure_authentication_result = three_d_secure_authentication_result


def pgw_authorize(request, pgw_payment):
    # PGWのAuthorizeAPIをコールします
    result = pgw_api.authorize(request, pgw_payment)

    # PGW連携テーブルの更新
    # カードトークン関連情報テーブルの登録

    return result


def pgw_capture(request, payment_id, capture_amount):
    # PGWのCaptureAPIをコールします
    result = pgw_api.capture(request, payment_id, capture_amount)

    # PGW連携テーブルの更新

    return result


def pgw_authorize_and_capture(request, pgw_payment):
    # PGWのAuthorizeAndCaptureAPIをコールします
    result = pgw_api.authorize_and_capture(request, pgw_payment)

    # PGW連携テーブルの更新
    # カードトークン関連情報テーブルの登録

    return result


def pgw_find(request, payment_ids, search_type=None):
    # PGWのFindAPIをコールします
    result = pgw_api.find(request, payment_ids, search_type)

    return result


def pgw_cancel_or_refund(request, payment_id):
    # PGWのCancelOrRefundAPIをコールします
    result = pgw_api.cancel_or_refund(request, payment_id)

    # PGW連携テーブルの更新

    return result


def pgw_modify(request, payment_id, modified_amount):
    # PGWのModifyAPIをコールします
    result = pgw_api.modify(request, payment_id, modified_amount)

    # PGW連携テーブルの更新

    return result


def pgw_three_d_secure_enrollment_check(request, sub_service_id, enrollment_id, callback_url, amount, card_token):
    # PGWの3DSecureEnrollmentCheckAPIをコールします
    result = pgw_api.three_d_secure_enrollment_check(
        request,
        sub_service_id,
        enrollment_id,
        callback_url,
        amount,
        card_token)

    # PGW連携テーブルの登録
    # 3Dセキュアのレスポンステーブル登録

    return result


def get_pgw_status(request, payment_id):
    # PGWOrderStatusのステータスを返す
    # 現状は暫定でPGWのFindAPIのステータスを返すようにします
    result = pgw_api.find(request, payment_id)

    return result['details'][0]['paymentStatusType']
