# -*- coding: utf-8 -*-
import logging
import json
import urllib2
import socket
from sqlalchemy.orm.exc import NoResultFound
from altair.pgw import util as pgw_util
from .exceptions import PgwAPIError
from .models import _session, PGWResponseLog
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
    pgw_3d_secure_status = get_pgw_3d_secure_status(payment_id=payment_id, session=session, for_update=False)
    pgw_request = create_settlement_request(payment_id=payment_id, pgw_order_status=pgw_order_status,
                                            pgw_3d_secure_status=pgw_3d_secure_status, email=email)

    # PGWのAuthorizeAPIをコールします
    is_three_d_secure_authentication_result = _is_three_d_secure_authentication_result(pgw_3d_secure_status)
    pgw_request_data = {
        "pgw_request": pgw_request,
        "is_three_d_secure_authentication_result": is_three_d_secure_authentication_result
    }
    try:
        pgw_api_response = _request_orderreview_pgw(
            request=request,
            pgw_request_data=pgw_request_data,
            request_url=_get_url_for_auth(request)
        )
    # 一般的なHTTPエラー
    except urllib2.HTTPError as http_error:
        logger.exception(http_error)
        raise PgwAPIError(error_code='unexpected_error',
                          error_message='Error occurred during HTTP connection: (StatusCode: {}, Reason: {})'.format(
                              http_error.code, http_error.reason),
                          payment_id=payment_id)
    # 以下参照：http://tdoc.info/blog/2012/06/22/urllib_socket.html
    # HTTPリクエスト送信中に発生するエラー
    except urllib2.URLError as url_error:
        logger.exception(url_error)
        raise PgwAPIError(error_code='url_open_error',
                          error_message='Error while sending request data',
                          payment_id=payment_id)
    # HTTPヘッダー、ボディを受信中に発生するエラー
    except socket.timeout as timeout:
        logger.exception(timeout)
        raise PgwAPIError(error_code='time_out_error',
                          error_message='Timeout occurred while receiving response data',
                          payment_id=payment_id)
    except Exception as e:
        logger.exception(e)
        raise PgwAPIError(error_code='unexpected_error',
                          error_message='Failed to process authorize',
                          payment_id=payment_id)

    # オーソリ通信結果をDBに保存
    log_id = _insert_response_record(payment_id=payment_id,
                                     pgw_api_response=pgw_api_response,
                                     api_type='authorize',
                                     transaction_status=pgw_order_status.payment_status)
    # PGWの処理が成功したのか失敗したのかを確認する
    _confirm_pgw_api_result(payment_id=payment_id, api_type='authorize', pgw_api_response=pgw_api_response)

    # PGWResponseLogのステータスの更新
    PGWResponseLog.update_transaction_status(log_id, int(PaymentStatusEnum.auth))
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
    pgw_request_data = {
        "payment_id": payment_id,
        "capture_amount": capture_amount
    }
    try:
        pgw_api_response = _request_orderreview_pgw(
            request=request,
            pgw_request_data=pgw_request_data,
            request_url="{0}orderreview/capture".format(_get_backend_domain(request))
        )
    # 一般的なHTTPエラー
    except urllib2.HTTPError as http_error:
        logger.exception(http_error)
        raise PgwAPIError(error_code='unexpected_error',
                          error_message='Error occurred during HTTP connection: (StatusCode: {}, Reason: {})'.format(
                              http_error.code, http_error.reason),
                          payment_id=payment_id)
    # 以下参照：http://tdoc.info/blog/2012/06/22/urllib_socket.html
    # HTTPリクエスト送信中に発生するエラー
    except urllib2.URLError as url_error:
        logger.exception(url_error)
        raise PgwAPIError(error_code='url_open_error',
                          error_message='Error while sending request data',
                          payment_id=payment_id)
    # HTTPヘッダー、ボディを受信中に発生するエラー
    except socket.timeout as timeout:
        logger.exception(timeout)
        raise PgwAPIError(error_code='time_out_error',
                          error_message='Timeout occurred while receiving response data',
                          payment_id=payment_id)
    except Exception as e:
        logger.exception(e)
        raise PgwAPIError(error_code='unexpected_error',
                          error_message='Failed to process capture',
                          payment_id=payment_id)

    # キャプチャ通信結果をDBに保存
    log_id = _insert_response_record(payment_id=payment_id,
                                     pgw_api_response=pgw_api_response,
                                     api_type='capture',
                                     transaction_status=pgw_order_status.payment_status,
                                     )

    # PGWの処理が成功したのか失敗したのかを確認する
    _confirm_pgw_api_result(payment_id=payment_id, api_type='capture', pgw_api_response=pgw_api_response)

    # PGWResponseLogのステータスの更新
    PGWResponseLog.update_transaction_status(log_id, int(PaymentStatusEnum.capture))

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
    pgw_3d_secure_status = get_pgw_3d_secure_status(payment_id=payment_id, session=session, for_update=False)
    is_three_d_secure_authentication_result = _is_three_d_secure_authentication_result(pgw_3d_secure_status)
    pgw_request = create_settlement_request(payment_id=payment_id, pgw_order_status=pgw_order_status,
                                            pgw_3d_secure_status=pgw_3d_secure_status, email=email)

    # PGWのAuthorizeAPIをコールします
    pgw_request_data = {
        "pgw_request": pgw_request,
        "is_three_d_secure_authentication_result": is_three_d_secure_authentication_result
    }
    try:
        pgw_api_response = _request_orderreview_pgw(
            request=request,
            pgw_request_data=pgw_request_data,
            request_url=_get_url_for_auth_and_capture(request)
        )
    # 一般的なHTTPエラー
    except urllib2.HTTPError as http_error:
        logger.exception(http_error)
        raise PgwAPIError(error_code='unexpected_error',
                          error_message='Error occurred during HTTP connection: (StatusCode: {}, Reason: {})'.format(
                              http_error.code, http_error.reason),
                          payment_id=payment_id)
    # 以下参照：http://tdoc.info/blog/2012/06/22/urllib_socket.html
    # HTTPリクエスト送信中に発生するエラー
    except urllib2.URLError as url_error:
        logger.exception(url_error)
        raise PgwAPIError(error_code='url_open_error',
                          error_message='Error while sending request data',
                          payment_id=payment_id)
    # HTTPヘッダー、ボディを受信中に発生するエラー
    except socket.timeout as timeout:
        logger.exception(timeout)
        raise PgwAPIError(error_code='time_out_error',
                          error_message='Timeout occurred while receiving response data',
                          payment_id=payment_id)
    except Exception as e:
        logger.exception(e)
        raise PgwAPIError(error_code='unexpected_error',
                          error_message='Failed to process authorize and capture',
                          payment_id=payment_id)

    # オーソリ＆キャプチャ通信結果をDBに保存
    log_id = _insert_response_record(payment_id=payment_id,
                                     pgw_api_response=pgw_api_response,
                                     api_type='authorize_and_capture',
                                     transaction_status=pgw_order_status.payment_status,
                                     )

    # PGWの処理が成功したのか失敗したのかを確認する
    _confirm_pgw_api_result(payment_id=payment_id, api_type='authorize_and_capture', pgw_api_response=pgw_api_response)

    # PGWResponseLogのステータスの更新
    PGWResponseLog.update_transaction_status(log_id, int(PaymentStatusEnum.capture))

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
    pgw_request_data = {
        "payment_ids": payment_ids,
        "search_type": search_type
    }
    try:
        pgw_api_response = _request_orderreview_pgw(
            request=request,
            pgw_request_data=pgw_request_data,
            request_url="{0}orderreview/find".format(_get_backend_domain(request))
        )
    # 一般的なHTTPエラー
    except urllib2.HTTPError as http_error:
        logger.exception(http_error)
        raise PgwAPIError(error_code='unexpected_error',
                          error_message='Error occurred during HTTP connection: (StatusCode: {}, Reason: {})'.format(
                              http_error.code, http_error.reason),
                          payment_id=payment_ids)
    # HTTPリクエスト送信中に発生するエラー
    except urllib2.URLError as url_error:
        logger.exception(url_error)
        raise PgwAPIError(error_code='url_open_error',
                          error_message='Error while sending request data',
                          payment_id=payment_ids)
    # HTTPヘッダー、ボディを受信中に発生するエラー
    except socket.timeout as timeout:
        logger.exception(timeout)
        raise PgwAPIError(error_code='time_out_error',
                          error_message='Timeout occurred while receiving response data',
                          payment_id=payment_ids)
    except Exception as e:
        logger.exception(e)
        raise PgwAPIError(error_code='unexpected_error',
                          error_message='Failed to process find',
                          payment_id=payment_ids)

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
    pgw_request_data = {
        "payment_id": payment_id
    }
    try:
        logger.warning("{0}orderreview/cancel_or_refund".format(_get_backend_domain(request)))
        pgw_api_response = _request_orderreview_pgw(
            request=request,
            pgw_request_data=pgw_request_data,
            request_url="{0}orderreview/cancel_or_refund".format(_get_backend_domain(request))
        )
    # 一般的なHTTPエラー
    except urllib2.HTTPError as http_error:
        logger.exception(http_error)
        raise PgwAPIError(error_code='unexpected_error',
                          error_message='Error occurred during HTTP connection: (StatusCode: {}, Reason: {})'.format(
                              http_error.code, http_error.reason),
                          payment_id=payment_id)
    # HTTPリクエスト送信中に発生するエラー
    except urllib2.URLError as url_error:
        logger.exception(url_error)
        raise PgwAPIError(error_code='url_open_error',
                          error_message='Error while sending request data',
                          payment_id=payment_id)
    # HTTPヘッダー、ボディを受信中に発生するエラー
    except socket.timeout as timeout:
        logger.exception(timeout)
        raise PgwAPIError(error_code='time_out_error',
                          error_message='Timeout occurred while receiving response data',
                          payment_id=payment_id)
    except Exception as e:
        logger.exception(e)
        raise PgwAPIError(error_code='unexpected_error',
                          error_message='Failed to process cancel or refund',
                          payment_id=payment_id)

    # キャンセル／リファンド通信結果をDBに保存
    log_id = _insert_response_record(payment_id=payment_id,
                                     pgw_api_response=pgw_api_response,
                                     api_type='cancel_or_refund',
                                     transaction_status=pgw_order_status.payment_status,
                                     )

    # PGWの処理が成功したのか失敗したのかを確認する
    _confirm_pgw_api_result(payment_id=payment_id, api_type='cancel_or_refund', pgw_api_response=pgw_api_response)

    # PGWOrderStatusテーブルの更新
    transaction_time = _convert_to_jst_timezone(pgw_api_response.get('transactionTime'))
    pgw_order_status.canceled_at = transaction_time
    updated_status = 0
    # キャプチャ済みの場合は払戻ステータスで更新
    if pgw_order_status.payment_status == int(PaymentStatusEnum.capture):
        pgw_order_status.refunded_at = transaction_time
        pgw_order_status.payment_status = int(PaymentStatusEnum.refund)
        updated_status = int(PaymentStatusEnum.refund)
    # オーソリのキャンセルはキャンセルステータスで更新
    else:
        pgw_order_status.payment_status = int(PaymentStatusEnum.cancel)
        updated_status = int(PaymentStatusEnum.cancel)
    PGWOrderStatus.update_pgw_order_status(pgw_order_status=pgw_order_status, session=session)
    # PGWResponseLogのステータスの更新
    PGWResponseLog.update_transaction_status(log_id, updated_status)


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
    pgw_request_data = {
        "payment_id": payment_id,
        "modified_amount": int(modified_amount)
    }
    try:
        pgw_api_response = _request_orderreview_pgw(
            request=request,
            pgw_request_data=pgw_request_data,
            request_url = "{0}orderreview/modify".format(_get_backend_domain(request))
        )
    # 一般的なHTTPエラー
    except urllib2.HTTPError as http_error:
        logger.exception(http_error)
        raise PgwAPIError(error_code='unexpected_error',
                          error_message='Error occurred during HTTP connection: (StatusCode: {}, Reason: {})'.format(
                              http_error.code, http_error.reason),
                          payment_id=payment_id)
    # HTTPリクエスト送信中に発生するエラー
    except urllib2.URLError as url_error:
        logger.exception(url_error)
        raise PgwAPIError(error_code='url_open_error',
                          error_message='Error while sending request data',
                          payment_id=payment_id)
    # HTTPヘッダー、ボディを受信中に発生するエラー
    except socket.timeout as timeout:
        logger.exception(timeout)
        raise PgwAPIError(error_code='time_out_error',
                          error_message='Timeout occurred while receiving response data',
                          payment_id=payment_id)
    except Exception as e:
        logger.exception(e)
        raise PgwAPIError(error_code='unexpected_error',
                          error_message='',
                          payment_id=payment_id)

    # 決済金額変更通信結果をDBに保存
    log_id = _insert_response_record(payment_id=payment_id,
                                     pgw_api_response=pgw_api_response,
                                     api_type='modify',
                                     transaction_status=pgw_order_status.payment_status,
                                     )

    # PGWの処理が成功したのか失敗したのかを確認する
    _confirm_pgw_api_result(payment_id=payment_id, api_type='modify', pgw_api_response=pgw_api_response)

    # PGWOrderStatusテーブルの更新
    pgw_order_status.gross_amount = modified_amount
    PGWOrderStatus.update_pgw_order_status(pgw_order_status=pgw_order_status, session=session)
    # PGWResponseLogのステータスの更新
    PGWResponseLog.update_transaction_status(log_id, pgw_order_status.payment_status)


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
    pgw_request_data = {
        "sub_service_id": pgw_order_status.pgw_sub_service_id,
        "enrollment_id": enrollment_id,
        "callback_url": callback_url,
        "gross_amount": pgw_order_status.gross_amount,
        "card_token": pgw_order_status.card_token
    }

    try:
        pgw_api_response = _request_orderreview_pgw(
            request=request,
            pgw_request_data=pgw_request_data,
            request_url=_get_url_for_3d_secure(request)
        )
    # 一般的なHTTPエラー
    except urllib2.HTTPError as http_error:
        logger.exception(http_error)
        raise PgwAPIError(error_code='unexpected_error',
                          error_message='Error occurred during HTTP connection: (StatusCode: {}, Reason: {})'.format(
                              http_error.code, http_error.reason),
                          payment_id=payment_id)
    # HTTPリクエスト送信中に発生するエラー
    except urllib2.URLError as url_error:
        logger.exception(url_error)
        raise PgwAPIError(error_code='url_open_error',
                          error_message='Error while sending request data',
                          payment_id=payment_id)
    # HTTPヘッダー、ボディを受信中に発生するエラー
    except socket.timeout as timeout:
        logger.exception(timeout)
        raise PgwAPIError(error_code='time_out_error',
                          error_message='Timeout occurred while receiving response data',
                          payment_id=payment_id)
    except Exception as e:
        logger.exception(e)
        raise PgwAPIError(error_code='unexpected_error',
                          error_message='',
                          payment_id=payment_id)

    # 3Dセキュアの使用可否確認通信結果をDBに保存
    log_id = _insert_response_record(payment_id=payment_id,
                                     pgw_api_response=pgw_api_response,
                                     api_type='three_d_secure_enrollment_check',
                                     transaction_status=int(ThreeDInternalStatusEnum.initialized),
                                     )

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


