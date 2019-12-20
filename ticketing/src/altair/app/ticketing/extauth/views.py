# encoding: UTF-8
import logging
import sys
import re
import urllib2
import distutils.util
from datetime import datetime
from urlparse import urljoin, urlparse
from urllib import urlencode, quote
from pyramid.view import view_defaults
from pyramid.events import subscriber
from pyramid.httpexceptions import HTTPBadRequest, HTTPInternalServerError, HTTPFound, HTTPForbidden
from pyramid.security import Authenticated, forget
from pyramid.session import check_csrf_token
from sqlalchemy.orm.exc import NoResultFound

from altair.pyramid_dynamic_renderer.config import lbr_view_config, lbr_notfound_view_config
from altair.auth.api import get_plugin_registry, get_auth_api, get_who_api
from altair.oauth.api import get_oauth_provider, get_openid_provider
from altair.oauth.request import WebObOAuthRequestParser
from altair.oauth.exceptions import OAuthRenderableError, OAuthBadRequestError, OpenIDAccountSelectionRequired, OpenIDLoginRequired
from altair.rakuten_auth.openid import RakutenOpenID
from altair.fanclub_auth.plugin import FanclubAuthPlugin
from altair.exclog.api import log_exception_message, build_exception_message
from altair.sqlahelper import get_db_session
from redis.exceptions import ResponseError
from .rendering import selectable_renderer
from .rakuten_auth import get_openid_claimed_id, get_open_id_for_sso
from .api import get_communicator
from .utils import get_oauth_response_renderer
from .models import MemberKind, MemberSet, Member
from .internal_auth import InternalAuthPlugin
from .helpers import Helpers
from .exceptions import GenericError

logger = logging.getLogger(__name__)


class RedisResponseError(Exception):
    def __init__(self, msg):
        self.msg = msg


class URLopenTimeoutError(Exception):
    def __init__(self, msg):
        self.msg = msg


class OAuthError(Exception):
    def __init__(self, msg):
        self.msg = msg


def extract_identifer(request):
    retval = None
    for authenticator_name, identity in request.authenticated_userid.items():
        plugin_registry = get_plugin_registry(request)
        authenticator = plugin_registry.lookup(authenticator_name)
        if isinstance(authenticator, RakutenOpenID):
            # if the session is authenticated both by RakutenOpenID and InternalAuth, then
            # InternalAuth will take precedence.
            retval = identity['claimed_id'], authenticator_name
        if isinstance(authenticator, FanclubAuthPlugin):
            retval = identity['pollux_member_id'], authenticator_name
        elif isinstance(authenticator, InternalAuthPlugin):
            retval = u'acct:%s+%s@%s' % (
                quote(identity.get('auth_identifier') or u'*'),
                quote(identity['member_set']),
                quote(identity['host_name'])
                ), authenticator_name
            break
    return retval

JUST_AUTHENTICATED_KEY = '%s.just_authenticated' % __name__

def rakuten_auth_challenge_succeeded(request, plugin, identity, metadata):
    request.session[JUST_AUTHENTICATED_KEY] = True

def challenge_service_provider(request, challenger_name):
    api = get_who_api(request)
    response = HTTPForbidden()
    if api.challenge(response=response, challenger_name=challenger_name):
        return response
    else:
        logger.error('WTF?')
        raise HTTPInternalServerError()

class OAuthParamsReceiver(object):
    def __init__(self, oauth_request_parser):
        self.oauth_request_parser = oauth_request_parser

    def __call__(self, fn):
        def _(context, request):
            logger.debug('oauth request parser: {}'.format(request.url))
            def _has_oauth_params(params):
                oauth_params_keys = ['scope', 'client_id', 'state', 'authenticated_at', 'aux',
                                     'max_age', 'nonce', 'prompt', 'response_type', 'redirect_uri']
                for param in params.keys():
                    if param in oauth_params_keys:
                        return True
                return False

            if _has_oauth_params(request.params) or 'oauth_params' not in request.session:
                oauth_params = None
                try:
                    oauth_params = self.oauth_request_parser.parse_grant_authorization_code_request(request)
                    provider = get_oauth_provider(request)
                    state = self.oauth_request_parser.get_state(request)
                    if oauth_params['scope'] is not None:
                        provider.validate_scope(oauth_params['scope'])
                    provider.validated_client(oauth_params['client_id'], None)
                    oauth_params['state'] = state
                    oauth_params['authenticated_at'] = datetime.now()
                    aux = oauth_params.pop('aux')
                    max_age = aux.get('max_age')
                    if max_age is not None:
                        try:
                            max_age = int(max_age)
                        except (TypeError, ValueError):
                            raise HTTPBadRequest('invalid max_age value')
                    oauth_params['max_age'] = max_age
                    oauth_params['nonce'] = aux.get('nonce')
                    oauth_params['prompt'] = re.split(ur'\s+', aux.get('prompt', 'select_account'))
                    request.session['oauth_params'] = oauth_params
                except ResponseError as e:
                    logger.warn(str(e))
                    raise RedisResponseError(e.message)
                except OAuthBadRequestError as e:
                    logger.warn(str(e))
                    raise OAuthError(str(e))
                except OAuthRenderableError as e:
                    logger.exception('oops')
                    if oauth_params is not None:
                        raise HTTPFound(
                            location=urljoin(
                                oauth_params['redirect_uri'],
                                '?' + get_oauth_response_renderer(request).render_exc_as_urlencoded_params(e, state)
                                )
                            )
                    else:
                        return HTTPInternalServerError(e.message)
            return fn(context, request)
        return _

