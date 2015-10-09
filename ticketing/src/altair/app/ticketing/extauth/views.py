import logging
import re
from datetime import datetime
from urlparse import urljoin, urlparse
from urllib import urlencode, quote
from pyramid.view import view_defaults
from pyramid.httpexceptions import HTTPBadRequest, HTTPInternalServerError, HTTPFound

from altair.pyramid_dynamic_renderer.config import lbr_view_config, lbr_notfound_view_config
from altair.auth.api import get_plugin_registry
from altair.auth.pyramid import challenge_view
from altair.oauth.api import get_oauth_provider, get_openid_provider
from altair.oauth.request import WebObOAuthRequestParser
from altair.oauth.exceptions import OAuthRenderableError, OpenIDAccountSelectionRequired, OpenIDLoginRequired
from altair.rakuten_auth.openid import RakutenOpenID
from .rendering import selectable_renderer
from .rakuten_auth import get_openid_claimed_id
from .api import get_communicator
from .utils import get_oauth_response_renderer

logger = logging.getLogger(__name__)

def extract_identifer(request):
    for authenticator_name, identity in request.authenticated_userid.items():
        plugin_registry = get_plugin_registry(request)
        authenticator = plugin_registry.lookup(authenticator_name)
        if isinstance(authenticator, RakutenOpenID):
            return identity['claimed_id']
    return u'urn:eagles:soc:0000000'

class RakutenIDView(object):
    oauth_request_parser = WebObOAuthRequestParser()

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @lbr_view_config(
        route_name='extauth.rakuten.index',
        renderer=selectable_renderer('index.mako'),
        request_method='GET'
        )
    def index(self):
        try:
            provider = get_oauth_provider(self.request)
            state = self.oauth_request_parser.get_state(self.request)
            oauth_params = self.oauth_request_parser.parse_grant_authorization_code_request(self.request)
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
            prompt = re.split(ur'\s+', aux.get('prompt', 'select_account'))
            if 'altair.auth.authenticator:rakuten' in self.request.effective_principals:
                if 'login' not in prompt:
                    request.session.delete()
                    return challenge_view(self.context, self.request)
            else:
                if 'none' in prompt:
                    raise OpenIDLoginRequired()
                return challenge_view(self.context, self.request)
            self.request.session['oauth_params'] = oauth_params
            openid_claimed_id = get_openid_claimed_id(self.request)
            if openid_claimed_id is not None:
                data = get_communicator(self.request).get_user_profile(openid_claimed_id)
                self.request.session['retrieved'] = data
                if len(data['memberships']) == 1:
                    return HTTPFound(
                        location=self.request.route_path(
                            'extauth.rakuten.login',
                            _query=dict(
                                member_kind_id=data['memberships'][0]['kind']['id'],
                                membership_id=data['memberships'][0]['membership_id']
                                )
                            ),
                        )
                elif len(data['memberships']) > 1:
                    if 'select_account' not in prompt:
                        raise OpenIDAccountSelectionRequired()
                return data
            else:
                raise HTTPInternalServerError()
        except OAuthRenderableError as e:
            logger.exception('oops')
            raise HTTPFound(
                location=urljoin(
                    oauth_params['redirect_uri'],
                    '?' + get_oauth_response_renderer(self.request).render_exc_as_urlencoded_params(e, state)
                    )
                )

    @lbr_view_config(route_name='extauth.rakuten.login', permission='rakuten')
    def login(self):
        try:
            member_kind_id_str = self.request.params['member_kind_id']
            membership_id = self.request.params['membership_id']
        except KeyError as e:
            raise HTTPBadRequest('missing parameter: %s' % e.message)
        try:
            member_kind_id = int(member_kind_id_str)
        except (TypeError, ValueError):
            raise HTTPBadRequest('invalid parameter: member_kidn_id')
        retrieved_profile = self.request.session['retrieved']
        member_kinds = {
            membership['kind']['id']: membership['kind']['name']
            for membership in retrieved_profile['memberships']
            }
        if member_kind_id not in member_kinds:
            raise HTTPBadRequest('invalid parameter: member_kind_id')
        provider = get_oauth_provider(self.request)
        oauth_params = dict(self.request.session['oauth_params'])
        state = oauth_params.pop('state')
        id_ = extract_identifer(self.request)
        identity = dict(
            id=id_,
            profile=self.request.altair_auth_metadata,
            member_kind=dict(
                id=member_kind_id,
                name=member_kinds[member_kind_id]
                ),
            membership_id=membership_id
            )
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
    route_name='extauth.reset_and_continue',
    request_method='GET'
    )
def reset_and_continue(context, request):
    path = request.application_url + u'/' + u'/'.join(request.matchdict['path']) + u'?' + request.query_string
    request.session.delete()
    return HTTPFound(location=path)


@lbr_notfound_view_config(
    renderer=selectable_renderer('notfound.mako'),
    append_slash=True
    )
def notfound(context, request):
    return {}


