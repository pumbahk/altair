# -*- coding: utf-8 -*-
import logging
import altair.pgw.api as pgw_api
from .models import _session
from altair.pgw.api import PGWRequest
from .models import PGWOrderStatus, PaymentStatusEnum
from datetime import datetime
from pytz import timezone

logger = logging.getLogger(__name__)


def authorize(request, payment_id, email, session=None):
    """
    PGWのAuthorizeAPIをコールします
    :param request: リクエスト
    :param payment_id: 予約番号(cart:order_no, lots:entry_no)
    :param email: Eメールアドレス
    :param session: DBセッション
    """
    if session is None:
        session = _session
    pgw_order_status = get_pgw_order_status(payment_id=payment_id, session=session, for_update=True)
    pgw_request = create_settlement_request(payment_id=payment_id, pgw_order_status=pgw_order_status, email=email)

    # PGWのAuthorizeAPIをコールします
    pgw_api_response = pgw_api.authorize(request=request, pgw_request=pgw_request)

    # PGWの処理が成功したのか失敗したのかを確認する
    _confirm_pgw_api_result(payment_id=payment_id, api_type='authorize', pgw_api_response=pgw_api_response)

    # PGWOrderStatusテーブルの更新
    pgw_order_status.authed_at = _convert_to_jst_timezone(pgw_api_response.get('transactionTime'))
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
    if session is None:
        session = _session
    # PGWOrderStatusレコード取得
    pgw_order_status = get_pgw_order_status(payment_id=payment_id, session=session, for_update=True)
    capture_amount = pgw_order_status.gross_amount

    # PGWのCaptureAPIをコールします
    pgw_api_response = pgw_api.capture(request=request, payment_id=payment_id, capture_amount=capture_amount)

    # PGWの処理が成功したのか失敗したのかを確認する
    _confirm_pgw_api_result(payment_id=payment_id, api_type='capture', pgw_api_response=pgw_api_response)

    # PGWOrderStatusテーブルの更新
    pgw_order_status.captured_at = _convert_to_jst_timezone(pgw_api_response.get('transactionTime'))
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
    if session is None:
        session = _session
    pgw_order_status = get_pgw_order_status(payment_id=payment_id, session=session, for_update=True)
    pgw_request = create_settlement_request(payment_id=payment_id, pgw_order_status=pgw_order_status, email=email)

    # PGWのAuthorizeAPIをコールします
    pgw_api_response = pgw_api.authorize_and_capture(request=request, pgw_request=pgw_request)

    # PGWの処理が成功したのか失敗したのかを確認する
    _confirm_pgw_api_result(payment_id=payment_id, api_type='authorize_and_capture', pgw_api_response=pgw_api_response)

    # PGWOrderStatusテーブルの更新
    transaction_time = _convert_to_jst_timezone(pgw_api_response.get('transactionTime'))
    pgw_order_status.authed_at = transaction_time
    pgw_order_status.captured_at = transaction_time
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
    _confirm_pgw_api_result(payment_id=payment_ids, api_type='find', pgw_api_response=pgw_api_response)

    return pgw_api_response


def cancel_or_refund(request, payment_id, session=None):
    """
    PGWのCancelOrRefundAPIをコールします
    :param request: リクエスト
    :param payment_id: 予約番号(cart:order_no, lots:entry_no)
    :param session: DBセッション
    """
    if session is None:
        session = _session
    pgw_order_status = get_pgw_order_status(payment_id=payment_id, session=session, for_update=True)

    # PGWのCancelOrRefundAPIをコールします
    pgw_api_response = pgw_api.cancel_or_refund(request=request, payment_id=payment_id)

    # PGWの処理が成功したのか失敗したのかを確認する
    _confirm_pgw_api_result(payment_id=payment_id, api_type='cancel_or_refund', pgw_api_response=pgw_api_response)

    # PGWOrderStatusテーブルの更新
    transaction_time = _convert_to_jst_timezone(pgw_api_response.get('transactionTime'))
    pgw_order_status.canceled_at = transaction_time
    # キャプチャ済みの場合は払戻ステータスで更新
    if pgw_order_status.payment_status == int(PaymentStatusEnum.capture):
        pgw_order_status.refunded_at = transaction_time
        pgw_order_status.payment_status = int(PaymentStatusEnum.refund)
    # オーソリのキャンセルはキャンセルステータスで更新
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
    if session is None:
        session = _session
    pgw_order_status = get_pgw_order_status(payment_id=payment_id, session=session, for_update=True)

    # PGWのModifyAPIをコールします
    pgw_api_response = pgw_api.modify(request=request, payment_id=payment_id, modified_amount=modified_amount)

    # PGWの処理が成功したのか失敗したのかを確認する
    _confirm_pgw_api_result(payment_id=payment_id, api_type='modify', pgw_api_response=pgw_api_response)

    # PGWOrderStatusテーブルの更新
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
    _confirm_pgw_api_result(
        payment_id=payment_id, api_type='three_d_secure_enrollment_check', pgw_api_response=pgw_api_response
    )

    # PGWOrderStatusテーブルの更新
    pgw_order_status = get_pgw_order_status(payment_id=payment_id, session=session)
    pgw_order_status.enrolled_at = _convert_to_jst_timezone(pgw_api_response.get('transactionTime'))
    PGWOrderStatus.update_pgw_order_status(pgw_order_status=pgw_order_status, session=session)

    # 3Dセキュアのレスポンステーブル登録

    return pgw_api_response


def create_settlement_request(payment_id, pgw_order_status, email):
    """
    AuthorizeAPI, AuthorizeAndCaptureAPI用リクエストオブジェクトを作成します
    :param payment_id: 予約番号(cart:order_no, lots:entry_no)
    :param pgw_order_status: PGWOrderStatusテーブルのレコード
    :param email: Eメールアドレス
    :return: pgw_request: PGW決済リクエストオブジェクト(PGWRequest)
    """
    pgw_request = PGWRequest(payment_id)
    pgw_request.email = email

    # PGWOrderStatusの対象レコード取得
    pgw_request.sub_service_id = pgw_order_status.pgw_sub_service_id
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
    return PGWOrderStatus.insert_pgw_order_status(pgw_order_status=pgw_order_status, session=session)


def get_pgw_order_status(payment_id, session=None, for_update=False):
    """
    PGWOrderStatusテーブルのレコードを取得します。
    :param payment_id: 予約番号(cart:order_no, lots:entry_no)
    :param session: DBセッション
    :param for_update: 排他制御フラグ
    :return: PGWOrderStatusレコード
    """
    # PGWOrderStatusのステータスを返す
    pgw_order_status = PGWOrderStatus.get_pgw_order_status(
        payment_id=payment_id, session=session, for_update=for_update
    )
    return pgw_order_status


def _confirm_pgw_api_result(payment_id, api_type, pgw_api_response):
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


def _convert_to_jst_timezone(pgw_transaction_time):
    """
    PGWから返却されるtransaction_time(UTC)をJSTの時間に変換します
    :param pgw_transaction_time: PGW APIから返却されたtransactionTime
    :return: JSTに変換したtransaction_time
    """
    try:
        transaction_time = datetime.strptime(pgw_transaction_time, '%Y-%m-%d %H:%M:%S.%f')
        jst_transaction_time = timezone('UTC').localize(transaction_time).astimezone(timezone('Asia/Tokyo'))
    except Exception as e:
        logger.exception(e)
        raise e

    return jst_transaction_time
