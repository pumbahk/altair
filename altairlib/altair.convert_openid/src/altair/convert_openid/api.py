# -*- coding:utf-8 -*-
import urllib2
import logging

from zope.interface import implementer
from .interfaces import IOpenIDConverterFactory
from .exceptions import ConverterAPIError, EasyIDNotFoundError
from xml.etree import ElementTree

logger = logging.getLogger(__name__)


def convert_openid_to_easyid(request, openid):
    """
    get_easyidメソッドを呼び出し、対象のOpenIDをEasyIDに変換して返却します。
    :param request:
    :param openid:
    :return: easyid(openidから変換した結果)
    """
    converter = request.registry.getUtility(IOpenIDConverterFactory)
    # openidからeasyidを取得する
    easyid = converter.get_easyid(openid)
    return easyid


def converter_api_setting(config):
    settings = config.registry.settings

    endpoint = settings.get('altair.converter_openid.endpoint')
    timeout = settings.get('altair.converter_openid.timeout')
    timeout = timeout and int(timeout) or None

    return OpenIDConverterFactory(
        endpoint=endpoint,
        timeout=timeout
    )


@implementer(IOpenIDConverterFactory)
class OpenIDConverterFactory(object):
    """
    OpenID -> EasyIDへの転換APIへ接続するクライアントクラスです。
    get_easyidメソッドよりOpenIDを渡せばEasyIDを返却します。
    """
    def __init__(self, endpoint, timeout):
        self.endpoint = endpoint
        self.timeout = timeout

    def get_easyid(self, openid):
        request_url = self.endpoint + openid

        for _ in range(3):  # リトライ処理(最大3回実行)
            try:
                response = None
                response = urllib2.urlopen(request_url, timeout=self.timeout)
                result = response.read()

                # response check
                logger.debug('converter API result log : %s', result)
                result_tree = ElementTree.fromstring(result)
                easyid = result_tree.find('easyId').text
            except Exception as e:
                pass
            else:  # try処理が成功した場合
                if easyid is None:
                    raise EasyIDNotFoundError('[OID0002]failed to get the target EasyID. openid = {}'.format(openid))
                return easyid
            finally:
                if response:
                    response.close()
        else:  # リトライしても全て失敗した場合
            logger.exception(e.message)
            raise ConverterAPIError('[OID0001]failed to request OpenID converter API. openid = {}'.format(openid))


def includeme(config):
    factory = converter_api_setting(config)
    config.registry.registerUtility(factory, IOpenIDConverterFactory)
