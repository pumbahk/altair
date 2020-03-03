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
from contextlib import closing

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
                          card_token, cvv_token, email, is_three_d_secure_authentication_result,
                          message_version=None, cavv_algorithm=None, cavv=None,
                          eci=None, transaction_id=None, transaction_status=None):
        """
        PGWのAuthorizeAPIと通信します
        :param sub_service_id: 店舗ID
        :param payment_id: 予約番号(cart:order_no, lots:entry_no)
        :param gross_amount: 決済総額
        :param card_token: カードトークン
        :param cvv_token: セキュリティコードトークン
        :param email: Eメールアドレス
        :param is_three_d_secure_authentication_result: 3DSのレスポンス可否
        :param message_version: 3DSecure message version
        :param cavv_algorithm: 3DSecure CAVV algorithm
        :param cavv: 3DSecure CAVV
        :param eci: 3DSecure ECI
        :param transaction_id: 3DSecure transaction identifier (XID)
        :param transaction_status: 3DSecure transaction status
        :return: PGWからのAPIレスポンス
        """
        request_url = self.endpoint + "/Payment/V1/Authorize"

        request_data = {
            "serviceId": self.service_id,
            "subServiceId": self._convert_str_param(sub_service_id),
            "timestamp": self.get_timestamp,
            "paymentId": self._convert_str_param(payment_id),
            "agencyCode": self.AGENCY_CODE,
            "currencyCode": self.CURRENCY_CODE,
            "grossAmount": int(gross_amount),
            "order": {
                "version": self.ORDER_VERSION,
                "email": self._convert_str_param(email),
                "ipAddress": self.get_ip_address
            }
        }

        # 3DSecure認証済みの場合
        if is_three_d_secure_authentication_result:
            request_data.update({
                "cardToken": {
                    "version": self.CARD_TOKEN_VERSION,
                    "amount": int(gross_amount),
                    "cardToken": self._convert_str_param(card_token),
                    "cvvToken": self._convert_str_param(cvv_token),
                    "withThreeDSecure": self.WITH_THREE_D_SECURE,
                    "threeDSecureAuthenticationResult": {
                        "messageVersion": self._convert_str_param(message_version),
                        "cavvAlgorithm": self._convert_str_param(cavv_algorithm),
                        "cavv": self._convert_str_param(cavv),
                        "eci": self._convert_str_param(eci),
                        "transactionId": self._convert_str_param(transaction_id),
                        "transactionStatus": self._convert_str_param(transaction_status)
                    }
                }
            })
        else:
            request_data.update({
                "cardToken": {
                    "version": self.CARD_TOKEN_VERSION,
                    "amount": int(gross_amount),
                    "cardToken": self._convert_str_param(card_token),
                    "cvvToken": self._convert_str_param(cvv_token),
                    "withThreeDSecure": self.WITH_THREE_D_SECURE
                }
            })

        return self._request_pgw_api(request_url, request_data)

    def request_capture(self, payment_id, capture_amount):
        """
        PGWのCaptureAPIと通信します
        :param payment_id: 予約番号(cart:order_no, lots:entry_no)
        :param capture_amount: キャプチャする決済金額
        :return: PGWからのAPIレスポンス
        """
        request_url = self.endpoint + "/Payment/V1/Capture"

        request_data = {
            "serviceId": self.service_id,
            "timestamp": self.get_timestamp,
            "paymentId": self._convert_str_param(payment_id),
            "amount": int(capture_amount)
        }

        return self._request_pgw_api(request_url, request_data)

    def request_authorize_and_capture(self, sub_service_id, payment_id, gross_amount,
                                      card_token, cvv_token, email, is_three_d_secure_authentication_result,
                                      message_version=None, cavv_algorithm=None, cavv=None,
                                      eci=None, transaction_id=None, transaction_status=None):
        """
        PGWのAuthorizeAndCaptureAPIと通信します
        :param sub_service_id: 店舗ID
        :param payment_id: 予約番号(cart:order_no, lots:entry_no)
        :param gross_amount: 決済総額
        :param card_token: カードトークン
        :param cvv_token: セキュリティコードトークン
        :param email: Eメールアドレス
        :param is_three_d_secure_authentication_result: 3DSのレスポンス可否
        :param message_version: 3DSecure message version
        :param cavv_algorithm: 3DSecure CAVV algorithm
        :param cavv: 3DSecure CAVV
        :param eci: 3DSecure ECI
        :param transaction_id: 3DSecure transaction identifier (XID)
        :param transaction_status: 3DSecure transaction status
        :return: PGWからのAPIレスポンス
        """
        request_url = self.endpoint + "/Payment/V1/AuthorizeAndCapture"

        request_data = {
            "serviceId": self.service_id,
            "subServiceId": self._convert_str_param(sub_service_id),
            "timestamp": self.get_timestamp,
            "paymentId": self._convert_str_param(payment_id),
            "agencyCode": self.AGENCY_CODE,
            "currencyCode": self.CURRENCY_CODE,
            "grossAmount": int(gross_amount),
            "order": {
                "version": self.ORDER_VERSION,
                "email": self._convert_str_param(email),
                "ipAddress": self.get_ip_address
            }
        }

        # 3DSecure認証済みの場合
        if is_three_d_secure_authentication_result:
            request_data.update({
                "cardToken": {
                    "version": self.CARD_TOKEN_VERSION,
                    "amount": int(gross_amount),
                    "cardToken": self._convert_str_param(card_token),
                    "cvvToken": self._convert_str_param(cvv_token),
                    "withThreeDSecure": self.WITH_THREE_D_SECURE,
                    "threeDSecureAuthenticationResult": {
                        "messageVersion": self._convert_str_param(message_version),
                        "cavvAlgorithm": self._convert_str_param(cavv_algorithm),
                        "cavv": self._convert_str_param(cavv),
                        "eci": self._convert_str_param(eci),
                        "transactionId": self._convert_str_param(transaction_id),
                        "transactionStatus": self._convert_str_param(transaction_status)
                    }
                }
            })
        else:
            request_data.update({
                "cardToken": {
                    "version": self.CARD_TOKEN_VERSION,
                    "amount": int(gross_amount),
                    "cardToken": self._convert_str_param(card_token),
                    "cvvToken": self._convert_str_param(cvv_token),
                    "withThreeDSecure": self.WITH_THREE_D_SECURE
                }
            })

        return self._request_pgw_api(request_url, request_data)

    def request_find(self, payment_ids, search_type=None):
        """
        PGWのFindAPIと通信します
        :param payment_ids: 予約番号リスト(cart:order_no, lots:entry_no)
        :param search_type: 検索タイプ
        :return: PGWからのAPIレスポンス
        """
        request_url = self.endpoint + "/Payment/V1/Find"

        request_data = {
            "serviceId": self.service_id,
            "timestamp": self.get_timestamp,
            "searchType": self._convert_str_param(search_type) if search_type is not None else self.DEFAULT_SEARCH_TYPE,
            "paymentIds": map(str, payment_ids) if type(payment_ids) == 'list' else self._convert_str_param(payment_ids)
        }

        return self._request_pgw_api(request_url, request_data)

    def request_cancel_or_refund(self, payment_id):
        """
        PGWのCancelOrRefundAPIと通信します
        :param payment_id: 予約番号(cart:order_no, lots:entry_no)
        :return: PGWからのAPIレスポンス
        """
        request_url = self.endpoint + "/Payment/V1/CancelOrRefund"

        request_data = {
            "serviceId": self.service_id,
            "timestamp": self.get_timestamp,
            "paymentId": self._convert_str_param(payment_id)
        }

        return self._request_pgw_api(request_url, request_data)

    def request_modify(self, payment_id, modified_amount):
        """
        PGWのModifyAPIと通信します
        :param payment_id: 予約番号(cart:order_no, lots:entry_no)
        :param modified_amount: 変更後の決済金額
        :return: PGWからのAPIレスポンス
        """
        request_url = self.endpoint + "/Payment/V1/Modify"

        request_data = {
            "serviceId": self.service_id,
            "timestamp": self.get_timestamp,
            "paymentId": self._convert_str_param(payment_id),
            "amount": int(modified_amount)
        }

        return self._request_pgw_api(request_url, request_data)

    def request_3d_secure_enrollment_check(self, sub_service_id, enrollment_id, callback_url, amount, card_token):
        """
        PGWの3DSecureEnrollmentCheckAPIと通信します
        :param sub_service_id: 店舗ID
        :param enrollment_id: 3DSecure認証用ID(予約番号)(cart:order_no, lots:entry_no)
        :param callback_url: コールバックURL
        :param amount: 決済予定金額
        :param card_token: カードトークン
        :return: PGWからのAPIレスポンス
        """
        request_url = self.endpoint + "/3DSecureEnrollment/V1/Check"

        request_data = {
            "serviceId": self.service_id,
            "subServiceId": self._convert_str_param(sub_service_id),
            "enrollmentId": self._convert_str_param(enrollment_id),
            "timestamp": self.get_timestamp,
            "agencyCode": self.AGENCY_CODE,
            "callbackUrl": self._convert_str_param(callback_url),
            "currencyCode": self.CURRENCY_CODE,
            "amount": int(amount),
            "cardToken": self._convert_str_param(card_token)
        }

        return self._request_pgw_api(request_url, request_data)

    @staticmethod
    def _convert_str_param(param):
        """
        リクエストパラメータをJSON化する際にTypeErrorを防ぐため文字列に変換する
        :return: str型に変換した文字列
        """
        return str(param)

    def _create_pgw_request_data(self, data):
        """
        PGW APIのリクエストパラメータを作成します
        :param data: リクエストパラメータの元情報
        :return: PGW APIのリクエストパラメータ
        """
        # JSON形式に変換
        request_data = json.dumps(data)

        # request_dataをBase64エンコードで暗号化する
        payment_info = self._create_payment_info(request_data)

        # request_dataをHMAC SHA256でハッシュ化する
        signature = self._create_signature(request_data)

        pgw_request_data = {
            "paymentinfo": payment_info,
            "signature": signature
        }
        return pgw_request_data

    @staticmethod
    def _create_payment_info(pgw_request_params):
        """
        PGWリクエストパラメータをBase64エンコードで暗号化するメソッドです
        :param pgw_request_params: 暗号化を行うPGWリクエストパラメータ
        :return: payment_info
        """
        return base64.b64encode(pgw_request_params)

    def _create_signature(self, pgw_request_params):
        """
        PGWリクエストパラメータをHMAC SHA256でハッシュ化するメソッドです
        :param pgw_request_params: ハッシュ化するPGWリクエストパラメータ
        :return: signature
        """
        return hmac.new(self.authentication_key, pgw_request_params, hashlib.sha256).hexdigest()

    def _request_pgw_api(self, request_url, request_data):
        """
        PGW APIへリクエストを送信します。
        :param request_url: PGW APIの接続URL
        :param request_data: PGW APIのリクエスト元データ
        :return: PGW APIのレスポンス情報
        """
        # PGW APIのPOSTパラメータ作成
        pgw_request_data = self._create_pgw_request_data(request_data)

        try:
            post_params = urllib.urlencode(pgw_request_data)
            pgw_request = urllib2.Request(request_url, post_params, self.REQUEST_HEADERS)
            opener = urllib2.build_opener(urllib2.HTTPSHandler())
            urllib2.install_opener(opener)
            with closing(urllib2.urlopen(pgw_request, timeout=float(self.timeout))) as pgw_response:
                pgw_result = pgw_response.read()

                # PGW専用ログにレスポンスを出力する
                logger.info('PGW request URL = {url}, PGW result = {result}'.format(url=request_url, result=pgw_result))

                # JSONをdict形式に変換する
                pgw_dict = json.loads(pgw_result)
        except Exception as e:
            logger.exception(e)
            raise e
        return pgw_dict


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

