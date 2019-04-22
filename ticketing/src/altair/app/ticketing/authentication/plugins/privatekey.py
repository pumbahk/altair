# encoding: utf-8

from altair.app.ticketing.authentication.plugins import TicketingKeyBaseAuthPlugin
from altair.auth.api import get_who_api, decide

PRIVATEKEY_AUTH_IDENTIFIER_NAME = 'privatekey'


class PrivateKeyAuthPlugin(TicketingKeyBaseAuthPlugin):
    name = PRIVATEKEY_AUTH_IDENTIFIER_NAME


class PrivateKeyAuthPredicate(object):
    """View Predicate Factory class corresponding to privatekey_auth_param"""
    def __init__(self, val, config):
        self.val = val

    def text(self):
        return 'privatekey_auth_param = %s' % (self.val,)

    phash = text

    def __call__(self, context, request):
        # キーワード認証が指定されていない場合は predicate 結果を False で返す
        auth_plugin_names = decide(request)
        if PRIVATEKEY_AUTH_IDENTIFIER_NAME not in auth_plugin_names:
            return False

        keyword = request.POST.get(self.val)
        if not keyword:
            return False  # キーワード認証が指定されているのに、キーワードがない

        api = get_who_api(request)
        identities, auth_factors, metadata = api.authenticate()  # 現在の認証状態を取得
        if identities is not None and identities.get(PRIVATEKEY_AUTH_IDENTIFIER_NAME) is not None:
            return True  # 既に認証済み

        # 新規認証
        identities, headers, metadata, response = api.login(
            credentials={PRIVATEKEY_AUTH_IDENTIFIER_NAME: {self.val: keyword}}
        )
        if identities:
            request.response.headers.update(headers)
            return True  # 新規認証成功
        else:
            return False  # 新規認証失敗
