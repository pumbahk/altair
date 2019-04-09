# coding=utf-8
import base64
import logging

from pyramid.httpexceptions import HTTPFound, HTTPForbidden

from altair.auth.api import get_who_api

from .interfaces import IExternalMemberAuthCrypto
from .plugins.externalmember import EXTERNALMEMBER_AUTH_IDENTIFIER_NAME
from .plugins.privatekey import PRIVATEKEY_AUTH_IDENTIFIER_NAME

logger = logging.getLogger(__name__)


class TicketingKeyBaseAuthView(object):
    def __init__(self, request, identifier_name, additional_credential_param=None):
        self.request = request
        self.identifier_name = identifier_name
        self.additional_credential_param = additional_credential_param or ()

    def __call__(self):
        self.introduce_authentication(self.identifier_name, self.additional_credential_param)
        return HTTPFound(self.request.current_route_path())

    def get_credential(self, param_name):
        return self.request.POST.get(param_name)

    def introduce_authentication(self, identifier_name, additional_credential_param=None):
        credential_dict = {
            'key': self.get_credential('keyword')
        }
        credential_dict.update({
            k: self.get_credential(k) for k in additional_credential_param or ()
        })
        if all([v is not None and v is not u'' for k, v in credential_dict.items()]):
            api = get_who_api(self.request)
            identities, auth_factors, metadata = api.authenticate()
            if identities is None or identities.get(identifier_name) is None:
                # POSTでかつキーワード認証されていないときのみ、新規の認証を試みる
                identities, headers, metadata, response = api.login(
                    credentials={identifier_name: credential_dict}
                )
                if identities:
                    self.request.response.headers.update(headers)


class PrivateKeyAuthView(TicketingKeyBaseAuthView):
    def __init__(self, request):
        super(PrivateKeyAuthView, self).__init__(request, PRIVATEKEY_AUTH_IDENTIFIER_NAME)


class ExternalMemberAuthView(TicketingKeyBaseAuthView):
    def __init__(self, request):
        super(ExternalMemberAuthView, self).__init__(request,
                                                     EXTERNALMEMBER_AUTH_IDENTIFIER_NAME,
                                                     ('email_address', 'member_id'))

    def get_credential(self, param_name):
        """リクエストパラメータは暗号化されているので、復号化して取得します"""
        data = self.request.POST.get(param_name)
        if not data:
            return data

        try:
            decoded = base64.b64decode(data)
            crypto = self.request.registry.getUtility(IExternalMemberAuthCrypto)
            return crypto.decrypt(decoded)
        except Exception as e:
            logger.warn('Failed to decrypt %s: %s', data, e.message)
            raise HTTPForbidden()
