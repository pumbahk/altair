# encoding: utf-8
import base64
import logging

from pyramid.httpexceptions import HTTPForbidden

from altair.app.ticketing.authentication import IExternalMemberAuthCrypto
from altair.app.ticketing.authentication.plugins import TicketingKeyBaseAuthPlugin
from altair.auth.api import get_who_api, decide

logger = logging.getLogger(__name__)

EXTERNALMEMBER_AUTH_IDENTIFIER_NAME = 'externalmember'
EXTERNALMEMBER_ID_POLICY_NAME = 'externalmember_id'
EXTERNALMEMBER_EMAIL_ADDRESS_POLICY_NAME = 'externalmember_email_address'


class ExternalMemberAuthPlugin(TicketingKeyBaseAuthPlugin):
    name = EXTERNALMEMBER_AUTH_IDENTIFIER_NAME


class ExternalMemberAuthPredicate(object):
    """View Predicate Factory class corresponding to external_auth_param"""
    def __init__(self, val, config):
        self.val = val

    def text(self):
        return 'externalmember_auth_param = %s' % (self.val,)

    phash = text

    def __call__(self, context, request):
        # 外部会員番号取得キーワード認証が指定されていない場合は predicate 結果を False で返す
        auth_plugin_names = decide(request)
        if EXTERNALMEMBER_AUTH_IDENTIFIER_NAME not in auth_plugin_names:
            return False

        credential, res = self.get_credential(request)
        if res:
            api = get_who_api(request)
            identities, auth_factors, metadata = api.authenticate()
            if identities is None or identities.get(EXTERNALMEMBER_AUTH_IDENTIFIER_NAME) is None:
                # 外部会員番号取得キーワード認証されていないときのみ、新規の認証を試みる
                identities, headers, metadata, response = api.login(
                    credentials={EXTERNALMEMBER_AUTH_IDENTIFIER_NAME: credential}
                )
                if identities:  # 新規の認証に成功した場合
                    request.response.headers.update(headers)
                else:  # 新規の認証に失敗した場合は predicate 結果を False にする
                    res = False
        return res

    def get_credential(self, request):
        """
        認証に必要なパラメータをリクエストから取得して、全て取得できたかどうかの結果と共に返却します。
        リクエストパラメータは暗号化されているので、復号化して取得します
        """
        credential = {}
        res = True
        for k in self.val:
            data = request.POST.get(k)
            if data is None or data is u'':
                res = False
                break

            try:
                decoded = base64.b64decode(data)
                crypto = request.registry.getUtility(IExternalMemberAuthCrypto)
                credential[k] = crypto.decrypt(decoded)
            except Exception as e:
                logger.warn('Failed to decrypt %s: %s', data, e.message)
                raise HTTPForbidden()
        return credential, res
