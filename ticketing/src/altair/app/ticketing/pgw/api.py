# -*- coding: utf-8 -*-
import logging
import altair.pgw.api as pgw_api
from altair.pgw.api import PGWRequest
from .models import PGWOrderStatus, PaymentStatusEnum
from datetime import datetime

logger = logging.getLogger(__name__)


def authorize(request, payment_id, email, session=None):
    """
    PGWのAuthorizeAPIをコールします
    :param request: リクエスト
    :param payment_id: 予約番号(cart:order_no, lots:entry_no)
    :param email: Eメールアドレス
    :param session: DBセッション
    """
    pgw_request = create_settlement_request(payment_id=payment_id, email=email)

    # PGWのAuthorizeAPIをコールします
    pgw_api_response = pgw_api.authorize(request=request, pgw_request=pgw_request)

    # PGWの処理が成功したのか失敗したのかを確認する
    confirm_pgw_api_result(payment_id=payment_id, api_type='authorize', pgw_api_response=pgw_api_response)

    # PGWOrderStatusテーブルの更新
    pgw_order_status = get_pgw_order_status(payment_id=payment_id, session=session)
    pgw_order_status.authed_at = datetime.strptime(pgw_api_response.get('transactionTime'), '%Y-%m-%d %H:%M:%S')
    pgw_order_status.payment_status = int(PaymentStatusEnum.auth)
    PGWOrderStatus.update_pgw_order_status(pgw_order_status=pgw_order_status, session=session)

    # カードトークン関連情報テーブルの登録


def capture(request, payment_id, session=None):
    """
    PGWのCaptureAPIをコールします
    :param request: リクエスト
    :param payment_id: 予約番号(cart:order_no, lots:entry_no)
    :param session: DBセッション
    """
    # PGWOrderStatusレコード取得
    pgw_order_status = get_pgw_order_status(payment_id=payment_id, session=session)
    capture_amount = pgw_order_status.gross_amount

    # PGWのCaptureAPIをコールします
    pgw_api_response = pgw_api.capture(request=request, payment_id=payment_id, capture_amount=capture_amount)

    # PGWの処理が成功したのか失敗したのかを確認する
    confirm_pgw_api_result(payment_id=payment_id, api_type='capture', pgw_api_response=pgw_api_response)

    # PGWOrderStatusテーブルの更新
    pgw_order_status = get_pgw_order_status(payment_id=payment_id, session=session)
    pgw_order_status.captured_at = datetime.strptime(pgw_api_response.get('transactionTime'), '%Y-%m-%d %H:%M:%S')
    pgw_order_status.payment_status = int(PaymentStatusEnum.capture)
    PGWOrderStatus.update_pgw_order_status(pgw_order_status=pgw_order_status, session=session)


def authorize_and_capture(request, payment_id, email, session=None):
    """
    PGWのAuthorizeAndCaptureAPIをコールします
    :param request: リクエスト
    :param payment_id: 予約番号(cart:order_no, lots:entry_no)
    :param email: Eメールアドレス
    :param session: DBセッション
    """
    pgw_request = create_settlement_request(payment_id=payment_id, email=email)

    # PGWのAuthorizeAPIをコールします
    pgw_api_response = pgw_api.authorize_and_capture(request=request, pgw_request=pgw_request)

    # PGWの処理が成功したのか失敗したのかを確認する
    confirm_pgw_api_result(payment_id=payment_id, api_type='authorize_and_capture', pgw_api_response=pgw_api_response)

    # PGWOrderStatusテーブルの更新
    pgw_order_status = get_pgw_order_status(payment_id=payment_id, session=session)
    pgw_order_status.authed_at = datetime.strptime(pgw_api_response.get('transactionTime'), '%Y-%m-%d %H:%M:%S')
    pgw_order_status.captured_at = datetime.strptime(pgw_api_response.get('transactionTime'), '%Y-%m-%d %H:%M:%S')
    pgw_order_status.payment_status = int(PaymentStatusEnum.capture)
    PGWOrderStatus.update_pgw_order_status(pgw_order_status=pgw_order_status, session=session)

    # カードトークン関連情報テーブルの登録


