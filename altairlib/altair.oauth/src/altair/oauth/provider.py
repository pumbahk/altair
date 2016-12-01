# encoding: UTF-8
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
        authorized_scope = set(client.authorized_scope)
        if scope is not None:
            scope = set(scope)
            self.validate_scope(scope)
            if not (authorized_scope & scope):
                raise OAuthAccessDeniedError(u'scope error')
        else:
            scope = authorized_scope
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

    def _is_using_rakuten_fanclub(self, request):
        import distutils.util
        use_fanclub = distutils.util.strtobool(request.params.get('use_fanclub', 'True'))
        return request.organization.fanclub_api_available and use_fanclub

    def _retrieved_member_kinds(self, request):
        retrieved_profile = request.session['retrieved']
        member_kinds = {
            membership['kind']['id']: membership['kind']['name']
            for membership in retrieved_profile['memberships']
            }
        return member_kinds

    def validate_authz_request(self, request, authenticator_name):
        from pyramid.httpexceptions import HTTPBadRequest
        if authenticator_name == 'internal' or \
                (authenticator_name == 'rakuten' and self._is_using_rakuten_fanclub(request)):
            try:
                member_kind_id_str = request.params['member_kind_id']
                membership_id = request.params['membership_id']
            except KeyError as e:
                raise HTTPBadRequest('missing parameter: %s' % e.message)
            try:
                member_kind_id = int(member_kind_id_str)
            except (TypeError, ValueError):
               raise HTTPBadRequest('invalid parameter: member_kind_id')
            member_kinds = self._retrieved_member_kinds(request)
            if member_kind_id not in member_kinds:
                raise HTTPBadRequest('invalid parameter: member_kind_id')
            return True
        elif authenticator_name == 'pollux':
            try:
                member_kind_name = request.params['member_kind_name']
            except KeyError as e:
                raise HTTPBadRequest('missing parameter: %s' % e.message)
            retrieved_member_kinds = self._retrieved_member_kinds(request)
            # FIXME: 会員資格文字列で正当性検証するのは微妙
            if member_kind_name not in retrieved_member_kinds.values():
                raise HTTPBadRequest('invalid parameter: member_kind_name')
            return True
        return False

    def build_identity(self, request, id_, authenticator_name):
        if authenticator_name == 'internal' or \
                (authenticator_name == 'rakuten' and self._is_using_rakuten_fanclub(request)):
            membership_id = request.params['membership_id']
            member_kind_id = int(request.params['member_kind_id'])
            member_kinds = self._retrieved_member_kinds(request)
            return dict(
                id=id_,
                profile=request.altair_auth_metadata,
                member_kind=dict(
                    id=request.params['membership_id'],
                    name=member_kinds[member_kind_id]
                    ),
                membership_id=membership_id
            )
        elif authenticator_name == 'rakuten' and not self._is_using_rakuten_fanclub(request):
            # fanclubAPIが無効(=False)な場合は一般ユーザーという固定値をfanclubコース名の代わりに与える
            # この名称をORGごとに変えたいという要件が出てきた場合はDBから取得するように実装を変更してください
            return dict(
                id=id_,
                profile=request.altair_auth_metadata,
                member_kind=dict(name=u'一般ユーザー'),
                membership_id=id_
            )
        elif authenticator_name == 'pollux':
            member_kind_name = request.params['member_kind_name']
            return dict(
                id=id_,
                profile=request.altair_auth_metadata,
                member_kind=dict(name=member_kind_name),
                membership_id=id_
            )
        return None
