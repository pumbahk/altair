# -*- coding: utf-8 -*-
import logging
import altair.pgw.api as pgw_api
from sqlalchemy.orm.exc import NoResultFound
from .models import _session
from altair.pgw.api import PGWRequest
from .models import PGWOrderStatus, PGWMaskedCardDetail, PGW3DSecureStatus, PaymentStatusEnum, ThreeDInternalStatusEnum
from altair.app.ticketing.models import DBSession
from altair.app.ticketing.users.models import UserCredential
from datetime import datetime
from pytz import timezone

logger = logging.getLogger(__name__)


def authorize(request, payment_id, email, user_id, session=None):
    """
    PGWのAuthorizeAPIをコールします
    :param request: リクエスト
    :param payment_id: 予約番号(cart:order_no, lots:entry_no)
    :param email: Eメールアドレス
    :param user_id: ユーザID
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
    _convert_card_info(pgw_order_status, pgw_api_response)
    PGWOrderStatus.update_pgw_order_status(pgw_order_status=pgw_order_status, session=session)

    # カードトークン関連情報テーブルの登録
    if user_id:
        _register_pgw_masked_card_detail(pgw_api_response=pgw_api_response, user_id=user_id)


def auth_cancel(payment_id, session=None):
    """
    オーソリキャンセル対象とマークする処理します
    :param payment_id: 予約番号(cart:order_no, lots:entry_no)
    :param session: DBセッション
    """
    if session is None:
        session = _session
    # PGWOrderStatusレコード取得
    pgw_order_status = get_pgw_order_status(payment_id=payment_id, session=session, for_update=True)

    # PGWOrderStatusテーブルの更新
    pgw_order_status.payment_status = int(PaymentStatusEnum.auth_cancel)
    PGWOrderStatus.update_pgw_order_status(pgw_order_status=pgw_order_status, session=session)


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


def authorize_and_capture(request, payment_id, email, user_id, session=None):
    """
    PGWのAuthorizeAndCaptureAPIをコールします
    :param request: リクエスト
    :param payment_id: 予約番号(cart:order_no, lots:entry_no)
    :param email: Eメールアドレス
    :param user_id: ユーザID
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
    _convert_card_info(pgw_order_status, pgw_api_response)
    PGWOrderStatus.update_pgw_order_status(pgw_order_status=pgw_order_status, session=session)

    # カードトークン関連情報テーブルの登録
    if user_id:
        _register_pgw_masked_card_detail(pgw_api_response=pgw_api_response, user_id=user_id)


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


