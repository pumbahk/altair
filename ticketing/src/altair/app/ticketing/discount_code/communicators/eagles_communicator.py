# encoding: UTF-8

import json
import logging
import hashlib
import requests
import six
from datetime import datetime
from zope.interface import implementer
from .interfaces import ICommunicator

logger = logging.getLogger(__name__)

@implementer(ICommunicator)
class EaglesCommunicator(object):
    def __init__(self, endpoint_base, client_name, hash_key, hash_key_extauth, proxies=None, request_charset='utf-8', timeout=None):
        self.endpoint_base = endpoint_base
        self.client_name = client_name
        self.proxies = proxies
        self.hash_key = hash_key
        self.hash_key_extauth = hash_key_extauth
        self.request_charset = request_charset
        self.timeout = timeout or 600

    def _get_next_year(self):
        return six.text_type(datetime.now().year + 1)

    def _create_token(self, data, hash_key=None):
        h = hashlib.sha224()
        h.update(data)
        h.update(self.client_name)
        h.update(hash_key or self.hash_key)
        return six.text_type(h.hexdigest())

    def _request(self, method, url, data):
        logger.info(data)
        with requests.Session() as s:
            resp = s.request(
                method=method,
                url=url,
                data=data,
                headers={
                    'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',
                    'Connection': 'close'
                },
                verify=False,
                proxies=self.proxies,
                timeout=self.timeout
            )

        logger.info(resp)
        # 現時点はレスポンスのデータタイプがJSONのみを予想してる
        # TODO レスポンスのデータタイプをチェックする
        # TODO 連結失敗などの例外処理を追加する
        return resp.json()

    def _parse_content_type(self, resp):
        content_type = resp.header.get('content-type', None)
        if content_type:
            mime_type, charset = content_type.split(';')
            return mime_type, charset
        else:
            return None, None

    def get_fc_member_id(self, open_id):
        """
        open_id = "https://myid.rakuten.co.jp/openid/user/rNmPCzshCVbzC2SulpKTnGlWg=="
        """
        token = self._create_token(open_id, hash_key=self.hash_key_extauth)
        post_data = {
            "open_id": open_id,
            "client_name": self.client_name,
            "token": token,
            "start_year": self._get_next_year(),
            "end_year": self._get_next_year(),
            'ticket_only': 1,
            'is_eternal': 1
        }
        url = self.endpoint_base + "/members-check"
        resp_data = self._request('POST', url, post_data)

        return resp_data

    def _discount_code_common_method(self, url_suffix, data):
        first_token = data['coupons'][0]['coupon_cd']
        token = self._create_token(first_token)

        json_data = json.dumps(data)

        if url_suffix == "/coupon/confirm/status":
            data_key = 'confirmation_condition'
        elif url_suffix == "/coupon/use":
            data_key = 'usage_coupons'
        elif url_suffix == "/coupon/cancel/used":
            data_key = 'used_coupons'
        else:
            raise ValueError('url_suffix is not set correctly.')

        post_data = {
            "client_name": self.client_name,
            "token": token,
            data_key: json_data
        }

        url = self.endpoint_base + url_suffix
        resp_data = self._request('POST', url, post_data)

        return resp_data

    def confirm_discount_code_status(self, data):
        """
        data = {
            'usage_type': '1010',
            'fc_member_id': '1222984',
            'coupons': [{'coupon_cd': 'EQWM7RFA7AGT'},{'coupon_cd': 'EEQT7CY7WP74'},{'coupon_cd': 'EEQTW3X3Q9LN'}]
        }
        """
        resp_data = self._discount_code_common_method(url_suffix="/coupon/confirm/status", data=data)
        return resp_data

    def use_discount_code(self, data):
        """
        data = {
            'usage_type': '1010',
            'fc_member_id': '1222984',
            'coupons': [{'coupon_cd': 'EQWM7RFA7AGT'},{'coupon_cd': 'EEQT7CY7WP74'},{'coupon_cd': 'EEQTW3X3Q9LN'}]
        }
        """
        resp_data = self._discount_code_common_method(url_suffix="/coupon/use", data=data)
        return resp_data

    def cancel_used_discount_code(self, data):
        """
        data = {
            'usage_type': '1010',
            'coupons': [{'coupon_cd': 'EQWM7RFA7AGT'},{'coupon_cd': 'EEQT7CY7WP74'},{'coupon_cd': 'EEQTW3X3Q9LN'}]
        }
        """
        resp_data = self._discount_code_common_method(url_suffix="/coupon/cancel/used", data=data)
        return resp_data