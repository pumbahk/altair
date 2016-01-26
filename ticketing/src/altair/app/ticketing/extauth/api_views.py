import logging
from pyramid.view import view_defaults, view_config
from pyramid.httpexceptions import HTTPBadRequest, HTTPUnauthorized, HTTPInternalServerError, HTTPFound
from pyramid.compat import string_types
from pyramid.renderers import RendererHelper
from altair.httpsession.pyramid.interfaces import ISessionPersistenceBackendFactory
from altair.oauth.request import WebObOAuthRequestParser
from altair.oauth.api import get_oauth_provider, get_openid_provider
from altair.oauth.exceptions import OAuthBadRequestError, OAuthRenderableError, OAuthNoSuchAccessTokenError
from .utils import get_oauth_response_renderer
from .models import OAuthClient

logger = logging.getLogger(__name__)

oauth_request_parser = WebObOAuthRequestParser()
        
def invalidate_client_http_session(request, session_id):
    logger.debug('invalidating http session: %s' % session_id)
    persistence_backend_factory = request.registry.queryUtility(ISessionPersistenceBackendFactory)
    persistence_backend = persistence_backend_factory(request)
    persistence_backend.delete(session_id, {})

def verify_access_token(renderer):
    def _(fn):
        def _(context, request):
            provider = get_oauth_provider(request)
            auth_descriptor = None
            access_token = None
            try:
                access_token = oauth_request_parser.get_access_token(request)
            except:
                pass
            if access_token is not None:
                try:
                    auth_descriptor = provider.get_auth_descriptor_by_token(access_token)
                except OAuthNoSuchAccessTokenError:
                    def render(response):
                        _renderer = renderer
                        if isinstance(_renderer, string_types):
                            _renderer = RendererHelper(name=_renderer)
                        attrs = getattr(request, '__dict__', {})
                        if '__view__' in attrs:
                            view_inst = attrs.pop('__view__')
                        else:
                            view_inst = getattr(fn, '__original_view__', fn)
                        return _renderer.render_view(request, response, view_inst, context)
                    request.response.status = 401
                    return render({
                        u'error': u'invalid_request',
                        u'error_description': u'invalid access token',
                        u'message': u'invalid access token'
                        })
                if auth_descriptor is None:
                    logger.debug('no corresponding auth descriptor for access_token=%s' % access_token)
            else:
                logger.debug('access token is not provided')
            if auth_descriptor is None:
                return HTTPUnauthorized('no access token provided')
            request.auth_descriptor = auth_descriptor
            return fn(context, request)
        return _
    return _

@view_defaults(renderer='json')
class APIView(object):
    def __init__(self, context, request):
         self.context = context
         self.request = request

    @view_config(route_name='extauth.api.issue_oauth_access_token')
    def issue_oauth_access_token(self):
        state = oauth_request_parser.get_state(self.request)
        try:
            client_id, client_secret = oauth_request_parser.get_client_credentials(self.request)
            params = oauth_request_parser.parse_issue_access_token_request(self.request)
        except OAuthBadRequestError:
            logger.exception('bad request')
            self.request.response.status = 400
            retval = {}
            if state is not None:
                retval[u'state'] = state
            return retval
        provider = get_oauth_provider(self.request)
        openid_provider = get_openid_provider(self.request)
        try:
            auth_descriptor = provider.issue_access_token(client_id=client_id, client_secret=client_secret, **params)
            authenticated_at = auth_descriptor['identity'].pop('authenticated_at', None)
            id_token = openid_provider.issue_id_token(
                client_id=client_id,
                identity=auth_descriptor['identity'],
                authenticated_at=authenticated_at,
                aux={ 'http_session_id': auth_descriptor['identity'].get('http_session_id') }
                )
        except OAuthRenderableError as e:
            self.request.response.status = e.http_status
            return get_oauth_response_renderer(self.request).render_exc_as_dict(e)
        renderer = get_oauth_response_renderer(self.request)
        result = renderer.render_auth_descriptor_as_dict(auth_descriptor, state)
        result.update(renderer.render_id_token_as_dict(id_token))
        return result

    @view_config(route_name='extauth.api.revoke_oauth_access_token', request_method='DELETE')
    def revoke_oauth_access_token(self):
        try:
            client_id, client_secret = oauth_request_parser.get_client_credentials(self.request)
        except OAuthBadRequestError:
            logger.exception('bad request')
            self.request.response.status = 400
            return {}
        provider = get_oauth_provider(self.request)
        try:
            access_token = self.request.matchdict['access_token']
            auth_descriptor = provider.get_auth_descriptor_by_token(access_token)
            provider.revoke_access_token(client_id=client_id, client_secret=client_secret, access_token=access_token)
            client = provider.validated_client(client_id, client_secret)
            if isinstance(client, OAuthClient):
                if client.organization.invalidate_client_http_session_on_access_token_revocation:
                    http_session_id = auth_descriptor['identity']['http_session_id']
                    if http_session_id is not None:
                        invalidate_client_http_session(self.request, http_session_id) 
        except OAuthRenderableError as e:
            self.request.response.status = e.http_status
            return get_oauth_response_renderer(self.request).render_exc_as_dict(e)
        return {}

    @view_config(route_name='extauth.api.openid_end_session', request_method='GET')
    def openid_end_session(self):
        try:
            client_id, client_secret = oauth_request_parser.get_client_credentials(self.request)
        except OAuthBadRequestError:
            logger.exception('bad request')
            self.request.response.status = 400
            return {}
        try:
            try:
                id_token = self.request.GET['id_token']
            except KeyError:
                raise OAuthBadRequestError('id_token is not given')
            openid_provider = get_openid_provider(self.request)
            authn_descriptor = provider.get_authn_descriptor_by_id_token(id_token)
            openid_provider.revoke_id_token(client_id, id_token)
            http_session_id = authn_descriptor['aux']['http_session_id']
            if http_session_id is not None:
                invalidate_client_http_session(self.request, http_session_id) 
        except OAuthRenderableError as e:
            self.request.response.status = e.http_status
            return get_oauth_response_renderer(self.request).render_exc_as_dict(e)
        except OAuthNoSuchAccessTokenError:
            self.request.response.status = 404
            return {}
        return {}


    @view_config(route_name='extauth.api.v0.user', decorator=(verify_access_token('json'),))
    def user(self):
        return self.request.auth_descriptor['identity']
