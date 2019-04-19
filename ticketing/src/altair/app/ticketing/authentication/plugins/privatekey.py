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
        res = False
        if keyword:
            api = get_who_api(request)
            identities, auth_factors, metadata = api.authenticate()
            if identities is None or identities.get(PRIVATEKEY_AUTH_IDENTIFIER_NAME) is None:
                # キーワード認証されていないときのみ、新規の認証を試みる
                identities, headers, metadata, response = api.login(
                    credentials={PRIVATEKEY_AUTH_IDENTIFIER_NAME: {self.val: keyword}}
                )
                if identities:  # 新規の認証に成功した場合
                    request.response.headers.update(headers)
                    res = True
            else:
                res = True
        return res