receives_oauth_params = OAuthParamsReceiver(WebObOAuthRequestParser())


def require_oauth_params_in_session(fn):
    def _(context, request):
        if 'oauth_params' not in request.session:
            raise HTTPBadRequest()
        return fn(context, request)
    return _


@view_defaults(http_cache=0)
class View(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def navigate_to_select_account(self):
        oauth_params = self.request.session['oauth_params']
        data = self.request.session['retrieved']

        if len(data['memberships']) == 1:
            return HTTPFound(
                location=self.request.route_path(
                    'extauth.authorize',
                    subtype=self.context.subtype,
                    _query=dict(
                        _=self.request.session.get_csrf_token(),
                        member_kind_id=data['memberships'][0]['kind']['id'],
                        membership_id=data['memberships'][0]['membership_id']
                        )
                    ),
            )
        elif len(data['memberships']) > 1:
            if 'select_account' not in oauth_params['prompt']:
                raise OpenIDAccountSelectionRequired()
        elif len(data['memberships']) == 0:
            raise HTTPFound(location=self.request.route_path('extauth.no_valid_memberships', subtype=self.context.subtype))
        return HTTPFound(location=self.request.route_path('extauth.select_account', subtype=self.context.subtype))

    def navigate_to_select_account_rakuten_auth(self):
        openid_claimed_id = get_openid_claimed_id(self.request)
        if openid_claimed_id is not None:
            try:
                data = get_communicator(self.request, self.request.organization.fanclub_api_type).get_user_profile(openid_claimed_id)
            except urllib2.URLError as e:
                logger.error(str(e))
                raise URLopenTimeoutError(str(e))
            except GenericError as e:
                logger.info('get_user_profile failed: %r' % e)
                data = None
            if data is None:
                return HTTPFound(
                    location=self.request.route_path(
                        'extauth.unknown_user',
                        subtype=self.context.subtype
                        )
                    )
            logger.debug('retrieved=%r' % data)
            self.request.session['retrieved'] = data
            return self.navigate_to_select_account()
        else:
            logger.error('openid_claimed_id is None')
            raise HTTPInternalServerError()

    @lbr_view_config(
        route_name='extauth.entry',
        renderer=selectable_renderer('index.mako'),
        request_method='GET',
        decorator=(receives_oauth_params, )
        )
    def entry(self):
        # usersideからextauthへのリクエストにあるSPを指定するパラメタをセッションに格納して使いまわす
        if self.request.params.get('service_providers'):
            self.request.session['service_providers'] = self.request.params.get('service_providers').split(',')
        oauth_params = self.request.session['oauth_params']
        logger.debug('the state for now is: {}'.format(oauth_params['state']))
        principals = self.request.effective_principals
        if Authenticated in principals:
            if u'login' in oauth_params['prompt']:
                self.request.response.headers.update(forget(self.request))
            elif u'altair.auth.authenticator:rakuten' in principals:
                return self.navigate_to_select_account_rakuten_auth()

        return dict(oauth_service_providers=self.context.visible_oauth_service_providers)

    @lbr_view_config(
        route_name='extauth.rakuten.entry',
        request_method='GET',
        decorator=(receives_oauth_params, )
        )
    def rakuten_entry(self):
        oauth_params = self.request.session['oauth_params']
        logger.debug('the state for now is: {}'.format(oauth_params['state']))
        logger.debug('effective_principals: {}'.format(self.request.effective_principals))

        # リクエストの Cookie から暗号化された Open ID を復号化して取得する
        open_id = get_open_id_for_sso(self.request)
        if open_id is not None:
            # Open ID が取得できた場合は SSO ログインを試みる TKT-9043
            from altair.rakuten_auth import AUTH_PLUGIN_NAME, SSO_IDENTITY
            credentials = {SSO_IDENTITY: {'claimed_id': open_id}}
            auth_api = get_auth_api(self.request)
            identities, _, _ = auth_api.login(self.request, self.request.response, credentials,
                                              auth_factor_provider_name=AUTH_PLUGIN_NAME)
            if identities:  # SSO 認証成功の場合
                return self._rakuten_sso_entry()

        if 'altair.auth.authenticator:rakuten' in self.request.effective_principals:
            if self.request.session.get(JUST_AUTHENTICATED_KEY, False):
                del self.request.session[JUST_AUTHENTICATED_KEY]
            else:
                if 'login' in oauth_params['prompt']:
                    self.request.response.headers.update(forget(self.request))
                    return challenge_service_provider(self.request, 'rakuten')
        else:
            if 'none' in oauth_params['prompt']:
                raise OpenIDLoginRequired()
            return challenge_service_provider(self.request, 'rakuten')

        # fanclubのコースチェックを行うparameter。存在しない場合はdefault True
        if self.request.organization.fanclub_api_available:
            use_fanclub = distutils.util.strtobool(self.request.params.get('use_fanclub', 'True'))
        else:
            use_fanclub = False

        # fanclubを利用するORGはコースチェックへ、しないORGはauthorizeへ
        if self.request.organization.fanclub_api_available and use_fanclub:
            return self.navigate_to_select_account_rakuten_auth()
        else:
            return HTTPFound(
                location=self.request.route_path(
                    'extauth.authorize',
                    subtype=self.context.subtype,
                    _query=dict(
                        _=self.request.session.get_csrf_token(),
                        use_fanclub=use_fanclub
                        )
                    ),
            )

    def _rakuten_sso_entry(self):
        if self.request.organization.fanclub_api_available and \
                distutils.util.strtobool(self.request.params.get('use_fanclub', 'True')):
            # EAGLES/Visselファンクラブログインの場合は会員情報取得へ移動
            return self.navigate_to_select_account_rakuten_auth()
        else:
            # 通常の楽天ログインの場合は認証結果確認へ移動
            # csrf token 確認が必要なので、Header に追加する
            csrf_token = self.request.session.get_csrf_token()
            self.request.headers['X-CSRF-Token'] = csrf_token
            return self.authorize()

    @lbr_view_config(
        route_name='extauth.fanclub.entry',
        request_method='GET',
        decorator=(receives_oauth_params, )
        )
    def fanclub_entry(self):
        oauth_params = self.request.session['oauth_params']
        if 'altair.auth.authenticator:pollux' in self.request.effective_principals:
            if self.request.session.get(JUST_AUTHENTICATED_KEY, False):
                del self.request.session[JUST_AUTHENTICATED_KEY]
            else:
                if 'login' in oauth_params['prompt']:
                    self.request.response.headers.update(forget(self.request))
                    # XXX:polluxで認証するときはどのfanclubで認証するのか特定する必要がある
                    self.request.session['service_provider_name'] = self.context.challenge_service_provider_name
                    return challenge_service_provider(self.request, 'pollux')
        else:
            if 'none' in oauth_params['prompt']:
                raise Exception('not implemented')
            # XXX:polluxで認証するときはどのfanclubで認証するのか特定する必要がある
            self.request.session['service_provider_name'] = self.context.challenge_service_provider_name
            return challenge_service_provider(self.request, 'pollux')

        # TODO: 複数会員資格が返ってきたときはイーグルスみたいに選ばせる必要がある
        def normalize_received_data(received_data):
                norm_data = {}
                norm_data['memberships'] = [dict(
                    membership_id=None,
                    kind=dict(
                        id=index,
                        name=data.get('membership_name')
                    )
                ) for index, data in enumerate(received_data)]
                return norm_data

        data = normalize_received_data(self.request.altair_auth_metadata['memberships'])
        self.request.session['retrieved'] = data
        if len(data['memberships']) == 0:
            return HTTPFound(location=self.request.route_path('extauth.no_valid_memberships', subtype=self.context.subtype))
        elif len(data['memberships']) > 1 and u'select_account' in oauth_params['prompt']:
            return HTTPFound(location=self.request.route_path('extauth.select_account', subtype=self.context.subtype))
        return HTTPFound(
                location=self.request.route_path(
                    'extauth.authorize',
                    subtype=self.context.subtype,
                    _query=dict(
                        _=self.request.session.get_csrf_token(),
                        member_kind_name=data['memberships'][0]['kind']['name']
                        )
                    ),
            )

    @lbr_view_config(
        route_name='extauth.select_account',
        renderer=selectable_renderer('select_account.mako'),
        permission='authenticated'
        )
    def select_account(self):
        data = self.request.session['retrieved']

        if len(data['memberships']) == 1:
            return HTTPFound(
                location=self.request.route_path(
                    'extauth.authorize',
                    subtype=self.context.subtype,
                    _query=dict(
                        _=self.request.session.get_csrf_token(),
                        member_kind_id=data['memberships'][0]['kind']['id'],
                        membership_id=data['memberships'][0]['membership_id']
                        )
                    ),
                )
        else:
            membership_ids = set(membership['membership_id'] for membership in data['memberships'])
            data = dict(data, membership_ids_are_the_same=(len(membership_ids) == 1))
        return data

    @lbr_view_config(route_name='extauth.authorize', permission='authenticated')
    def authorize(self):
        check_csrf_token(self.request, '_')
        
        provider = get_oauth_provider(self.request)
        oauth_params = dict(self.request.session['oauth_params'])
        logger.debug('the state for now is: {}'.format(oauth_params['state']))
        state = oauth_params.pop('state')
        id_, authenticator_name = extract_identifer(self.request)

        # raise error if something goes wrong.
        provider.validate_authz_request(self.request, authenticator_name)

        identity = provider.build_identity(self.request, id_, authenticator_name)
        if identity is None:
            raise OAuthBadRequestError('could not build identity')

        nonce = oauth_params.pop('nonce')
        max_age = oauth_params.pop('max_age')
        authenticated_at = oauth_params.pop('authenticated_at')
        openid_provider = get_openid_provider(self.request)
        identity.update(
            openid_provider.handle_authentication_request(
                subject_id=id_,
                nonce=nonce,
                max_age=max_age
                ),
            authenticated_at=authenticated_at,
            http_session_id=self.request.session.id
            )
        code = provider.grant_authorization_code(
            identity=identity,
            client_id=oauth_params['client_id'],
            redirect_uri=oauth_params['redirect_uri'],
            scope=oauth_params['scope']
            )
        return HTTPFound(
            location=urljoin(
                oauth_params['redirect_uri'],
                '?' + get_oauth_response_renderer(self.request).render_authorization_code_as_urlencoded_params(code, state)
                )
            )

    @lbr_view_config(
        route_name='extauth.login',
        renderer=selectable_renderer('login.mako'),
        request_method='GET',
        decorator=(require_oauth_params_in_session,)
        )
    def login_form(self):
        dbsession = get_db_session(self.request, 'extauth_slave')
        member_set_name = self.request.GET[u'member_set']
        try:
            member_set = dbsession.query(MemberSet).filter_by(
                organization_id=self.request.organization.id,
                name=member_set_name
                ).one()
        except NoResultFound:
            return HTTPBadRequest('invalid member_set')
        if Authenticated in self.request.effective_principals:
            self.request.response.headers.update(forget(self.request))
        return dict(
            selected_member_set=member_set,
            username=u'',
            password=u'',
            message=None
            )

    @lbr_view_config(
        route_name='extauth.login',
        renderer=selectable_renderer('login.mako'),
        request_method='POST',
        decorator=(require_oauth_params_in_session,)
        )
    def login(self):
        check_csrf_token(self.request, '_')
        member_set_name = self.request.POST[u'member_set']
        guest_login = None
        for k in self.request.POST:
            if isinstance(k, bytes):
                k = k.decode("UTF-8")
            if k.startswith(u'doGuestLoginAs'):
                guest_login = k[14:]
        dbsession = get_db_session(self.request, 'extauth_slave')
        try:
            member_set = dbsession.query(MemberSet).filter_by(
                organization_id=self.request.organization.id,
                name=member_set_name
                ).one()
        except NoResultFound:
            return HTTPBadRequest('invalid member_set')
        if guest_login is None:
            username = self.request.POST[u'username']
            password = self.request.POST[u'password']
            credentials = dict(
                member_set=member_set.name,
                auth_identifier=username,
                auth_secret=password
                )
            auth_api = get_auth_api(self.request)
            identities, auth_factors, metadata = auth_api.login(self.request, self.request.response, credentials, auth_factor_provider_name='internal')
            if 'internal' not in identities:
                helpers = Helpers(self.request)
                return dict(
                    selected_member_set=member_set,
                    username=username,
                    password=password,
                    message=(self.request.translate(u'{}または{}が違います')).format(
                        helpers.auth_identifier_field_name(member_set), helpers.auth_secret_field_name(member_set)
                    )
                )
            else:
                member = dbsession.query(Member).filter_by(id=identities['internal']['member_id']).one()
                valid_memberships = member.query_valid_memberships(self.request.now)
                if not valid_memberships:
                    self.request.response.headers.update(forget(self.request))
                    return dict(
                        selected_member_set=member_set,
                        username=username,
                        password=password,
                        message=u'ログインできません'
                        )
                account_data = dict(
                    memberships=[
                        dict(
                            membership_id=membership.membership_identifier,
                            displayed_membership_id=membership.membership_identifier,
                            kind=dict(
                                id=membership.member_kind.id,
                                name=membership.member_kind.name
                                )
                            )
                        for membership in member.valid_memberships
                        ]
                    )
                self.request.session['retrieved'] = account_data
                return self.navigate_to_select_account()
        else:
            try:
                member_kind = dbsession.query(MemberKind) \
                    .filter_by(member_set_id=member_set.id,
                               name=guest_login) \
                    .one()
            except NoResultFound:
                raise HTTPBadRequest('invalid member_kind')
            credentials = dict(
                member_set=member_set.name,
                member_kind=member_kind.name,
                guest=True
                )
            auth_api = get_auth_api(self.request)
            identities, auth_factors, metadata = auth_api.login(self.request, self.request.response, credentials, auth_factor_provider_name='internal')
            if 'internal' not in identities:
                return dict(
                    selected_member_set=member_set,
                    username=u'',
                    password=u'',
                    message=u'現在ゲストログインはできなくなっております'
                    )
            else:
                account_data = dict(
                    memberships=[
                        dict(
                            membership_id=None,
                            displayed_membership_id=None,
                            kind=dict(
                                id=member_kind.id,
                                name=member_kind.name
                                )
                            )
                        ]
                    )
                self.request.session['retrieved'] = account_data
                return HTTPFound(
                    location=self.request.route_path(
                        'extauth.authorize',
                        subtype=self.context.subtype,
                        _query=dict(
                            _=self.request.session.get_csrf_token(),
                            member_kind_id=member_kind.id,
                            membership_id=None
                            )
                        )
                    )

    @lbr_view_config(
        route_name='extauth.unknown_user',
        renderer=selectable_renderer('unknown.mako'),
        request_method='GET',
        permission='authenticated'
        )
    def unknown_user(self):
        return dict()

    @lbr_view_config(
        route_name='extauth.no_valid_memberships',
        renderer=selectable_renderer('no_valid_memberships.mako'),
        request_method='GET',
        permission='authenticated'
        )
    def no_valid_memberships(self):
        return dict()


@lbr_view_config(route_name='extauth.logout')
def logout(context, request):
    headers = forget(request)
    return HTTPFound(
        location=request.route_path(
            'extauth.entry',
            subtype=context.subtype
            ),
        headers=headers
        )

@lbr_view_config(
    route_name='extauth.reset_and_continue',
    request_method='GET'
    )
def reset_and_continue(context, request):
    path = request.application_url + u'/' + u'/'.join(request.matchdict['path']) + u'?' + request.query_string
    headers = forget(self.request)
    request.session.delete()
    return HTTPFound(location=path, headers=headers)


@lbr_notfound_view_config(
    renderer=selectable_renderer('notfound.mako'),
    append_slash=True
    )
def notfound(context, request):
    return {}


@lbr_view_config(
        context=RedisResponseError,
        renderer=selectable_renderer("redis_response_error.mako")
        )
def redis_response_error(exception, request):
    return {}


@lbr_view_config(
    context=URLopenTimeoutError,
    renderer=selectable_renderer('urlopen_timeout_error.mako'),
    )
def urlopen_timeout_error(exception, request):
    log_exception_message(request, *build_exception_message(request))
    return {}


@lbr_view_config(
    context=OAuthError,
    renderer=selectable_renderer('oauth_error.mako'),
    )
def oauth_error(exception, request):
    return {}


@lbr_view_config(
    context=Exception,
    renderer=selectable_renderer('fatal.mako'),
    )
def fatal(exception, request):
    log_exception_message(request, *build_exception_message(request))
    return {}
