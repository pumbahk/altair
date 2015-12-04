import logging
from zope.interface import implementer
from .interfaces import IOAuthProvider
from .exceptions import (
    OAuthAccessDeniedError,
    OAuthNoSuchAccessTokenError,
    OAuthInvalidScopeError,
    OAuthClientNotFound,
    OAuthInvalidSecretError,
    OAuthServerError,
    OAuthNoSuchAuthorizationCodeError,
    )

logger = logging.getLogger(__name__)

@implementer(IOAuthProvider)
class OAuthProvider(object):
    CODE_GENERATION_MAX_RETRY = 10

    def __init__(self, client_repository, scope_manager, now_getter, code_store, code_generator, access_token_store, access_token_generator, refresh_token_store, refresh_token_generator):
        self.client_repository = client_repository
        self.scope_manager = scope_manager
        self.now_getter = now_getter
        self.code_store = code_store
        self.code_generator = code_generator
        self.access_token_store = access_token_store
        self.access_token_generator = access_token_generator
        self.refresh_token_store = refresh_token_store
        self.refresh_token_generator = refresh_token_generator

    def validate_scope(self, scope):
        for scope_item in scope:
            if not self.scope_manager.exists(scope_item):
                raise OAuthInvalidScopeError(u'invalid scope item: {scope_item}'.format(scope_item=scope_item))

    def validated_client(self, client_id, client_secret):
        client = self.client_repository.lookup(client_id, self.now_getter())
        if client is None:
            raise OAuthClientNotFound(client_id)
        if client_secret is not None:
            if not client.validate_secret(client_secret):
                raise OAuthInvalidSecretError()
        return client

    def _generate_authorization_code(self):
        for _ in range(self.CODE_GENERATION_MAX_RETRY):
            code = self.code_generator()
            if code not in self.code_store:
                break
        else:
            raise OAuthServerError()
        return code

    def _generate_access_token(self):
        for _ in range(self.CODE_GENERATION_MAX_RETRY):
            token = self.access_token_generator()
            if token not in self.access_token_store:
                break
        else:
            raise OAuthServerError()
        return token

    def _generate_refresh_token(self):
        for _ in range(self.CODE_GENERATION_MAX_RETRY):
            token = self.refresh_token_generator()
            if token not in self.refresh_token_store:
                break
        else:
            raise OAuthServerError()
        return token

    def grant_authorization_code(self, client_id, redirect_uri=None, scope=None, identity=None):
        client = self.validated_client(client_id, None)
        if scope is not None:
            scope = set(scope)
            self.validate_scope(scope)
            if not (client.authorized_scope & scope):
                raise OAuthAccessDeniedError(u'scope error')
        else:
            scope = client.authorized_scope
        if redirect_uri is not None:
            if not client.validate_redirect_uri(redirect_uri):
                raise OAuthAccessDeniedError(u'redirect_uri does not match')
        code = self._generate_authorization_code()
        self.code_store[code] = {
            'client_id': client_id,
            'redirect_uri': redirect_uri,
            'scope': list(scope),
            'identity': identity,
            }
        return code

    def issue_access_token(self, code, client_id, client_secret=None, token_type=u'bearer', redirect_uri=None, aux=None):
        now = self.now_getter()
        authreq_descriptor = self._get_authreq_descriptor_by_code(code)
        if authreq_descriptor['client_id'] != client_id:
            logger.info('client_id does not match (%s != %s)' % (client_id, authreq_descriptor['client_id']))
            raise OAuthNoSuchAuthorizationCodeError(u'client_id does not match')
        if authreq_descriptor['redirect_uri'] != redirect_uri:
            logger.info('redirect_uri does not match (%s != %s)' % (redirect_uri, authreq_descriptor['redirect_uri']))
            raise OAuthNoSuchAuthorizationCodeError(u'redirect_uri does not match')
        client = self.validated_client(client_id, client_secret)
        auth_descriptor = {
            'client_id': client_id,
            'scope': list(authreq_descriptor['scope']),
            'token_type': token_type,
            'identity': authreq_descriptor['identity'],
            }
        access_token = self._generate_access_token()
        auth_descriptor['access_token'] = access_token
        auth_descriptor['access_token_expire_at'] = ((now + self.access_token_store.expiration_time) if self.access_token_store.expiration_time is not None else None)
        refresh_token = None
        refresh_token_expire_in = None
        if self.refresh_token_store is not None:
            refresh_token = self._generate_refresh_token()
            refresh_token_expire_in = self.refresh_token_store.expiration_time
        auth_descriptor['refresh_token'] = refresh_token
        auth_descriptor['refresh_token_expire_at'] = ((now + refresh_token_expire_in) if refresh_token_expire_in is not None else None)
        auth_descriptor['aux'] = dict(aux) if aux is not None else {}
        self.access_token_store[access_token] = auth_descriptor
        if self.refresh_token_store is not None:
            self.refresh_token_store[refresh_token] = auth_descriptor
        try:
            del self.code_store[code]
        except:
            logger.warning('failed to invalidate authorization code: %s' % code)
        return auth_descriptor

    def revoke_access_token(self, client_id, client_secret, access_token):
        client = self.validated_client(client_id, client_secret)
        try:
            auth_descriptor = self.access_token_store[access_token]
        except KeyError:
            raise OAuthNoSuchAccessTokenError(access_token)
        if auth_descriptor['client_id'] != client_id:
            logger.info('client_id does not match (%s != %s)' % (client_id, auth_descriptor['client_id']))
            raise OAuthNoSuchAuthorizationCodeError(u'client_id does not match')
        del self.access_token_store[access_token]

    def _get_authreq_descriptor_by_code(self, code):
        try:
            return self.code_store[code]
        except KeyError:
            raise OAuthNoSuchAuthorizationCodeError(u'authorization code is not the one granted from the provider')

    def get_identity_by_code(self, code):
        return _get_authreq_descriptor_by_code(code)['identity']

    def get_auth_descriptor_by_token(self, access_token):
        try:
            return self.access_token_store[access_token]
        except KeyError:
            raise OAuthNoSuchAccessTokenError(access_token)
