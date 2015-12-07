import os
import binascii
import logging
from zope.interface import implementer
from pyramid.interfaces import ISession
from pyramid.compat import text_
from pyramid.config import ConfigurationError
from pyramid.path import DottedNameResolver
from pyramid.settings import asbool
from ..api import HTTPSession, BasicHTTPSessionManager, CookieSessionBinder
from ..factory import BackendFactoryFactory, parameters
from .interfaces import ISessionHTTPBackendFactory, ISessionPersistenceBackendFactory

__all__ = [
    'PyramidSession',
    'PyramidSessionFactory',
    'register_utilities',
    ]

logger = logging.getLogger(__name__)

@implementer(ISession)
class PyramidSession(HTTPSession):
    def _queue_key(self, key):
        return '_f_' + key

    def _csrf_token_key(self):
        return '_csrft_'

    def flash(self, msg, queue='', allow_duplicate=True):
        storage = self.setdefault(self._queue_key(queue), [])
        if allow_duplicate or (msg not in storage):
            storage.append(msg)

    def pop_flash(self, queue=''):
        storage = self.pop(self._queue_key(queue), [])
        return storage

    def peek_flash(self, queue=''):
        storage = self.get(self._queue_key(queue), [])
        return storage

    def new_csrf_token(self):
        token = text_(binascii.hexlify(os.urandom(20)))
        self[self._csrf_token_key()] = token
        return token

    def get_csrf_token(self):
        token = self.get(self._csrf_token_key(), None)
        if token is None:
            token = self.new_csrf_token()
        return token

    @property
    def new(self):
        return self.is_new

    def changed(self):
        self.dirty = True


class ResponseWrapper(object):
    def __init__(self, resp):
        self.resp = resp

    def get_response_text(self):
        return self.resp.text

    def get_response_body(self):
        return self.resp.body

    def set_response_text(self, text):
        self.resp.text = text

    def set_response_body(self, body):
        self.resp.body = body

    def add_header(self, key, value):
        self.resp.headerlist.append((key, value))


@parameters(
    CookieSessionBinder,
    secret='str?',
    cookie_factory='callable?'
    )
def cookies(request, secret=None, cookie_factory=None, **kwargs):
    if cookie_factory is not None:
        cookie_factory = DottedNameResolver().maybe_dotted(cookie_factory)
    else:
        from ..cookies import SignedCookie, PlainCookie
        if secret is not None:
            cookie_factory = lambda input: SignedCookie(secret, input=input)
        else:
            cookie_factory = PlainCookie
    cookie_header_value = request.environ.get('HTTP_COOKIE')
    return CookieSessionBinder(
        cookie=cookie_factory(input=cookie_header_value),
        **kwargs
        )


class PyramidSessionFactory(object):
    session_factory=PyramidSession

    def __call__(self, request):
        persistence_backend_factory = request.registry.queryUtility(ISessionPersistenceBackendFactory)
        http_backend_factory = request.registry.queryUtility(ISessionHTTPBackendFactory)
        manager = BasicHTTPSessionManager(
            persistence_backend_factory=persistence_backend_factory,
            http_backend_factory=http_backend_factory,
            session_factory=self.session_factory
            )
        session = manager(request)
        def session_callback(request, response):
            session.save()
            session.context.http_backend.modify_response(ResponseWrapper(response))
        request.add_response_callback(session_callback)
        return session


def register_utilities(config, prefix='altair.httpsession', skip_http_backend_registration=False):
    if prefix[-1] != '.':
        prefix += '.'

    coercers = BackendFactoryFactory.default_coercers.copy()
    coercers.update({
        'bool': asbool,
        'class': config.maybe_dotted,
        'instance': config.maybe_dotted,
        'callable': config.maybe_dotted,
        })
    backend_factory_factory = BackendFactoryFactory(coercers=coercers)

    settings = {}
    http_backend_settings = {}
    persistence_backend_settings = {}
    for k, v in config.registry.settings.items():
        prefix_http_backend = prefix + 'http_backend.'
        prefix_persistence_backend = prefix + 'persistence.'
        if k.startswith(prefix_http_backend):
            http_backend_settings[k[len(prefix_http_backend):]] = v
        elif k.startswith(prefix_persistence_backend):
            persistence_backend_settings[k[len(prefix_persistence_backend):]] = v
        elif k.startswith(prefix):
            settings[k[len(prefix):]] = v

    http_backend_factory = None
    if not skip_http_backend_registration:
        http_backend_factory_value = settings.get('http_backend', cookies)
        http_backend_factory = config.maybe_dotted(http_backend_factory_value)
        if http_backend_factory is None:
            raise ConfigurationError('Could not find http backend factory (%s)' % http_backend_factory_value)

    persistence_value = settings.get('persistence')
    persistence_backend_factory = config.maybe_dotted(persistence_value)
    if persistence_backend_factory is None:
        raise ConfigurationError('Could not find persistence backend factory (%s)' % persistence_value)

    if http_backend_factory is not None:
        config.registry.registerUtility(
            backend_factory_factory(http_backend_factory, http_backend_settings),
            ISessionHTTPBackendFactory
            )
    else:
        logger.info('skipping HTTP backend registration')

    config.registry.registerUtility(
        backend_factory_factory(persistence_backend_factory, persistence_backend_settings),
        ISessionPersistenceBackendFactory
        )


def includeme(config):
    register_utilities(config)
    config.set_session_factory(PyramidSessionFactory())
