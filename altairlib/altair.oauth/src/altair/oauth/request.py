import re
import sys
import six
import logging
from .exceptions import OAuthBadRequestError
from base64 import b64decode

logger = logging.getLogger(__name__)

class WebObOAuthRequestParser(object):
    def get_state(self, request):
        state = None
        if 'state' in request.GET:
            state = request.GET.pop('state')
        return state

    def parse_grant_authorization_code_request(self, request):
        try:
            if 'response_type' in request.GET:
                if request.GET.getone('response_type') != 'code':
                    raise OAuthBadRequestError('response_type != "code"')
            client_id = request.GET.getone('client_id')
            redirect_uri = request.GET.getone('redirect_uri')
            scope = None
            if 'scope' in request.GET:
                scope = request.GET.getone('scope')
                if scope:
                    scope = set(re.split(ur'\s+', scope))
                else:
                    scope = None
        except KeyError as e:
            raise OAuthBadRequestError('missing parameter: %s' % e.message)
        return dict(
            client_id=client_id,
            redirect_uri=redirect_uri,
            scope=scope
            )

    def parse_issue_access_token_request(self, request):
        try:
            if 'grant_type' in request.POST:
                if request.POST.getone('grant_type') != 'authorization_code':
                    raise OAuthBadRequestError('grant_type != "authorization_code"')
            code = request.POST.getone('code')
            redirect_uri = request.POST.getone('redirect_uri')
        except KeyError as e:
            raise OAuthBadRequestError('missing parameter: %s' % e.message)
        return dict(
            code=code,
            redirect_uri=redirect_uri
            )

    def get_client_credentials(self, request):
        try:
            authz = request.authorization
            client_id = client_secret = None
            if authz is not None:
                type = authz[0]
                params = authz[1]
                _client_id, _, _client_secret = b64decode(params).partition(':')
                client_id = six.text_type(_client_id)
                client_secret = six.text_type(_client_secret)
            elif 'client_id' in request.GET:
                client_id = request.GET.pop('client_id')
                client_secret = request.GET.pop('client_secret')
            elif 'client_id' in request.POST:
                client_id = request.POST.pop('client_id')
                client_secret = request.POST.pop('client_secret')
            else:
                raise OAuthBadRequestError(u'no client credentials provided')
            return client_id, client_secret
        except OAuthBadRequestError:
            raise
        except:
            logger.info(u'failed to get client credentials', exc_info=sys.exc_info())
            raise OAuthBadRequestError()

    def get_access_token(self, request):
        authz = request.authorization
        access_token = None
        if authz is not None and authz[0].lower() in ('token', 'basic'):
            access_token = authz[1]
        elif 'access_token' in request.GET:
            access_token = request.GET.pop('access_token')
        elif 'access_token' in request.POST:
            access_token = request.POST.pop('access_token')
        elif 'access_token' in request.json:
            access_token = request.json['access_token']
        return access_token
