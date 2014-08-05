# encoding: utf-8

import urllib
import urllib2
from urlparse import urljoin
import logging
import uuid
from zope.interface import implementer
from altair.httpsession.api import (
    HTTPSession,
    BasicHTTPSessionManager,
    DummyHTTPBackend,
    )
from altair.httpsession.idgen import _generate_id

from pyramid.httpexceptions import HTTPFound, HTTPUnauthorized
from pyramid.response import Response
from pyramid.path import DottedNameResolver
from pyramid import security

from altair.auth import who_api as get_who_api
from altair.mobile.interfaces import IMobileRequest
from altair.mobile.session import HybridHTTPBackend, merge_session_restorer_to_url

from .interfaces import IRakutenOpenID
from .events import Authenticated
from . import IDENT_METADATA_KEY

logger = logging.getLogger(__name__)


class RakutenOpenIDHTTPSessionContext(object):
    http_backend = None

    def __init__(self, persistence_backend):
        self.persistence_backend = persistence_backend

    def on_load(self, id_, data):
        pass

    def on_new(self, id_, data):
        pass

    def on_save(self, id_, data):
        pass

    def on_delete(self, id_, data):
        pass

    def generate_id(self):
        return _generate_id()


class RakutenOpenIDHTTPSessionFactory(object):
    def __init__(self, persistence_backend, session_args):
        import altair.httpsession
        self.persistence_backend_factory = DottedNameResolver(altair.httpsession).maybe_resolve(persistence_backend)
        self.session_args = session_args

    def __call__(self, request, id=None):
        persistence_backend = self.persistence_backend_factory(request, **self.session_args)
        return HTTPSession(
            RakutenOpenIDHTTPSessionContext(persistence_backend),
            id
            )


