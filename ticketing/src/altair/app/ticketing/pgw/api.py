# -*- coding: utf-8 -*-
import altair.pgw.api as pgw_api
from altair.pgw.api import PGWRequest


"""
DB接続までできるようにした段階で下記のクラスは削除します
"""
class PGWPaymentRequest(object):
    """
    authorize, authorize_and_capture呼び出し時に生成するリクエストオブジェクトです
    """
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


# def authorize(request, payment_id, email):
def authorize(request, pgw_payment_request):
    """
    PGWのAuthorizeAPIをコールします
    :param request: リクエスト
    :param pgw_payment_request: PGW決済リクエストオブジェクト(ticketing.src.altair.app.ticketing.pgw.api.PGWPayment)
    :return: PGWからのAPIレスポンス
    """
    # pgw_request = create_settlement_request(PGWRequest(payment_id), email)

    # PGWのAuthorizeAPIをコールします
    # result = pgw_api.authorize(request, pgw_request)
    result = pgw_api.authorize(request, pgw_payment_request)

    # PGW連携テーブルの更新
    # カードトークン関連情報テーブルの登録

    return result


def capture(request, payment_id, capture_amount):
    """
    PGWのCaptureAPIをコールします
    :param request: リクエスト
    :param payment_id: 予約番号(cart:order_no, lots:entry_no)
    :param capture_amount: キャプチャする決済金額
    :return: PGWからのAPIレスポンス
    """
    # PGWのCaptureAPIをコールします
    result = pgw_api.capture(request, payment_id, capture_amount)

    # PGW連携テーブルの更新

    return result


# def authorize_and_capture(request, payment_id, email):
def authorize_and_capture(request, pgw_payment_request):
    """
    PGWのAuthorizeAndCaptureAPIをコールします
    :param request: リクエスト
    :param pgw_payment_request: PGW決済リクエストオブジェクト(ticketing.src.altair.app.ticketing.pgw.api.PGWPayment)
    :return: PGWからのAPIレスポンス
    """
    # pgw_request = PGWRequest(payment_id)
    # pgw_request.create_settlement_request(email)

    # PGWのAuthorizeAndCaptureAPIをコールします
    # result = pgw_api.authorize_and_capture(request, pgw_request)
    result = pgw_api.authorize_and_capture(request, pgw_payment_request)

    # PGW連携テーブルの更新
    # カードトークン関連情報テーブルの登録

    return result


def find(request, payment_ids, search_type=None):
    """
    PGWのFindAPIをコールします
    :param request: リクエスト
    :param payment_ids: 予約番号リスト(cart:order_no, lots:entry_no)
    :param search_type: 検索タイプ
    :return: PGWからのAPIレスポンス
    """
    # PGWのFindAPIをコールします
    result = pgw_api.find(request, payment_ids, search_type)

    return result


def cancel_or_refund(request, payment_id):
    """
    PGWのCancelOrRefundAPIをコールします
    :param request: リクエスト
    :param payment_id: 予約番号(cart:order_no, lots:entry_no)
    :return: PGWからのAPIレスポンス
    """
    # PGWのCancelOrRefundAPIをコールします
    result = pgw_api.cancel_or_refund(request, payment_id)

    # PGW連携テーブルの更新

    return result


def modify(request, payment_id, modified_amount):
    """
    PGWのModifyAPIをコールします
    :param request: リクエスト
    :param payment_id: 予約番号(cart:order_no, lots:entry_no)
    :param modified_amount: 変更後の決済金額
    :return: PGWからのAPIレスポンス
    """
    # PGWのModifyAPIをコールします
    result = pgw_api.modify(request, payment_id, modified_amount)

    # PGW連携テーブルの更新

    return result


def three_d_secure_enrollment_check(request, sub_service_id, enrollment_id, callback_url, amount, card_token):
    """
    PGWの3DSecureEnrollmentCheckAPIをコールします
    :param request: リクエスト
    :param sub_service_id: 店舗ID
    :param enrollment_id: 3DSecure認証用ID(予約番号)(cart:order_no, lots:entry_no)
    :param callback_url: コールバックURL
    :param amount: 決済予定金額
    :param card_token: カードトークン
    :return: PGWからのAPIレスポンス
    """
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
    """
    PGWOrderStatusのステータスを返します
    :param request: リクエスト
    :param payment_id: 予約番号(cart:order_no, lots:entry_no)
    :return:
    """
    # PGWOrderStatusのステータスを返す
    # 現状は暫定でPGWのFindAPIのステータスを返すようにします
    result = pgw_api.find(request, payment_id)

    # success以外の場合はステータスをinitializedで返す
    if result['resultType'] != u'success':
        return {
            u'details': [
                {
                    u'paymentStatusType': u'initialized',
                    u'grossAmount': 0
                }
            ]
        }
    return result


def create_settlement_request(pgw_request, email):
    """
    AuthorizeAPI, AuthorizeAndCaptureAPI用リクエストオブジェクトを作成します
    :param pgw_request: PGW決済リクエストオブジェクト(PGWRequest)
    :param email: Eメールアドレス
    :return:
    """
    pgw_request.email = email
    # PGWOrderStatusの対象レコード取得
    """
    pgw_request.sub_service_id = 
    pgw_request.gross_amount = 
    pgw_request.card_token = 
    pgw_request.cvv_token =
    """

    return pgw_request
