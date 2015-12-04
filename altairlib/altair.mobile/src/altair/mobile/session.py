import urllib
import logging
from altair.httpsession.factory import parameters
from altair.httpsession.cookies import PlainCookie, SignedCookie
from altair.httpsession.api import CookieSessionBinder
from .interfaces import IMobileRequest
from urlparse import urlparse, urlunparse

__all__ = [
    'HybridHTTPBackend',
    'http_backend_factory',
    ]

logger = logging.getLogger(__name__)


def parse_query_string(query_string):
    return (tuple(urllib.unquote_plus(kv) for kv in s2.partition(b'=')) for s1 in query_string.split(b'&') for s2 in s1.split(b';'))

def get_cookie_factory(secret):
    if secret is not None:
        cookie_factory = lambda input: SignedCookie(secret, input=input)
    else:
        cookie_factory = PlainCookie
    return cookie_factory

def pop_session_restorer(environ, query_string_key):
    query_string = environ.get('QUERY_STRING')
    if query_string is not None:
        new_query_string, session_restorer = strip_session_restorer(query_string, query_string_key)
        if session_restorer is not None:
            environ['QUERY_STRING'] = new_query_string
            return session_restorer
    return None

def append_session_restorer(query_string, query_string_key, session_restorer):
    if query_string:
        x = ';'
    else:
        x = ''
    x += '%s=%s' % (
        urllib.quote_plus(query_string_key),
        urllib.quote_plus(session_restorer),
        )
    return query_string + x

def strip_session_restorer(query_string, query_string_key):
    session_restorer = None
    new_params = []
    for k, _, v in parse_query_string(query_string):
        if k == query_string_key:
            session_restorer = v
        else:
            new_params.append((k, v))
    return urllib.urlencode(new_params), session_restorer

def merge_session_restorer_to_url(url, query_string_key, session_restorer):
    parsed_url = urlparse(url)
    query_string = append_session_restorer(parsed_url[4], query_string_key, session_restorer)
    return urlunparse((parsed_url[0], parsed_url[1], parsed_url[2], parsed_url[3], query_string, parsed_url[5]))

def unmerge_session_restorer_from_url(url, query_string_key):
    parsed_url = urlparse(url)
    query_string, _ = strip_session_restorer(parsed_url[4], query_string_key)
    return urlunparse((parsed_url[0], parsed_url[1], parsed_url[2], parsed_url[3], query_string, parsed_url[5]))

class HybridHTTPBackend(object):
    ENV_QUERY_STRING_KEY_KEY = 'altair.mobile.session.HybridHTTPBackend.key'
    ENV_SESSION_RESTORER_KEY = 'altair.mobile.session.HybridHTTPBackend.session_restorer'

    def __init__(self, request, query_string_key, secret=None, key='beaker.session.id', **kwargs):
        cookie_factory = get_cookie_factory(secret)
        cookie_header_value = None

        # first try to fetch session restorer from environ
        session_restorer = request.environ.get(self.ENV_SESSION_RESTORER_KEY)
        if session_restorer is None:
            session_restorer = pop_session_restorer(request.environ, query_string_key)

        if session_restorer is not None:
            cookie_header_value = b'%s=%s' % (key, urllib.quote(session_restorer))
        else:
            cookie_header_value = request.environ.get('HTTP_COOKIE')

        self.inner = CookieSessionBinder(
            key=key,
            cookie=cookie_factory(input=cookie_header_value),
            **kwargs
            )
        request.environ[self.ENV_QUERY_STRING_KEY_KEY] = query_string_key
        self.request = request

    def bind(self, id_):
        self.inner.bind(id_)
        try:
            cookie_item = self.inner.cookie[self.inner.key]
            self.request.environ[self.ENV_SESSION_RESTORER_KEY] = cookie_item.coded_value if cookie_item.value else None
        except KeyError:
            pass

    def unbind(self, id_):
        self.inner.unbind(id_)

    def get(self):
        return self.inner.get()

    def modify_response(self, resp):
        self.inner.modify_response(resp)

    @classmethod
    def get_query_string_key(cls, request):
        return request.environ.get(cls.ENV_QUERY_STRING_KEY_KEY)

    @classmethod
    def get_session_restorer(cls, request):
        return request.environ.get(cls.ENV_SESSION_RESTORER_KEY)


@parameters(
    CookieSessionBinder,
    query_string_key='str',
    secret='str?'
    )
def http_backend_factory(request, query_string_key, secret=None, key='beaker.session.id', **kwargs):
    if IMobileRequest.providedBy(request):
        return HybridHTTPBackend(request, query_string_key=query_string_key, secret=secret, key=key, **kwargs)
    else:
        return CookieSessionBinder(
            cookie=get_cookie_factory(secret)(input=request.environ.get('HTTP_COOKIE')),
            key=key,
            **kwargs
            )
