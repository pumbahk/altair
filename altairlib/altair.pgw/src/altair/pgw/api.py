# -*- coding:utf-8 -*-
from pyramid.interfaces import IRequest
from .interfaces import IPgwAPICommunicatorFactory


def authorize(request, pgw_payment_request):
    """
    PGWのAuthorizeAPIをコールします
    :param request: リクエスト
    :param pgw_payment_request: PGW決済リクエストオブジェクト(ticketing.src.altair.app.ticketing.pgw.api.PGWPayment)
    :return: PGWからのAPIレスポンス
    """
    pgw_api_client = create_pgw_api_communicator(request_or_registry=request)

    # request_authorize呼び出し
    result = pgw_api_client.request_authorize(
            sub_service_id=pgw_payment_request.sub_service_id,
            payment_id=pgw_payment_request.payment_id,
            gross_amount=pgw_payment_request.gross_amount,
            card_amount=pgw_payment_request.card_amount,
            card_token=pgw_payment_request.card_token,
            cvv_token=pgw_payment_request.cvv_token,
            email=pgw_payment_request.email
    )
    return result


def capture(request, payment_id, capture_amount):
    """
    PGWのCaptureAPIをコールします
    :param request: リクエスト
    :param payment_id: 予約番号(cart:order_no, lots:entry_no)
    :param capture_amount: キャプチャする決済金額
    :return: PGWからのAPIレスポンス
    """
    pgw_api_client = create_pgw_api_communicator(request_or_registry=request)

    # request_authorize呼び出し
    result = pgw_api_client.request_capture(
            payment_id=payment_id,
            capture_amount=capture_amount
    )
    return result


def authorize_and_capture(request, pgw_payment_request):
    """
    PGWのAuthorizeAndCaptureAPIをコールします
    :param request: リクエスト
    :param pgw_payment_request: PGW決済リクエストオブジェクト(ticketing.src.altair.app.ticketing.pgw.api.PGWPayment)
    :return: PGWからのAPIレスポンス
    """
    pgw_api_client = create_pgw_api_communicator(request_or_registry=request)

    # request_authorize呼び出し
    result = pgw_api_client.request_authorize_and_capture(
        sub_service_id=pgw_payment_request.sub_service_id,
        payment_id=pgw_payment_request.payment_id,
        gross_amount=pgw_payment_request.gross_amount,
        card_amount=pgw_payment_request.card_amount,
        card_token=pgw_payment_request.card_token,
        cvv_token=pgw_payment_request.cvv_token,
        email=pgw_payment_request.email
    )
    return result


def find(request, payment_ids, search_type=None):
    """
    PGWのFindAPIをコールします
    :param request: リクエスト
    :param payment_ids: 予約番号リスト(cart:order_no, lots:entry_no)
    :param search_type: 検索タイプ
    :return: PGWからのAPIレスポンス
    """
    pgw_api_client = create_pgw_api_communicator(request_or_registry=request)

    # request_authorize呼び出し
    result = pgw_api_client.request_find(
        payment_ids=payment_ids
    )
    return result


def cancel_or_refund(request, payment_id):
    """
    PGWのCancelOrRefundAPIをコールします
    :param request: リクエスト
    :param payment_id: 予約番号(cart:order_no, lots:entry_no)
    :return: PGWからのAPIレスポンス
    """
    pgw_api_client = create_pgw_api_communicator(request_or_registry=request)

    # request_authorize呼び出し
    result = pgw_api_client.request_cancel_or_refund(
        payment_id=payment_id
    )
    return result


def modify(request, payment_id, modified_amount):
    """
    PGWのModifyAPIをコールします
    :param request: リクエスト
    :param payment_id: 予約番号(cart:order_no, lots:entry_no)
    :param modified_amount: 変更後の決済金額
    :return: PGWからのAPIレスポンス
    """
    pgw_api_client = create_pgw_api_communicator(request_or_registry=request)

    # request_authorize呼び出し
    result = pgw_api_client.request_modify(
        payment_id=payment_id,
        modified_amount=modified_amount
    )
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
    pgw_api_client = create_pgw_api_communicator(request_or_registry=request)

    # request_authorize呼び出し
    result = pgw_api_client.request_3d_secure_enrollment_check(
        sub_service_id=sub_service_id,
        enrollment_id=enrollment_id,
        callback_url=callback_url,
        amount=amount,
        card_token=card_token
    )
    return result


def create_pgw_api_communicator(request_or_registry):
    """
    PGW APIクライアントを呼び出す通信用クラスの初期化処理を行います。
    :param request_or_registry: リクエスト
    :return: PgwAPICommunicatorFactory
    """
    if IRequest.providedBy(request_or_registry):
        registry = request_or_registry.registry
    else:
        registry = request_or_registry
    factory = registry.getUtility(IPgwAPICommunicatorFactory)
    return factory()