def find(request, payment_ids, search_type=None):
    """
    PGWのFindAPIをコールします
    :param request: リクエスト
    :param payment_ids: 予約番号リスト(cart:order_no, lots:entry_no)
    :param search_type: 検索タイプ
    :return: PGWからのAPIレスポンス
    """
    # PGWのFindAPIをコールします
    pgw_api_response = pgw_api.find(request=request, payment_ids=payment_ids, search_type=search_type)

    # PGWの処理が成功したのか失敗したのかを確認する
    confirm_pgw_api_result(payment_id=payment_ids, api_type='find', pgw_api_response=pgw_api_response)

    return pgw_api_response


def cancel_or_refund(request, payment_id, session=None):
    """
    PGWのCancelOrRefundAPIをコールします
    :param request: リクエスト
    :param payment_id: 予約番号(cart:order_no, lots:entry_no)
    :param session: DBセッション
    """
    # PGWのCancelOrRefundAPIをコールします
    pgw_api_response = pgw_api.cancel_or_refund(request=request, payment_id=payment_id)

    # PGWの処理が成功したのか失敗したのかを確認する
    confirm_pgw_api_result(payment_id=payment_id, api_type='cancel_or_refund', pgw_api_response=pgw_api_response)

    # PGWOrderStatusテーブルの更新
    pgw_order_status = get_pgw_order_status(payment_id=payment_id, session=session)
    pgw_order_status.canceled_at = datetime.strptime(pgw_api_response.get('transactionTime'), '%Y-%m-%d %H:%M:%S')
    if pgw_order_status.payment_status == PaymentStatusEnum.capture:
        pgw_order_status.refunded_at = datetime.strptime(pgw_api_response.get('transactionTime'), '%Y-%m-%d %H:%M:%S')
        pgw_order_status.payment_status = int(PaymentStatusEnum.refund)
    else:
        pgw_order_status.payment_status = int(PaymentStatusEnum.cancel)
    PGWOrderStatus.update_pgw_order_status(pgw_order_status=pgw_order_status, session=session)


def modify(request, payment_id, modified_amount, session=None):
    """
    PGWのModifyAPIをコールします
    :param request: リクエスト
    :param payment_id: 予約番号(cart:order_no, lots:entry_no)
    :param modified_amount: 変更後の決済金額
    :param session: DBセッション
    """
    # PGWのModifyAPIをコールします
    pgw_api_response = pgw_api.modify(request=request, payment_id=payment_id, modified_amount=modified_amount)

    # PGWの処理が成功したのか失敗したのかを確認する
    confirm_pgw_api_result(payment_id=payment_id, api_type='modify', pgw_api_response=pgw_api_response)

    # PGWOrderStatusテーブルの更新
    pgw_order_status = get_pgw_order_status(payment_id=payment_id, session=session)
    pgw_order_status.gross_amount = modified_amount
    PGWOrderStatus.update_pgw_order_status(pgw_order_status=pgw_order_status, session=session)


def three_d_secure_enrollment_check(request, sub_service_id, payment_id,
                                    callback_url, amount, card_token, session=None):
    """
    PGWの3DSecureEnrollmentCheckAPIをコールします
    :param request: リクエスト
    :param sub_service_id: 店舗ID
    :param payment_id: 予約番号(cart:order_no, lots:entry_no)
    :param callback_url: コールバックURL
    :param amount: 決済予定金額
    :param card_token: カードトークン
    :param session: DBセッション
    :return: PGWからのAPIレスポンス
    """
    # 3DSecure認証用ID生成
    enrollment_id = '{}_E'.format(payment_id)

    # PGWの3DSecureEnrollmentCheckAPIをコールします
    pgw_api_response = pgw_api.three_d_secure_enrollment_check(
        request=request,
        sub_service_id=sub_service_id,
        enrollment_id=enrollment_id,
        callback_url=callback_url,
        amount=amount,
        card_token=card_token)

    # PGWの処理が成功したのか失敗したのかを確認する
    confirm_pgw_api_result(payment_id=payment_id, api_type='three_d_secure_enrollment_check',
                           pgw_api_response=pgw_api_response)

    # PGWOrderStatusテーブルの更新
    pgw_order_status = get_pgw_order_status(payment_id=payment_id, session=session)
    pgw_order_status.enrolled_at = datetime.strptime(pgw_api_response.get('transactionTime'), '%Y-%m-%d %H:%M:%S')
    PGWOrderStatus.update_pgw_order_status(pgw_order_status=pgw_order_status, session=session)

    # 3Dセキュアのレスポンステーブル登録

    return pgw_api_response


