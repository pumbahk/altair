import logging
from urlparse import urljoin, urlparse
from urllib import urlencode, quote
from pyramid.view import view_defaults
from pyramid.httpexceptions import HTTPBadRequest, HTTPInternalServerError, HTTPFound

from altair.pyramid_dynamic_renderer.config import lbr_view_config, lbr_notfound_view_config
from altair.auth.api import get_plugin_registry
from altair.oauth.api import get_oauth_provider
from altair.oauth.request import WebObOAuthRequestParser
from altair.oauth.exceptions import OAuthBadRequestError, OAuthRenderableError
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

@view_defaults(permission='rakuten')
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
        provider = get_oauth_provider(self.request)
        state = self.oauth_request_parser.get_state(self.request)
        try:
            dict_ = self.oauth_request_parser.parse_grant_authorization_code_request(self.request)
        except OAuthBadRequestError as e:
            raise HTTPBadRequest(e.message)
        try:
            if dict_['scope'] is not None:
                provider.validate_scope(dict_['scope'])
            provider.validated_client(dict_['client_id'], None)
        except OAuthRenderableError as e:
            raise HTTPFound(
                location=urljoin(
                    dict_['redirect_uri'],
                    '?' + get_oauth_response_renderer(self.request).render_exc_as_urlencoded_params(e, state)
                    )
                )
        dict_['state'] = state
        self.request.session['oauth_params'] = dict_
        openid_claimed_id = get_openid_claimed_id(self.request)
        if openid_claimed_id is not None:
            data = get_communicator(self.request).get_user_profile(openid_claimed_id)
            self.request.session['retrieved'] = data
            return data
        else:
            raise HTTPInternalServerError()

    @lbr_view_config(route_name='extauth.rakuten.login')
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
        params = dict(self.request.session['oauth_params'])
        state = params.pop('state')
        identity = dict(
            id=extract_identifer(self.request),
            profile=self.request.altair_auth_metadata,
            member_kind=dict(
                id=member_kind_id,
                name=member_kinds[member_kind_id]
                ),
            membership_id=membership_id
            )
        code = provider.grant_authorization_code(identity=identity, **params)
        return HTTPFound(
            location=urljoin(
                params['redirect_uri'],
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
