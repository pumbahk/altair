# -*- coding:utf-8 -*-
from pyramid.interfaces import IRequest
from .interfaces import IPgwAPICommunicatorFactory


def authorize(request, sub_service_id, payment_id, gross_amount,
                          card_amount, card_token, cvv_token, email, three_d_secure_authentication_result=None):
    """

    :param request:
    :param sub_service_id:
    :param payment_id:
    :param gross_amount:
    :param card_amount:
    :param card_token:
    :param cvv_token:
    :param email:
    :param three_d_secure_authentication_result:
    :return:
    """
    pgw_api_client = create_pgw_api_communicator(request_or_registry=request)

    # request_authorize呼び出し
    result = pgw_api_client.request_authorize(
            sub_service_id=sub_service_id,
            payment_id=payment_id,
            gross_amount=gross_amount,
            card_amount=card_amount,
            card_token=card_token,
            cvv_token=cvv_token,
            email=email
    )
    return result


def capture(request, payment_id, capture_amount):
    """

    :param request:
    :param payment_id:
    :param capture_amount:
    :return:
    """
    pgw_api_client = create_pgw_api_communicator(request_or_registry=request)

    # request_authorize呼び出し
    result = pgw_api_client.request_capture(
            payment_id=payment_id,
            capture_amount=capture_amount
    )
    return result


def three_d_secure_enrollment_check(request, sub_service_id, enrollment_id, callback_url, amount, card_token):
    """

    :param request:
    :param sub_service_id:
    :param enrollment_id:
    :param callback_url:
    :param amount:
    :param card_token:
    :return:
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