def create_settlement_request(payment_id, email):
    """
    AuthorizeAPI, AuthorizeAndCaptureAPI用リクエストオブジェクトを作成します
    :param payment_id: 予約番号(cart:order_no, lots:entry_no)
    :param email: Eメールアドレス
    :return: pgw_request: PGW決済リクエストオブジェクト(PGWRequest)
    """
    pgw_request = PGWRequest(payment_id)
    pgw_request.email = email

    # PGWOrderStatusの対象レコード取得
    pgw_order_status = get_pgw_order_status(payment_id)
    pgw_request.sub_service_id = pgw_order_status.sub_service_id
    pgw_request.gross_amount = pgw_order_status.gross_amount
    pgw_request.card_token = pgw_order_status.card_token
    pgw_request.cvv_token = pgw_order_status.cvv_token

    return pgw_request


def initialize_pgw_order_status(sub_service_id, payment_id, card_token, cvv_token, gross_amount, session=None):
    """
    PGWOrderStatusのレコード初期登録を行う
    :param sub_service_id: 店舗ID
    :param payment_id: 予約番号(cart:order_no, lots:entry_no)
    :param card_token: カードトークン
    :param cvv_token: セキュリティコードトークン
    :param gross_amount: 決済総額
    :param session: DBセッション
    :return: PGWOrderStatusの主キー(id)
    """
    pgw_order_status = PGWOrderStatus(
        pgw_sub_service_id=sub_service_id,
        payment_id=payment_id,
        card_token=card_token,
        cvv_token=cvv_token,
        payment_status=int(PaymentStatusEnum.initialized),
        gross_amount=gross_amount
    )

    # PGWOrderStatusのレコードをinsert
    return PGWOrderStatus.insert_pgw_order_status(pgw_order_status, session=session)


def get_pgw_status(payment_id):
    """
    PGWOrderStatusのステータスを返します
    :param payment_id: 予約番号(cart:order_no, lots:entry_no)
    :return: payment_status
    """
    # PGWOrderStatusのステータスを返す
    pgw_order_status = get_pgw_order_status(payment_id)
    return pgw_order_status.payment_status


def get_pgw_order_status(payment_id, session=None):
    """
    PGWOrderStatusテーブルのレコードを取得します。
    :param payment_id: 予約番号(cart:order_no, lots:entry_no)
    :param session: DBセッション
    :return: PGWOrderStatusレコード
    """
    # PGWOrderStatusのステータスを返す
    pgw_order_status = PGWOrderStatus.get_pgw_order_status(payment_id, session)
    return pgw_order_status


def confirm_pgw_api_result(payment_id, api_type, pgw_api_response):
    """
    PGW APIのリクエスト処理結果を確認します
    :param payment_id: 予約番号(cart:order_no, lots:entry_no)
    :param api_type: コールしたAPIの種類
    :param pgw_api_response: PGW APIのレスポンス
    """
    result_type = pgw_api_response.get(u'resultType')
    if result_type != u'success':
        # TODO: 例外処理は別途対応しますので暫定でraiseだけ行います。errorCode, errorMessageを持つような例外クラスを作成予定
        raise Exception(u'PGW request was failure. payment_id = {paymentId}, '
                        u'api_type = {apiType}, resultType = {resultType}'
                        .format(paymentId=payment_id, apiType=api_type, resultType=result_type))
