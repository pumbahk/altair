# -*- coding:utf-8 -*-

"""
TODO PaymentGW APIのスタブです。本実装が完了次第削除します。
"""


PGW_PAYMENT_STATUS_TYPE_INITIALIZED = u'initialized'
PGW_PAYMENT_STATUS_TYPE_AUTHORIZED = u'authorized'
PGW_PAYMENT_STATUS_TYPE_CAPTURED = u'captured'
PGW_API_RESULT_TYPE_SUCCESS = u'success'
PGW_API_RESULT_TYPE_FAILURE = u'failure'
PGW_API_RESULT_TYPE_PENDING = u'pending'


def find_payment(order_like):
    return {
        u'paymentStatusType': PGW_PAYMENT_STATUS_TYPE_INITIALIZED,
        u'grossAmount': order_like.payment_amount
    }


def authorize_and_capture(order_like, sub_service_id):
    return {
        u'resultType': PGW_API_RESULT_TYPE_SUCCESS
    }
    # return {
    #     u'resultType': PGW_API_RESULT_TYPE_FAILURE,
    #     u'errorCode': 'unacceptable_request',
    #     u'errorMessage': 'unacceptable_request'
    # }


def capture(order_no):
    return {
        u'resultType': PGW_API_RESULT_TYPE_SUCCESS
    }
    # return {
    #     u'resultType': PGW_API_RESULT_TYPE_FAILURE,
    #     u'errorCode': 'unacceptable_request',
    #     u'errorMessage': 'unacceptable_request'
    # }


def modify(order_like, modify_amount):
    return {
        u'resultType': PGW_API_RESULT_TYPE_SUCCESS
    }
    # return {
    #     u'resultType': PGW_API_RESULT_TYPE_FAILURE,
    #     u'errorCode': 'unacceptable_request',
    #     u'errorMessage': 'unacceptable_request'
    # }
