# encoding: utf-8

import urllib
import urllib2
from urlparse import urljoin
import logging
import uuid
from zope.interface import implementer
from beaker.session import Session

from pyramid.httpexceptions import HTTPFound, HTTPUnauthorized
from pyramid.response import Response
from pyramid import security

from altair.auth import who_api as get_who_api

from .interfaces import IRakutenOpenID
from .events import Authenticated

logger = logging.getLogger(__name__)

@implementer(IRakutenOpenID)
class RakutenOpenID(object):
    SESSION_KEY = '_%s_session' % __name__

    def __init__(self,
            endpoint,
            verify_url,
            extra_verify_url,
            error_to,
            consumer_key,
            session_args,
            return_to=None,
            timeout=10):
        self.endpoint = endpoint
        self.verify_url = verify_url
        self.extra_verify_url = extra_verify_url
        self.error_to = error_to
        self.consumer_key = consumer_key
        self.session_args = session_args
        self.return_to = return_to or verify_url
        self.timeout = int(timeout)

    def get_session_id(self, request):
        return request.params.get('ak')

    def new_session(self, request):
        return Session(request, id=None, **self.session_args)

    def get_session(self, request):
        session = getattr(request, self.SESSION_KEY, None)
        if session is None:
            id = self.get_session_id(request)
            if id is not None:
                session = Session(request, id=id, **self.session_args)
                setattr(request, self.SESSION_KEY, session)
        return session

    def combine_session_id(self, url, session):
        return urljoin(url, '?ak=' + urllib.quote(session.id))

    def get_redirect_url(self, session):
        return self.endpoint + "?" + urllib.urlencode([
            ('openid.ns', 'http://specs.openid.net/auth/2.0'),
            ('openid.return_to', self.combine_session_id(self.return_to, session)),
            ('openid.claimed_id', 'http://specs.openid.net/auth/2.0/identifier_select'),
            ('openid.identity', 'http://specs.openid.net/auth/2.0/identifier_select'),
            ('openid.mode', 'checkid_setup'),
            ('openid.ns.oauth', 'http://specs.openid.net/extenstions/oauth/1.0'),
            ('openid.oauth.consumer', self.consumer_key),
            ('openid.oauth.scope', 'rakutenid_basicinfo,rakutenid_contactinfo,rakutenid_pointaccount'),
            # ('openid.ns.ax', 'http://openid.net/srv/ax/1.0'),
            # ('openid.ax.mode', 'fetch_request'),
            # ('openid.ax.type.nickname', 'http://schema.openid.net/namePerson/friendly'),
            # ('openid.ax.required', 'nickname'),
        ])

    def verify_authentication(self, request, identity):
        url = self.endpoint + "?" + urllib.urlencode(
           [('openid.ns', identity['ns']),
            ('openid.op_endpoint', identity['op_endpoint']),
            ('openid.claimed_id', identity['claimed_id']),
            ('openid.response_nonce',identity['response_nonce']),
            ('openid.mode', identity['mode']),
            ('openid.identity', identity['identity']),
            ('openid.return_to', identity['return_to']),
            ('openid.assoc_handle', identity['assoc_handle']),
            ('openid.signed', identity['signed']),
            ('openid.sig', identity['sig']),
            ('openid.ns.oauth', identity['ns_oauth']),
            ('openid.oauth.request_token', identity['oauth_request_token']),
            ('openid.oauth.scope', identity['oauth_scope']),
            # ('openid.ns.ax', identity['ns_ax']),
            # ('openid.ax.mode', identity['ax_mode']),
            # ('openid.ax.type.nickname', identity['ax_type_nickname']),
            # ('openid.ax.value.nickname', identity['ax_value_nickname'].encode('utf-8')),
        ])

        f = urllib2.urlopen(url, timeout=self.timeout)
        try:
            response_body = f.read()
        finally:
            f.close()

        logger.debug('authenticate result : %s' % response_body)
        is_valid = response_body.split("\n")[0].split(":")[1]

        if is_valid == "true":
            logger.debug("authentication OK")
            return True
        else:
            logger.debug("authentication NG")
            return False

    def openid_params(self, request):
        logger.debug('openid verify GET: {0}\nPOST{1}'.format(request.GET.items(), request.POST.items()))
        request_get = request.params
        return dict(
            ns = request_get['openid.ns'],
            op_endpoint = request_get['openid.op_endpoint'],
            claimed_id = request_get['openid.claimed_id'],
            response_nonce = request_get['openid.response_nonce'],
            mode = 'check_authentication',
            identity = request_get['openid.identity'],
            return_to = request_get['openid.return_to'],
            assoc_handle = request_get['openid.assoc_handle'],
            signed = request_get['openid.signed'],
            sig = request_get['openid.sig'],
            ns_oauth = 'http://specs.openid.net/extenstions/oauth/1.0',
            oauth_request_token = request_get['openid.oauth.request_token'],
            oauth_scope = 'rakutenid_basicinfo,rakutenid_contactinfo,rakutenid_pointaccount',
            # ns_ax = request_get['openid.ns.ax'],
            # ax_mode = request_get['openid.ax.mode'],
            # ax_type_nickname = request_get['openid.ax.type.nickname'],
            # ax_value_nickname = request_get['openid.ax.value.nickname'],
            )

    def get_return_url(self, session):
        return session.get(self.__class__.__name__ + '.return_url')

    def set_return_url(self, session, url):
        session[self.__class__.__name__ + '.return_url'] = url

    def on_verify(self, request):
        who_api = get_who_api(request, name="rakuten")
        params = self.openid_params(request)
        identity, headers = who_api.login(params)
        session = self.get_session(request)

        if identity:
            return HTTPFound(
	    	self.combine_session_id(
                    self.extra_verify_url,
                    session))
        else:
            return HTTPFound(location=self.error_to)

    def on_extra_verify(self, request):
        who_api = get_who_api(request, name="rakuten")
        identity = who_api.authenticate()
        if identity:
            request.registry.notify(Authenticated(request, identity))
            session = self.get_session(request)
            return_url = self.get_return_url(session)
            if not return_url:
                # TODO: デフォルトURLをHostからひいてくる
                return_url = "/"
            session.clear()
            headers = identity['identifier'].remember(request.environ, identity)
            return HTTPFound(location=return_url, headers=headers)
        else:
            logger.error('authentication failure on extra_verify, check that request.path_url (%s) is identical to %s' % (request.path_url, self.extra_verify_url))
            return HTTPFound(location=self.error_to)

def openid_consumer_from_settings(settings, prefix):
    session_args = {}
    for k, v in settings.items():
        if k.startswith(prefix + 'session.'):
            session_args[k[len(prefix + 'session.'):]] = v

    return RakutenOpenID(
        endpoint=settings[prefix + 'endpoint'],
        verify_url=settings[prefix + 'verify_url'],
        extra_verify_url=settings[prefix + 'extra_verify_url'],
        error_to=settings[prefix + 'error_to'],
        consumer_key=settings[prefix + 'oauth.consumer_key'],
        session_args=session_args,
        return_to=settings.get(prefix + 'return_to'),
        timeout=settings.get(prefix + 'timeout')
        )

def includeme(config):
    from . import CONFIG_PREFIX
    config.registry.registerUtility(
        openid_consumer_from_settings(
            config.registry.settings,
            prefix=CONFIG_PREFIX),
        IRakutenOpenID
        )
