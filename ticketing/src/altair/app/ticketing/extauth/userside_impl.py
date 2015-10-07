# encoding: utf-8
import logging
import json
from urllib import urlencode
import urllib2
import cgi
import six
from urlparse import urljoin
from zope.interface import implementer
from altair.oauth_auth.interfaces import IOAuthAPIFactory, IOAuthNegotiator, IOAuthAPI
from altair.oauth_auth.exceptions import OAuthAPICommunicationError
from altair.app.ticketing.utils import parse_content_type

logger = logging.getLogger(__name__)

@implementer(IOAuthAPIFactory)
class OAuthAPIFactory(object):
    def __init__(self, opener_factory, token_endpoint, client_credentials, encoding='utf-8'):
        self.opener_factory = opener_factory
        self.token_endpoint = token_endpoint
        self.client_credentials = client_credentials
        self.encoding = encoding

    def create_oauth_negotiator(self):
        return OAuthNegotiator(self.opener_factory, self.token_endpoint, self.client_credentials, self.encoding)

    def create_oauth_api(self, access_token, endpoint_url):
        return OAuthAPIClient(self.opener_factory, self.encoding, access_token, {u'get_user_info': endpoint_url})


class OAuthAPIBase(object):
    def _encode_params(self, params):
        return urlencode([
            (k.encode(self.encoding), v.encode(self.encoding))
            for k, v in params
            ])

@implementer(IOAuthNegotiator)
class OAuthNegotiator(OAuthAPIBase):
    def __init__(self, opener_factory, endpoint, client_credentials, encoding='utf-8'):
        self.opener_factory = opener_factory
        self.endpoint = endpoint
        self.client_credentials = client_credentials
        self.encoding = encoding

    def get_access_token(self, request, authorization_code, redirect_uri):
        opener = self.opener_factory()
        client_credentials = self.client_credentials
        if callable(client_credentials):
            client_credentials = client_credentials(request)
        client_id, client_secret = client_credentials
        endpoint = self.endpoint
        if callable(endpoint):
            endpoint = endpoint(request)
        req = urllib2.Request(
            endpoint,
            headers={'Content-Type': 'application/x-www-form-urlencoded; charset=%s' % self.encoding},
            data=self._encode_params(
                {u'grant_type': u'authorization_code', u'client_id': client_id, u'client_secret': client_secret, u'code': authorization_code, u'redirect_uri': redirect_uri}.items()
                )
            )
        try:
            resp = opener.open(req)
        except urllib2.HTTPError as e:
            resp = e
        retval = None
        try:
            mime_type, encoding = parse_content_type(resp.headers['content-type'])
            if not encoding:
                encoding = self.encoding
            if mime_type == 'application/json':
                retval = json.load(resp, encoding=encoding)
            elif mime_type in ('application/x-www-form-urlencoded', 'text/plain'): # text/plain は Facebook の腐った API 対策
                retval = dict(
                    (
                        six.text_type(k, encoding),
                        six.text_type(v, encoding)
                        )
                    for k, v in cgi.parse_qsl(resp.read())
                    )
            else:
                raise OAuthAPICommunicationError('unsupported response: mime_type=%s, body=%s' % (mime_type, resp.read()))
        finally:
            resp.close()
        if isinstance(resp, urllib2.HTTPError):
            logger.error('%r' % retval)
            if retval is not None:
                raise OAuthAPICommunicationError(u'%d %s (%s - %s)' % (e.code, e.msg, retval['error'], retval.get('error_description', u'(no description provided)')))
            else:
                raise OAuthAPICommunicationError(u'%d %s' % (e.code, e.msg))
        access_token = retval.pop(u'access_token')
        return (access_token, retval)


@implementer(IOAuthAPI)
class OAuthAPIClient(OAuthAPIBase):
    def __init__(self, opener_factory, encoding, access_token, endpoints):
        self.opener_factory = opener_factory
        self.encoding = encoding
        self.access_token = access_token
        self.endpoints = endpoints

    def _do_get_request(self, endpoint, params):
        opener = self.opener_factory()
        params_ = params.copy()
        params_.update(access_token=self.access_token)
        url = urljoin(endpoint, '?' + self._encode_params(params_.items()))
        req = urllib2.Request(url)
        try:
            resp = opener.open(req)
        except urllib2.HTTPError as e:
            raise OAuthAPICommunicationError(u'%s: url=%s, body=%s' % (unicode(e), url, e.read()))
        try:
            mime_type, encoding = parse_content_type(resp.headers['content-type'])
            if mime_type not in ('application/json', 'text/javascript'): # text/javascript は Facebook の腐った API 対策
                raise OAuthAPICommunicationError(u'MIME type should be application/json, got %s' % mime_type)
            return json.load(resp, encoding=(encoding or self.encoding))
        finally:
            resp.close()

    def get_endpoint(self, request, name):
        endpoint = self.endpoints[name]
        if callable(endpoint):
            endpoint = endpoint(request)
        return endpoint

    def get_user_info(self, request):
        user_info = self._do_get_request(self.get_endpoint(request, 'get_user_info'), {})
        logger.debug('get_user_info() = %r' % user_info)
        return dict(
            identifiers=dict(
                id=user_info['id'],
                authz_id=user_info.get('membership_id', user_info['id']),
                authz_kind=user_info['member_kind']['name'] if 'member_kind' in user_info else None
                ),
            profile=user_info.get('profile', None)
            )


class Authenticated(object):
    def __init__(self, request, id, metadata):
        self.request = request
        self.id = id
        self.metadata = metadata


def on_login(request, identity, metadata):
    request.registry.notify(
        Authenticated(
            request,
            identity,
            metadata['profile']
            )
        )


CLIENT_CREDENTIALS_KEY = '%s.client_credentials' % __name__
ENDPOINT_TOKEN_KEY = '%s.endpoint_token' % __name__
ENDPOINT_API_KEY = '%s.endpoint_api' % __name__

def includeme(config):
    registry = config.registry
    settings = registry.settings
    from altair.oauth_auth.plugin import OAuthAuthPlugin
    from altair.app.ticketing.urllib2ext import opener_factory_from_config

    def client_id(request):
        return request.session[CLIENT_CREDENTIALS_KEY][0]

    def authz_endpoint(request):
        request.session[CLIENT_CREDENTIALS_KEY] = (
            request.context.cart_setting.oauth_client_id,
            request.context.cart_setting.oauth_client_secret
            )
        request.session[ENDPOINT_API_KEY] = request.context.cart_setting.oauth_endpoint_api
        request.session[ENDPOINT_TOKEN_KEY] = request.context.cart_setting.oauth_endpoint_token
        return request.context.cart_setting.oauth_endpoint_authz
       
    def api_endpoint(request):
        return request.session[ENDPOINT_API_KEY]

    def error_url(request):
        return u'/'

    def token_endpoint(request):
        return request.session[ENDPOINT_TOKEN_KEY]

    def client_credentials(request):
        return request.session[CLIENT_CREDENTIALS_KEY]

    plugin = OAuthAuthPlugin(
        client_id,
        authz_endpoint,
        api_endpoint,
        u'/.extauth/callback',
        error_url,
        on_login=on_login
        )
    opener_factory = opener_factory_from_config(config, 'altair.extauth.oauth.urllib2_opener_fatory')
    registry.registerUtility(
        OAuthAPIFactory(
            opener_factory,
            token_endpoint,
            client_credentials,
            'utf-8'
            ),
        IOAuthAPIFactory,
        name=plugin.name
        )
    config.add_auth_plugin(plugin)
