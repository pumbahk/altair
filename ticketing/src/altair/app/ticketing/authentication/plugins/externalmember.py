# encoding: utf-8
import base64
import logging

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

        credential = self.get_credential(request)
        if not credential:
            return False  # 外部会員番号取得キーワード認証が指定されているのに、認証に必要な情報がない

        api = get_who_api(request)
        identities, auth_factors, metadata = api.authenticate()  # 現在の認証状態を取得
        if identities is not None and identities.get(EXTERNALMEMBER_AUTH_IDENTIFIER_NAME) is not None:
            return True  # 既に認証済み

        # 新規認証
        identities, headers, metadata, response = api.login(
            credentials={EXTERNALMEMBER_AUTH_IDENTIFIER_NAME: credential}
        )
        if identities:
            request.response.headers.update(headers)
            return True  # 新規認証成功
        else:
            return False  # 新規認証失敗

    def get_credential(self, request):
        """
        認証に必要なパラメータをリクエストから取得して返却します。
        リクエストパラメータは暗号化されているので、復号化して取得します
        """
        keyword = self.decrypt(request, 'keyword')
        member_id = self.decrypt(request, 'member_id')
        # keyword (認証のキー) & member_id (会員番号) は必須です
        if not keyword or not member_id:
            return None

        return {
            'keyword': keyword,
            'member_id': member_id,
            'email_address': self.decrypt(request, 'email_address')
        }

    def decrypt(self, request, key):
        val = request.POST.get(key)
        try:
            if val:
                decoded = base64.b64decode(val)
                crypto = request.registry.getUtility(IExternalMemberAuthCrypto)
                return crypto.decrypt(decoded)
        except Exception as e:
            logger.warn('Failed to decrypt %s: %s', val, e.message)
        return None
