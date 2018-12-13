# -*- coding:utf-8 -*-
import hashlib
import urllib
import urllib2
import logging
import codecs

from zope.interface import implementer
from .interfaces import IPointAPICommunicator, IPointAPICommunicatorFactory
from .exceptions import PointAPIError
from datetime import datetime

logger = logging.getLogger(__name__)


@implementer(IPointAPICommunicator)
class PointAPICommunicator(object):
    """
    ポイントAPIと通信を行うクライアントクラスです。
    request_XXXXXメソッドで各ポイントAPIの機能を呼び出して通信を行います。
    """
    def __init__(self, request_url, timeout, secret_key, shop_name, group_id, reason_id):
        self.request_url = request_url
        self.timeout = timeout
        self.secret_key = secret_key
        self.shop_name = shop_name
        self.group_id = group_id
        self.reason_id = reason_id

    def request_get_stdonly(self, easy_id):
        req_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        event = 'get-stdonly'

        # 署名用のキー作成
        params = self.convert_stg_param(easy_id) + \
            self.convert_stg_param(self.group_id) + \
            self.convert_stg_param(self.reason_id) + \
            self.convert_stg_param(req_time) + \
            event + \
            self.convert_stg_param(self.secret_key)
        confirmation_key = self.generate_key(params)

        req_values = {'easy_id': easy_id,
                      'group_id': self.group_id,
                      'reason_id': self.reason_id,
                      'req_time': req_time,
                      '__event': event,
                      'confirmation_key': confirmation_key}

        return self.request_point_api(req_values)

    def request_auth_stdonly(self, easy_id, auth_point, req_time):
        # モール以外のサービスは0を指定
        shop_id = '0'
        event = 'auth-stdonly'

        # 日本語が含まれたパラメータの文字コード変換実施
        shop_name = self.convert_char_code(self.shop_name)

        # 署名用のキー作成
        params = self.convert_stg_param(easy_id) + \
            self.convert_stg_param(auth_point) + \
            shop_id + \
            shop_name + \
            self.convert_stg_param(self.group_id) + \
            self.convert_stg_param(self.reason_id) + \
            self.convert_stg_param(req_time) + \
            event + \
            self.convert_stg_param(self.secret_key)
        confirmation_key = self.generate_key(params)

        req_values = {'easy_id': easy_id,
                      'auth_point': auth_point,
                      'shop_id': shop_id,
                      'shop_name': shop_name,
                      'group_id': self.group_id,
                      'reason_id': self.reason_id,
                      'req_time': req_time,
                      '__event': event,
                      'confirmation_key': confirmation_key}

        return self.request_point_api(req_values)

    def request_fix(self, easy_id, fix_point, unique_id, fix_id, req_time):
        event = 'fix'

        # 署名用のキー作成
        params = self.convert_stg_param(easy_id) + \
            self.convert_stg_param(fix_point) + \
            self.convert_stg_param(unique_id) + \
            self.convert_stg_param(fix_id) + \
            self.convert_stg_param(self.group_id) + \
            self.convert_stg_param(self.reason_id) + \
            self.convert_stg_param(req_time) + \
            event + \
            self.convert_stg_param(self.secret_key)
        confirmation_key = self.generate_key(params)

        req_values = {'easy_id': easy_id,
                      'fix_point': fix_point,
                      'unique_id': unique_id,
                      'fix_id': fix_id,
                      'group_id': self.group_id,
                      'reason_id': self.reason_id,
                      'req_time': req_time,
                      '__event': event,
                      'confirmation_key': confirmation_key}

        return self.request_point_api(req_values)

    def request_rollback(self, easy_id, unique_id):
        req_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        event = 'rollback'

        # 署名用のキー作成
        params = self.convert_stg_param(easy_id) + \
            self.convert_stg_param(unique_id) + \
            self.convert_stg_param(self.group_id) + \
            self.convert_stg_param(self.reason_id) + \
            self.convert_stg_param(req_time) + \
            event + \
            self.convert_stg_param(self.secret_key)
        confirmation_key = self.generate_key(params)

        req_values = {'easy_id': easy_id,
                      'unique_id': unique_id,
                      'group_id': self.group_id,
                      'reason_id': self.reason_id,
                      'req_time': req_time,
                      '__event': event,
                      'confirmation_key': confirmation_key}

        return self.request_point_api(req_values)

    @staticmethod
    def convert_char_code(param):
        """
        ポイントAPI側がEUC-JPの文字コードで処理を行うため
        日本語などのパラメータはEUC-JPに変換します。
        :param param: 文字コード変換を行うパラメータ
        :return: EUC-JPに変換されたパラメータ
        """
        return unicode(param, 'UTF-8').encode('EUC-JP')

    @staticmethod
    def convert_stg_param(param):
        """
        署名用のキーを作成するために各リクエストパラメータを文字列連結する。
        数字と文字列が混ざった場合にTypeErrorとなるため変換を行う。
        :return: str型に変換した文字列
        """
        return str(param)

    @staticmethod
    def generate_key(params):
        """
        confirmation_keyを除いた, 他の全パラメータとsecret keyを結合し、md5して生成される
        :param params: md5する文字列
        :return: md5で生成した文字列
        """
        return hashlib.md5(params).hexdigest()

    def request_point_api(self, req_values):
        """
        ポイントAPIへリクエストを送信します。
        :param req_values: POSTするパラメータ
        :return: ポイントAPIのレスポンスXML
        """
        try:
            response = None
            post_params = urllib.urlencode(req_values)
            request = urllib2.Request(self.request_url, post_params)
            response = urllib2.urlopen(request, timeout=float(self.timeout))
            result = response.read().replace('encoding="EUC-JP"', 'encoding="UTF-8"')
            logger.info(result)
        except Exception as e:
            logger.exception(e)
            raise PointAPIError('[PNT0001]failed to request Point API. request detail = {}'.format(req_values))
        finally:
            if response:
                response.close()
        return result


@implementer(IPointAPICommunicatorFactory)
class PointAPICommunicatorFactory(object):
    """
    ポイントAPIクライアント PointAPICommunicatorクラスを呼び出すための初期化処理を行うクラスです。
    """
    target = PointAPICommunicator

    def __init__(self, config):
        self.settings = config.registry.settings
        self.request_url = self.settings.get('altair.point.endpoint')
        self.timeout = self.settings.get('altair.point.timeout')
        self.secret_key = self.settings.get('altair.point.secret_key')

    def __call__(self, group_id, reason_id):
        shop_name = self.settings.get('altair.point.{group_id}.{reason_id}.shop_name'
                                      .format(group_id=group_id, reason_id=reason_id))
        return self.target(
            request_url=self.request_url,
            timeout=self.timeout,
            secret_key=self.secret_key,
            shop_name=shop_name,
            group_id=group_id,
            reason_id=reason_id
        )


def includeme(config):
    factory = PointAPICommunicatorFactory(config)
    config.registry.registerUtility(factory, IPointAPICommunicatorFactory)
