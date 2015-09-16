import logging
from pyramid.view import view_defaults, view_config
from pyramid.httpexceptions import HTTPBadRequest, HTTPUnauthorized, HTTPInternalServerError, HTTPFound
from altair.oauth.request import WebObOAuthRequestParser
from altair.oauth.api import get_oauth_provider
from altair.oauth.exceptions import OAuthBadRequestError, OAuthRenderableError
from .utils import get_oauth_response_renderer

logger = logging.getLogger(__name__)

oauth_request_parser = WebObOAuthRequestParser()

def verify_access_token(fn):
    def _(context, request):
        provider = get_oauth_provider(request)
        auth_descriptor = None
        access_token = None
        try:
            access_token = oauth_request_parser.get_access_token(request)
        except:
            pass
        if access_token is not None:
            auth_descriptor = provider.get_auth_descriptor_by_token(access_token)
            if auth_descriptor is None:
                logger.debug('no corresponding auth descriptor for access_token=%s' % access_token)
        else:
            logger.debug('access token is not provided')
        if auth_descriptor is None:
            return HTTPUnauthorized('no access token provided')
        request.auth_descriptor = auth_descriptor
        return fn(context, request)
    return _

@view_defaults(renderer='json')
class APIView(object):
    def __init__(self, context, request):
         self.context = context
         self.request = request

    @view_config(route_name='extauth.api.oauth_access_token')
    def oauth_access_token(self):
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
        try:
            auth_descriptor = provider.issue_access_token(client_id=client_id, client_secret=client_secret, **params)
        except OAuthRenderableError as e:
            self.request.response.status = e.http_status
            return get_oauth_response_renderer(self.request).render_exc_as_dict(e)
        return get_oauth_response_renderer(self.request).render_auth_descriptor_as_dict(auth_descriptor, state)

    @view_config(route_name='extauth.api.v0.user', decorator=(verify_access_token,))
    def user(self):
        return self.request.auth_descriptor['identity']