def three_d_secure_enrollment_check(request, payment_id, callback_url, session=None):
    """
    PGWの3DSecureEnrollmentCheckAPIをコールします
    :param request: リクエスト
    :param payment_id: 予約番号(cart:order_no, lots:entry_no)
    :param callback_url: コールバックURL
    :param session: DBセッション
    :return: PGWからのAPIレスポンス
    """
    if session is None:
        session = _session
    pgw_3d_secure_status = get_pgw_3d_secure_status(payment_id=payment_id, session=session, for_update=True)

    # 既に3DSecure認証済みの場合はAPIをコールせず処理を終了する
    if pgw_3d_secure_status is not None and \
            pgw_3d_secure_status.three_d_internal_status == int(ThreeDInternalStatusEnum.success):
        return None

    pgw_order_status = get_pgw_order_status(payment_id=payment_id, session=session, for_update=True)

    # 3DSecure認証用ID生成
    enrollment_id = '{}_E'.format(payment_id)

    # PGWの3DSecureEnrollmentCheckAPIをコールします
    pgw_api_response = pgw_api.three_d_secure_enrollment_check(
        request=request,
        sub_service_id=pgw_order_status.pgw_sub_service_id,
        enrollment_id=enrollment_id,
        callback_url=callback_url,
        amount=pgw_order_status.gross_amount,
        card_token=pgw_order_status.card_token)

    # PGWの処理が成功したのか失敗したのかを確認する
    _confirm_pgw_api_result(
        payment_id=payment_id, api_type='three_d_secure_enrollment_check', pgw_api_response=pgw_api_response
    )

    # PGWOrderStatusテーブルの更新
    pgw_order_status = get_pgw_order_status(payment_id=payment_id, session=session)
    pgw_order_status.enrolled_at = _convert_to_jst_timezone(pgw_api_response.get('transactionTime'))
    PGWOrderStatus.update_pgw_order_status(pgw_order_status=pgw_order_status, session=session)

    # 既にレコードが存在する場合はアップデート
    if pgw_3d_secure_status is not None:
        pgw_3d_secure_status.agency_request_id = pgw_api_response.get(u'agencyRequestId')
        pgw_3d_secure_status.three_d_auth_status = pgw_api_response.get(u'threeDSecureAuthenticationStatus')
        pgw_3d_secure_status.three_d_internal_status = int(ThreeDInternalStatusEnum.initialized)
        PGW3DSecureStatus.update_pgw_3d_secure_status(pgw_3d_secure_status=pgw_3d_secure_status, session=session)
    # レコードが存在しない場合は初期登録を行う
    else:
        pgw_3d_secure_status = PGW3DSecureStatus(
            pgw_sub_service_id=pgw_order_status.pgw_sub_service_id,
            payment_id=payment_id,
            enrollment_id=enrollment_id,
            agency_request_id=pgw_api_response.get(u'agencyRequestId'),
            three_d_auth_status=pgw_api_response.get(u'threeDSecureAuthenticationStatus'),
            three_d_internal_status=int(ThreeDInternalStatusEnum.initialized)
        )
        PGW3DSecureStatus.insert_pgw_3d_secure_status(pgw_3d_secure_status=pgw_3d_secure_status, session=session)

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
    PGWOrderStatusのレコード初期登録 or アップデート(既存レコードが存在する場合)を行う
    :param sub_service_id: 店舗ID
    :param payment_id: 予約番号(cart:order_no, lots:entry_no)
    :param card_token: カードトークン
    :param cvv_token: セキュリティコードトークン
    :param gross_amount: 決済総額
    :param session: DBセッション
    """
    if session is None:
        session = _session
    pgw_order_status = get_pgw_order_status(payment_id=payment_id, session=session, for_update=True)

    # 既にレコードが存在する場合はアップデート
    if pgw_order_status is not None:
        pgw_order_status.card_token = card_token
        pgw_order_status.cvv_token = cvv_token
        pgw_order_status.payment_status = int(PaymentStatusEnum.initialized)
        pgw_order_status.gross_amount = gross_amount
        PGWOrderStatus.update_pgw_order_status(pgw_order_status=pgw_order_status, session=session)
    # レコードが存在しない場合は初期登録を行う
    else:
        pgw_order_status = PGWOrderStatus(
            pgw_sub_service_id=sub_service_id,
            payment_id=payment_id,
            card_token=card_token,
            cvv_token=cvv_token,
            payment_status=int(PaymentStatusEnum.initialized),
            gross_amount=gross_amount
        )
        PGWOrderStatus.insert_pgw_order_status(pgw_order_status=pgw_order_status, session=session)


def update_three_d_internal_status(payment_id, pgw_api_response, validate_for_update=False, session=None):
    """
    PGW3DSecureStatusのthree_d_internal_statusカラムの更新を行う
    :param payment_id: 予約番号(cart:order_no, lots:entry_no)
    :param pgw_api_response: PGW APIのレスポンス
    :param validate_for_update: 3Dセキュアのステータスの整合性の確認の有無
    :param session: DBセッション
    """
    if session is None:
        session = _session
    pgw_3d_secure_status = get_pgw_3d_secure_status(payment_id=payment_id, session=session, for_update=True)

    # threeDSecureAuthenticationStatusの取得＆判定を行いDBを更新する
    three_d_secure_authentication_status = pgw_api_response.get('threeDSecureAuthenticationStatus')

    if three_d_secure_authentication_status is None:
        raise Exception('PGW3DSecureStatus record is not found. payment_id = {}'.format(payment_id))
    
    need_updated = True
    if validate_for_update:
        need_updated = _need_update_internal_status(pgw_3d_secure_status)
    
    if need_updated:
        if three_d_secure_authentication_status == u'authentication_available':
            pgw_3d_secure_status.three_d_internal_status = int(ThreeDInternalStatusEnum.initialized)
        elif three_d_secure_authentication_status == u'fully_authenticated' or \
                three_d_secure_authentication_status == u'eligible_for_3d_secure':
            pgw_3d_secure_status.three_d_internal_status = int(ThreeDInternalStatusEnum.success)
        elif three_d_secure_authentication_status == u'not_eligible_for_3d_secure' or \
                three_d_secure_authentication_status == u'authentication_error' or \
                three_d_secure_authentication_status == u'connection_error':
            pgw_3d_secure_status.three_d_internal_status = int(ThreeDInternalStatusEnum.failure)
        else:
            # エラーハンドリングは別途検討
            # PGWから想定外のステータスが返ってきた場合
            raise Exception('three_d_secure_authentication_status is wrong. '
                            'payment_id = {payment_id},'
                            'three_d_secure_authentication_status = {three_d_secure_authentication_status}'
                            .format(payment_id=payment_id,
                                    three_d_secure_authentication_status=three_d_secure_authentication_status))

    PGW3DSecureStatus.update_pgw_3d_secure_status(pgw_3d_secure_status)


def _need_update_internal_status(pgw_3d_secure_status):
    if pgw_3d_secure_status.three_d_auth_status == 'authentication_available':
        return pgw_3d_secure_status.three_d_internal_status != ThreeDInternalStatusEnum.initialized
    elif pgw_3d_secure_status.three_d_auth_status == 'eligible_for_3d_secure' \
        or pgw_3d_secure_status.three_d_auth_status == 'fully_authenticated':
        return pgw_3d_secure_status.three_d_internal_status != ThreeDInternalStatusEnum.success
    else:
        return pgw_3d_secure_status.three_d_internal_status != ThreeDInternalStatusEnum.failure


def _register_pgw_masked_card_detail(pgw_api_response, user_id, session=None):
    """
    PGWMaskedCardDetailのレコード登録 or アップデート(既存レコードが存在する場合)を行う
    :param pgw_api_response: PGW APIのレスポンス
    :param user_id: ユーザID
    :param session: DBセッション
    """
    # 楽天会員認証のユーザのみカード情報を登録する
    if session is None:
        session = DBSession

    try:
        user_credential = session.query(UserCredential).filter(UserCredential.user_id == user_id).one()
    except NoResultFound:
        raise

    authentication = user_credential.membership.name
    if authentication != 'rakuten':
        return

    # カードトークン関連情報をPGW APIのレスポンスから取得する
    try:
        card_info = pgw_api_response.get(u'card')
        card_token = card_info.get(u'cardToken')
        card_iin = card_info.get(u'iin')
        card_last4digits = card_info.get(u'last4digits')
        card_expiration_month = card_info.get(u'expirationMonth')
        card_expiration_year = card_info.get(u'expirationYear')
        card_brand_code = card_info.get(u'brandCode')
    except Exception as e:
        logger.exception(e)
        raise e

    pgw_masked_card_detail = get_pgw_masked_card_detail(user_id=user_id, session=session)

    # 既にレコードが存在する場合はアップデート
    if pgw_masked_card_detail is not None:
        pgw_masked_card_detail.card_token = card_token
        pgw_masked_card_detail.card_iin = card_iin
        pgw_masked_card_detail.card_last4digits = card_last4digits
        pgw_masked_card_detail.card_expiration_month = card_expiration_month
        pgw_masked_card_detail.card_expiration_year = card_expiration_year
        pgw_masked_card_detail.card_brand_code = card_brand_code
        PGWMaskedCardDetail.update_pgw_masked_card_detail(pgw_masked_card_detail=pgw_masked_card_detail, session=session)
    # レコードが存在しない場合は初期登録を行う
    else:
        pgw_masked_card_detail = PGWMaskedCardDetail(
            user_id=user_id,
            card_token=card_token,
            card_iin=card_iin,
            card_last4digits=card_last4digits,
            card_expiration_month=card_expiration_month,
            card_expiration_year=card_expiration_year,
            card_brand_code=card_brand_code
        )
        pgw_masked_card_detail.insert_pgw_masked_card_detail(
            pgw_masked_card_detail=pgw_masked_card_detail, session=session
        )


def get_pgw_order_status(payment_id, session=None, for_update=False):
    """
    PGWOrderStatusテーブルのレコードを取得します。
    :param payment_id: 予約番号(cart:order_no, lots:entry_no)
    :param session: DBセッション
    :param for_update: 排他制御フラグ
    :return: PGWOrderStatusレコード
    """
    # PGWOrderStatusのレコードを返す
    pgw_order_status = PGWOrderStatus.get_pgw_order_status(
        payment_id=payment_id, session=session, for_update=for_update
    )
    return pgw_order_status


def get_pgw_masked_card_detail(user_id, session=None):
    """
    PGWMaskedCardDetailテーブルのレコードを取得します。
    :param user_id: ユーザID
    :param session: DBセッション
    :return: PGWMaskedCardDetailレコード
    """
    # PGWMaskedCardDetailのレコードを返す
    pgw_masked_card_detail = PGWMaskedCardDetail.get_pgw_masked_card_detail(user_id=user_id, session=session)
    return pgw_masked_card_detail


def _convert_card_info(pgw_order_status, pgw_api_response):
    card = pgw_api_response.get('card')
    pgw_order_status.card_brand_code = card.get('cardBrand')
    pgw_order_status.card_iin = card.get('iin')
    pgw_order_status.card_last4digits = card.get('last4digits')
    rakuten_card_result = pgw_api_response.get('reference').get('rakutenCardResult')
    pgw_order_status.ahead_com_cd = rakuten_card_result.get('aheadComCd')
    pgw_order_status.approval_no = rakuten_card_result.get('approvalNo')


def get_pgw_3d_secure_status(payment_id, session=None, for_update=False):
    """
    PGW3DSecureStatusテーブルのレコードを取得します。
    :param payment_id: 予約番号(cart:order_no, lots:entry_no)
    :param session: DBセッション
    :param for_update: 排他制御フラグ
    :return: PGW3DSecureStatusレコード
    """
    # PGW3DSecureStatusのレコードを返す
    pgw_3d_secure_status = PGW3DSecureStatus.get_pgw_3d_secure_status(
        payment_id=payment_id, session=session, for_update=for_update
    )
    return pgw_3d_secure_status


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