@implementer(IRakutenOpenID)
class RakutenOpenID(object):
    SESSION_KEY = '_%s_session' % __name__
    SESSION_IDENT_KEY = 'RakutenOpenIDPlugin.identity'
    IDENT_OPENID_PARAMS_KEY = '%s.params' % __name__

    def __init__(self,
            endpoint,
            verify_url,
            extra_verify_url,
            error_to,
            consumer_key,
            session_factory,
            return_to=None,
            timeout=10):
        self.endpoint = endpoint
        self.verify_url = verify_url
        self.extra_verify_url = extra_verify_url
        self.error_to = error_to
        self.consumer_key = consumer_key
        self.session_factory = session_factory
        self.return_to = return_to or verify_url
        self.timeout = int(timeout)

    def get_session_id(self, request):
        return request.params.get('ak')

    def new_session(self, request):
        return self.session_factory(request, id=None)

    def get_session(self, request):
        session = getattr(request, self.SESSION_KEY, None)
        if session is None:
            id = self.get_session_id(request)
            if id is not None:
                session = self.session_factory(request, id=id)
                setattr(request, self.SESSION_KEY, session)
        return session

    def get_who_api(self, request):
        return get_who_api(request, name='rakuten')

    def combine_session_id(self, request, session, url):
        q = '?ak=' + urllib.quote(session.id)
        if IMobileRequest.providedBy(request):
            key = HybridHTTPBackend.get_query_string_key(request)
            session_restorer = HybridHTTPBackend.get_session_restorer(request)
            if key and session_restorer:
                # webobは"&"の他に";"文字もデリミタと見なしてくれる
                q += ';%s=%s' % (urllib.quote(key), urllib.quote(session_restorer))
        return urljoin(url, q)

    def get_redirect_url(self, request, session):
        return self.endpoint + "?" + urllib.urlencode([
            ('openid.ns', 'http://specs.openid.net/auth/2.0'),
            ('openid.return_to', self.combine_session_id(request, session, self.return_to)),
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

    def verify_authentication(self, request, params):
        url = self.endpoint + "?" + urllib.urlencode(
           [('openid.ns', params['ns']),
            ('openid.op_endpoint', params['op_endpoint']),
            ('openid.claimed_id', params['claimed_id']),
            ('openid.response_nonce',params['response_nonce']),
            ('openid.mode', params['mode']),
            ('openid.identity', params['identity']),
            ('openid.return_to', params['return_to']),
            ('openid.assoc_handle', params['assoc_handle']),
            ('openid.signed', params['signed']),
            ('openid.sig', params['sig']),
            ('openid.ns.oauth', params['ns_oauth']),
            ('openid.oauth.request_token', params['oauth_request_token']),
            ('openid.oauth.scope', params['oauth_scope']),
            # ('openid.ns.ax', params['ns_ax']),
            # ('openid.ax.mode', params['ax_mode']),
            # ('openid.ax.type.nickname', params['ax_type_nickname']),
            # ('openid.ax.value.nickname', params['ax_value_nickname'].encode('utf-8')),
        ])

        f = urllib2.urlopen(url, timeout=self.timeout)
        try:
            response_body = f.read()
        finally:
            f.close()

        logger.debug('authenticate result: %s' % response_body)
        is_valid = response_body.split("\n")[0].split(":")[1]

        if is_valid == "true":
            return True
        else:
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

    def extra_verification_phase(self, request):
        return request.path_url == self.extra_verify_url

    def extra_verification_phase_exists(self, request):
        return self.extra_verify_url is not None 

    def on_challenge(self, request):
        session = self.new_session(request)
        return_url = request.url
        _session = request.session # Session gets created here!
        if _session is not None and IMobileRequest.providedBy(request):
            key = HybridHTTPBackend.get_query_string_key(request)
            session_restorer = HybridHTTPBackend.get_session_restorer(request)
            if key and session_restorer:
                return_url = merge_session_restorer_to_url(return_url, key, session_restorer)
        self.set_return_url(session, return_url)
        session.save()
        redirect_to = self.get_redirect_url(request, session)
        logger.debug('redirect from %s to %s' % (request.url, redirect_to))
        return HTTPFound(location=redirect_to)

    def on_verify(self, request):
        params = self.openid_params(request)
        session = self.get_session(request)
        if session is None:
            logging.info('could not retrieve the temporary session')
            return HTTPFound(location=self.error_to)
        who_api = self.get_who_api(request)
        identity, headers = who_api.login({ self.IDENT_OPENID_PARAMS_KEY: params })
        if identity:
            if self.extra_verification_phase_exists(request):
                session[self.SESSION_IDENT_KEY] = identity
                session.save()
                return HTTPFound(
                    self.combine_session_id(
                        request, session,
                        self.extra_verify_url))
            else:
                return self._on_success(request, session, identity, headers)
        else:
            return HTTPFound(location=self.error_to)

    def on_extra_verify(self, request):
        if not self.extra_verification_phase(request):
            logger.error('authentication failure on verify. request.path_url (%s) != extra_verify_url (%s)' % (request.path_url, self.extra_verify_url))
            return HTTPFound(location=self.error_to)

        session = self.get_session(request)
        if session is None:
            logging.info('could not retrieve the temporary session')
            return HTTPFound(location=self.error_to)
        identity = session.get(self.SESSION_IDENT_KEY)
        if identity is None:
            logging.info('no identity stored in the temporary session')
            return HTTPFound(location=self.error_to)
        who_api = self.get_who_api(request)
        identity, headers = who_api.login(identity)
        if identity is not None:
            session = self.get_session(request)
            return self._on_success(request, session, identity, headers)
        else:
            logger.info('authentication failure on verify. temporary session timeout, oauth API failures etc.')
            return HTTPFound(location=self.error_to)

    def _on_success(self, request, session, identity, headers):
        who_api = self.get_who_api(request)
        identity = who_api.authenticate() # needed to fetch metadata
        request.registry.notify(Authenticated(
            request,
            identity['repoze.who.userid'],
            identity[IDENT_METADATA_KEY]
            ))
        return_url = self.get_return_url(session)
        if not return_url:
            # TODO: デフォルトURLをHostからひいてくる
            return_url = "/"
        session.invalidate()
        return HTTPFound(location=return_url, headers=headers)


def openid_consumer_from_settings(settings, prefix):
    session_args = {}
    for k, v in settings.items():
        if k.startswith(prefix + 'session.'):
            session_args[k[len(prefix + 'session.'):]] = v
    persistence_backend = settings[prefix + 'session']

    return RakutenOpenID(
        endpoint=settings[prefix + 'endpoint'],
        verify_url=settings[prefix + 'verify_url'],
        extra_verify_url=settings[prefix + 'extra_verify_url'],
        error_to=settings[prefix + 'error_to'],
        consumer_key=settings[prefix + 'oauth.consumer_key'],
        session_factory=RakutenOpenIDHTTPSessionFactory(
            persistence_backend,
            session_args
            ),
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
