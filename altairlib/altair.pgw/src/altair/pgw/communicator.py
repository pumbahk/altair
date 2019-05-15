# -*- coding:utf-8 -*-
import logging
import socket
import json
import urllib
import urllib2
import base64
import hmac
import hashlib

from zope.interface import implementer
from .interfaces import IPgwAPICommunicator, IPgwAPICommunicatorFactory
from datetime import datetime
from pytz import timezone

logger = logging.getLogger(__name__)

@implementer(IPgwAPICommunicator)
class PgwAPICommunicator(object):
    """
    PGW APIと通信を行うクライアントクラスです。
    request_XXXXXメソッドで各APIの機能を呼び出して通信を行います。
    """
    AGENCY_CODE = 'rakutencard'
    CURRENCY_CODE = 'JPY'
    CARD_TOKEN_VERSION = '2'
    WITH_THREE_D_SECURE = 'false'
    ORDER_VERSION = '1'
    DEFAULT_SEARCH_TYPE = 'current'
    REQUEST_HEADERS = {'Content-Type': 'application/x-www-form-urlencoded'}

    def __init__(self, authentication_key, endpoint, service_id, timeout):
        self.authentication_key = authentication_key
        self.endpoint = endpoint
        self.service_id = service_id
        self.timeout = timeout

    @property
    def get_timestamp(self):
        """
        PGWにリクエストする際のtimestampを取得する
        :return: yyyy-MM-dd HH:mm:ss.SSS
        """
        return datetime.now(timezone('UTC')).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

    @property
    def get_ip_address(self):
        """
        サーバーのIPアドレスを取得する
        :return: IPアドレス
        """
        return socket.gethostbyname(socket.gethostname())

    def request_authorize(self, sub_service_id, payment_id, gross_amount,
                          card_amount, card_token, cvv_token, email, three_d_secure_authentication_result=None):
        request_url = self.endpoint + "/Payment/V1/Authorize"

        data = {
            "serviceId": self.service_id,
            "subServiceId": sub_service_id,
            "timestamp": self.get_timestamp,
            "paymentId": payment_id,
            "agencyCode": self.AGENCY_CODE,
            "currencyCode": self.CURRENCY_CODE,
            "grossAmount": gross_amount,
            "cardToken": {
                "version": self.CARD_TOKEN_VERSION,
                "amount": card_amount,
                "cardToken": card_token,
                "cvvToken": cvv_token,
                "withThreeDSecure": self.WITH_THREE_D_SECURE
            },
            "order": {
                "version": self.ORDER_VERSION,
                "email": email,
                "ipAddress": self.get_ip_address
            }
        }

        # 3DSecure認証済みの場合
        if three_d_secure_authentication_result is not None:
            data.update({"threeDSecureAuthenticationResult": three_d_secure_authentication_result})

        # PGW APIのPOSTパラメータ作成
        pgw_request_data = self.create_pgw_request_data(data)

        return self.request_pgw_api(request_url, pgw_request_data)

    def request_capture(self, payment_id, capture_amount):
        request_url = self.endpoint + "/Payment/V1/Capture"

        data = {
            "serviceId": self.service_id,
            "timestamp": self.get_timestamp,
            "paymentId": payment_id,
            "amount": capture_amount
        }

        # PGW APIのPOSTパラメータ作成
        pgw_request_data = self.create_pgw_request_data(data)

        return self.request_pgw_api(request_url, pgw_request_data)

    def request_authorize_and_capture(self, sub_service_id, payment_id, gross_amount, card_amount,
                                      card_token, cvv_token, email, three_d_secure_authentication_result=None):
        request_url = self.endpoint + "/Payment/V1/AuthorizeAndCapture"

        data = {
            "serviceId": self.service_id,
            "subServiceId": sub_service_id,
            "timestamp": self.get_timestamp,
            "paymentId": payment_id,
            "agencyCode": self.AGENCY_CODE,
            "currencyCode": self.CURRENCY_CODE,
            "grossAmount": gross_amount,
            "cardToken": {
                "version": self.CARD_TOKEN_VERSION,
                "amount": card_amount,
                "cardToken": card_token,
                "cvvToken": cvv_token,
                "withThreeDSecure": self.WITH_THREE_D_SECURE
            },
            "order": {
                "version": self.ORDER_VERSION,
                "email": email,
                "ipAddress": self.get_ip_address
            }
        }

        # 3DSecure認証済みの場合
        if three_d_secure_authentication_result is not None:
            data.update({"threeDSecureAuthenticationResult": three_d_secure_authentication_result})

        # PGW APIのPOSTパラメータ作成
        pgw_request_data = self.create_pgw_request_data(data)

        return self.request_pgw_api(request_url, pgw_request_data)

    def request_find(self, payment_ids, search_type=None):
        request_url = self.endpoint + "/Payment/V1/Find"

        data = {
            "serviceId": self.service_id,
            "timestamp": self.get_timestamp,
            "searchType": search_type if search_type is not None else self.DEFAULT_SEARCH_TYPE,
            "paymentIds": payment_ids
        }

        # PGW APIのPOSTパラメータ作成
        pgw_request_data = self.create_pgw_request_data(data)

        return self.request_pgw_api(request_url, pgw_request_data)

    def request_cancel_or_refund(self, payment_id):
        request_url = self.endpoint + "/Payment/V1/CancelOrRefund"

        data = {
            "serviceId": self.service_id,
            "timestamp": self.get_timestamp,
            "paymentId": payment_id
        }

        # PGW APIのPOSTパラメータ作成
        pgw_request_data = self.create_pgw_request_data(data)

        return self.request_pgw_api(request_url, pgw_request_data)

    def request_modify(self, payment_id, modified_amount):
        request_url = self.endpoint + "/Payment/V1/Modify"

        data = {
            "serviceId": self.service_id,
            "timestamp": self.get_timestamp,
            "paymentId": payment_id,
            "amount": modified_amount
        }

        # PGW APIのPOSTパラメータ作成
        pgw_request_data = self.create_pgw_request_data(data)

        return self.request_pgw_api(request_url, pgw_request_data)

    def request_3d_secure_enrollment_check(self, sub_service_id, enrollment_id, callback_url, amount, card_token):
        request_url = self.endpoint + "/3DSecureEnrollment/V1/Check"

        data = {
            "serviceId": self.service_id,
            "subServiceId": sub_service_id,
            "enrollmentId": enrollment_id,
            "timestamp": self.get_timestamp,
            "agencyCode": self.AGENCY_CODE,
            "callbackUrl": callback_url,
            "currencyCode": self.CURRENCY_CODE,
            "amount": amount,
            "cardToken": card_token
        }

        # PGW APIのPOSTパラメータ作成
        pgw_request_data = self.create_pgw_request_data(data)

        return self.request_pgw_api(request_url, pgw_request_data)

    def create_pgw_request_data(self, data):
        """
        PGW APIのリクエストパラメータを作成します
        :param data: リクエストパラメータの元情報
        :return: PGW APIのリクエストパラメータ
        """
        # JSON形式に変換
        request_data = json.dumps(data)

        # request_dataをBase64エンコードで暗号化する
        payment_info = self.create_payment_info(request_data)

        # request_dataをHMAC SHA256でハッシュ化する
        signature = self.create_signature(request_data)

        pgw_request_data = {
            "paymentinfo": payment_info,
            "signature": signature
        }
        return pgw_request_data

    @staticmethod
    def create_payment_info(pgw_request_params):
        """
        PGWリクエストパラメータをBase64エンコードで暗号化するメソッドです
        :param pgw_request_params: 暗号化を行うPGWリクエストパラメータ
        :return: payment_info
        """
        return base64.b64encode(pgw_request_params)

    def create_signature(self, pgw_request_params):
        """
        PGWリクエストパラメータをHMAC SHA256でハッシュ化するメソッドです
        :param pgw_request_params: ハッシュ化するPGWリクエストパラメータ
        :return: signature
        """
        return hmac.new(self.authentication_key, pgw_request_params, hashlib.sha256).hexdigest()

    def request_pgw_api(self, request_url, pgw_request_data):
        """
        PGW APIへリクエストを送信します。
        :param request_url: PGW APIの接続URL
        :param pgw_request_data: PGW APIのPOSTパラメータ
        :return: PGW APIのレスポンス情報
        """
        try:
            post_params = urllib.urlencode(pgw_request_data)
            pgw_request = urllib2.Request(request_url, post_params, self.REQUEST_HEADERS)
            pgw_response = urllib2.urlopen(pgw_request, timeout=float(self.timeout))
            pgw_result = pgw_response.read()

            # PGW専用ログにレスポンスを出力する
            logger.info(pgw_result)
        except Exception as e:
            logger.exception(e)
            raise e
        finally:
            if pgw_response:
                pgw_response.close()
        return pgw_result


@implementer(IPgwAPICommunicatorFactory)
class PgwAPICommunicatorFactory(object):
    """
    PGW APIクライアント PgwAPICommunicatorクラスを呼び出すための初期化処理を行うクラスです。
    """
    target = PgwAPICommunicator

    def __init__(self, config):
        self.settings = config.registry.settings
        self.authentication_key = self.settings.get('altair.pgw.authentication_key')
        self.endpoint = self.settings.get('altair.pgw.endpoint')
        self.service_id = self.settings.get('altair.pgw.service_id')
        self.timeout = self.settings.get('altair.pgw.timeout')

    def __call__(self):

        return self.target(
            authentication_key=self.authentication_key,
            endpoint=self.endpoint,
            service_id=self.service_id,
            timeout=self.timeout
        )


def includeme(config):
    factory = PgwAPICommunicatorFactory(config)
    config.registry.registerUtility(factory, IPgwAPICommunicatorFactory)