def _request_orderreview_pgw(request, pgw_request_data, request_url):
    """
    PGWのリクエストを送るためにorderreviewを経由してアクセスする(python2.7.3環境で疎通ができないため、暫定対応)
    :param request:
    :param pgw_request_data:
    :param request_url:
    :return:
    """
    import urllib
    from contextlib import closing

    REQUEST_HEADERS = {'Content-Type': 'application/x-www-form-urlencoded'}
    timeout = 60

    post_params = urllib.urlencode(pgw_request_data)
    pgw_request = urllib2.Request(request_url, post_params, REQUEST_HEADERS)
    # localで通信する場合は以下のコメントアウトを外してください
    # pgw_request.set_proxy('localhost:58080', 'http')
    opener = urllib2.build_opener(urllib2.HTTPSHandler())
    urllib2.install_opener(opener)
    with closing(urllib2.urlopen(pgw_request, timeout=float(timeout))) as pgw_response:
        pgw_result = pgw_response.read()
        # PGW専用ログにレスポンスを出力する
        logger.info(
            'PGW request URL = {url}, PGW result = {result}'.format(url=request_url, result=pgw_result))
        pgw_dict = json.loads(pgw_result)

    return pgw_dict


def create_settlement_request(payment_id, pgw_order_status, pgw_3d_secure_status, email):
    """
    AuthorizeAPI, AuthorizeAndCaptureAPI用リクエストオブジェクトを作成します
    :param payment_id: 予約番号(cart:order_no, lots:entry_no)
    :param pgw_order_status: PGWOrderStatusテーブルのレコード
    :param pgw_3d_secure_status: PGW3DSecureStatusテーブルのレコード
    :param email: Eメールアドレス
    :return: pgw_request: PGW決済リクエストオブジェクト(PGWRequest)
    """
    pgw_request = {
        "sub_service_id": pgw_order_status.pgw_sub_service_id,
        "payment_id": payment_id,
        "gross_amount": pgw_order_status.gross_amount,
        "card_token": pgw_order_status.card_token,
        "cvv_token": pgw_order_status.cvv_token,
        "email": email,
        "message_version": pgw_3d_secure_status.message_version,
        "cavv_algorithm": pgw_3d_secure_status.cavv_algorithm,
        "cavv": pgw_3d_secure_status.cavv,
        "eci": pgw_3d_secure_status.eci,
        "transaction_id": pgw_3d_secure_status.transaction_id,
        "transaction_status": pgw_3d_secure_status.transaction_status
    }

    return json.dumps(pgw_request)


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
        raise PgwAPIError(error_code=None, error_message='PGW3DSecureStatus record is not found. payment_id = {}'.format(payment_id))
    
    need_updated = True
    if validate_for_update:
        need_updated = _need_update_internal_status(pgw_3d_secure_status)
    
    if need_updated:
        if three_d_secure_authentication_status == u'authentication_available':
            pgw_3d_secure_status.three_d_internal_status = int(ThreeDInternalStatusEnum.initialized)
            pgw_3d_secure_status.three_d_auth_status = three_d_secure_authentication_status
        elif three_d_secure_authentication_status == u'fully_authenticated' or \
                three_d_secure_authentication_status == u'eligible_for_3d_secure':
            pgw_3d_secure_status.three_d_internal_status = int(ThreeDInternalStatusEnum.success)
            pgw_3d_secure_status.three_d_auth_status = three_d_secure_authentication_status
        elif three_d_secure_authentication_status == u'not_eligible_for_3d_secure' or \
                three_d_secure_authentication_status == u'authentication_error' or \
                three_d_secure_authentication_status == u'connection_error':
            pgw_3d_secure_status.three_d_internal_status = int(ThreeDInternalStatusEnum.failure)
            pgw_3d_secure_status.three_d_auth_status = three_d_secure_authentication_status
        else:
            # エラーハンドリングは別途検討
            # PGWから想定外のステータスが返ってきた場合
            raise PgwAPIError(error_code=pgw_3d_secure_status.three_d_auth_status,
                              error_message='three_d_secure_authentication_status is wrong. '
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


def update_three_d_secure_authentication_result(pgw_3d_secure_status, payment_result, session=None):
    """
    3DS 本人確認認証成功時に返却されるthreeDSecureAuthenticationResultの結果を
    PGW3DSecureStatusのカラムへ反映する
    :param pgw_3d_secure_status: PGW3DSecureStatusインスタンス
    :param payment_result: 3DS本人確認認証成功時に返却されるPGWからのレスポンス
    :param session: DBセッション
    """
    _convert_payment_result(pgw_3d_secure_status, payment_result)
    PGW3DSecureStatus.update_pgw_3d_secure_status(pgw_3d_secure_status)


def _convert_payment_result(pgw_3d_secure_status, payment_result):
    """
    payment_resultのレスポンスからthreeDSecureAuthenticationResultのパラメータを抽出し
    PGW3DSecureStatusのインスタンスにつめる
    :param pgw_3d_secure_status: PGW3DSecureStatusインスタンス
    :param payment_result: 3DS本人確認認証成功時に返却されるPGWからのレスポンス
    """
    three_d_secure_authentication_result = payment_result.get('threeDSecureAuthenticationResult')
    pgw_3d_secure_status.message_version = three_d_secure_authentication_result.get('messageVersion')
    pgw_3d_secure_status.cavv_algorithm = three_d_secure_authentication_result.get('cavvAlgorithm')
    pgw_3d_secure_status.cavv = three_d_secure_authentication_result.get('cavv')
    pgw_3d_secure_status.eci = three_d_secure_authentication_result.get('eci')
    pgw_3d_secure_status.transaction_id = three_d_secure_authentication_result.get('transactionId')
    pgw_3d_secure_status.transaction_status = three_d_secure_authentication_result.get('transactionStatus')


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
        raise PgwAPIError(error_code='unexpected_error',
                          error_message='')

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


def get_pgw_response_log(payment_id, session):
    """
    PGWRequestLogテーブルのレコードを取得します。
    :param payment_id: 予約番号(cart:order_no, lots:entry_no)
    :param session:
    :return:
    """
    pgw_response_log = PGWResponseLog.get_pgw_response_log(payment_id, session)
    return pgw_response_log


def _confirm_pgw_api_result(payment_id, api_type, pgw_api_response):
    """
    PGW APIのリクエスト処理結果を確認します
    :param payment_id: 予約番号(cart:order_no, lots:entry_no)
    :param api_type: コールしたAPIの種類
    :param pgw_api_response: PGW APIのレスポンス
    """
    result_type = pgw_api_response.get(u'resultType')
    error_code = pgw_api_response.get(u'errorCode')
    error_message = pgw_api_response.get(u'errorMessage')
    if result_type != u'success':
        # 原則、PGW側で処理が出来ていればsuccessが帰ってくる模様
        raise PgwAPIError(error_code=error_code, error_message=error_message)


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

    return jst_transaction_time.replace(tzinfo=None)


def _is_three_d_secure_authentication_result(pgw_3d_secure_status):
    """
    pgw_requestにthreeDSecureAuthenticationResultのデータが入ってるかチェックする
    :param pgw_3d_secure_status: PGW3DSecureStatusテーブルのレコード
    :return: True or False
    """
    return pgw_3d_secure_status.message_version is not None and \
           pgw_3d_secure_status.cavv_algorithm is not None and \
           pgw_3d_secure_status.cavv is not None and \
           pgw_3d_secure_status.eci is not None and \
           pgw_3d_secure_status.transaction_id is not None and \
           pgw_3d_secure_status.transaction_status is not None


def _insert_response_record(payment_id, pgw_api_response, api_type, transaction_status, session=None):
    """
    PaymentGatewayのAPIレスポンスをDBに挿入します。
    :param payment_id:
    :param pgw_api_response: PaymentGatewayからのレスポンスデータ
    :param api_type: コールしたAPIの種類
    :param session: DBセッション
    """
    payment_id = payment_id
    transaction_status = transaction_status
    transaction_time = _convert_to_jst_timezone(pgw_api_response.get(u'transactionTime'))
    pgw_error_code = pgw_api_response.get(u'errorCode')
    card_comm_error_code = None
    try:
        #  楽天カードがレスポンスに設定するエラーコード
        reference = pgw_api_response.get(u'reference')
        card_result = reference.get(u'rakutenCardResult')
        card_comm_error_code = card_result.get(u'errCd')
    except KeyError:
        pass

    #  楽天カードがレスポンスに設定するエラーコード：原則設定されているはずだが、PGWがメッセージを設定することもある
    card_detail_error_code = pgw_api_response.get(u'errorMessage')
    # PaymentGWとの決済通信の結果をDBに保存する
    pgw_response_log = PGWResponseLog(
        payment_id=payment_id,
        transaction_time=transaction_time,
        transaction_type=api_type,
        transaction_status=transaction_status,
        pgw_error_code=pgw_error_code,
        card_comm_error_code=card_comm_error_code,
        card_detail_error_code=card_detail_error_code
    )

    return PGWResponseLog.insert_pgw_response_log(pgw_response_log)


def update_3d_secure_res_status(payment_id, status, session=None):
    """
    3Dセキュアはスコープが代わり、Viewで処理する必要があるため、専用のヘルパーでステータス更新を行う。
    :param payment_id: 予約番号(cart:order_no, lots:entry_no)
    :param status: 3Dセキュアのステータス
    :param session: DBセッション
    :return:
    """

    response_record = PGWResponseLog.get_pgw_response_log(payment_id=payment_id, session=session)[0]
    PGWResponseLog.update_transaction_status(log_id=response_record.id, tx_status=status, session=session)


def get_pgw_status(transaction_status, api_type):
    """
    決済全体のフローの観点から見たステータスを取得します。
    ３D認証〜オーソリ・キャプチャ〜キャンセル・リファンド
    :param api_type: コールしたAPIの種類
    :param transaction_status: PGWOrderStatusかPGW3DSecureStatusのDB上のステータス
    :return: Integer
    """
    is_3d_status = api_type == 'three_d_secure_enrollment_check'
    int_status = int(transaction_status)
    return pgw_util.get_pgw_status(int_status, is_3d_status)


def get_pgw_status_message(common_code, detail_code):
    return pgw_util.get_pgw_message_description(common_code, detail_code)


def _get_url_for_3d_secure(request):
    return 'https://{0}{1}'.format(request.host, '/orderreview/three_d_secure_enrollment_check')


def _get_url_for_auth(request):
    return 'https://{0}{1}'.format(request.host, '/orderreview/authorize')


def _get_url_for_auth_and_capture(request):
    return 'https://{0}{1}'.format(request.host, '/orderreview/authorize_and_capture')


def _get_backend_domain(request):
    return request.registry.settings.get('altair.pgw.orderreview_url')