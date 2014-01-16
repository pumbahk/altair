import urllib
import logging
from altair.httpsession.cookies import PlainCookie, SignedCookie
from altair.httpsession.api import CookieSessionBinder
from .interfaces import IMobileRequest

__all__ = [
    'HybridHTTPBackend',
    'http_backend_factory',
    ]

logger = logging.getLogger(__name__)

def parse_query_string(query_string):
    return (tuple(urllib.unquote(kv) for kv in c.partition(b'=')) for c in query_string.split(b'&'))


def get_cookie_factory(secret):
    if secret is not None:
        cookie_factory = lambda input: SignedCookie(secret, input=input)
    else:
        cookie_factory = PlainCookie
    return cookie_factory


def pop_session_restorer(environ, query_string_key):
    session_restorer = None
    new_params = []
    query_string = environ.get('QUERY_STRING')
    import sys
    if query_string is not None:
        for k, _, v in parse_query_string(query_string):
            if k == query_string_key:
                session_restorer = v
            else:
                new_params.append((k, v))
        if session_restorer is not None:
            environ['QUERY_STRING'] = urllib.urlencode(new_params)
            return session_restorer
    return None


class HybridHTTPBackend(object):
    ENV_QUERY_STRING_KEY_KEY = 'altair.mobile.session.HybridHTTPBackend.key'
    ENV_SESSION_RESTORER_KEY = 'altair.mobile.session.HybridHTTPBackend.session_restorer'

    def __init__(self, request, query_string_key, secret=None, key='beaker.session.id', **kwargs):
        cookie_factory = get_cookie_factory(secret)
        cookie_header_value = None

        session_restorer = pop_session_restorer(request.environ, query_string_key)
        if session_restorer is not None:
            cookie_header_value = b'%s=%s' % (key, urllib.quote(session_restorer))
        else:
            cookie_header_value = request.environ.get('HTTP_COOKIE')

        self.inner = CookieSessionBinder(
            request=request,
            key=key,
            cookie=cookie_factory(input=cookie_header_value),
            **kwargs
            )
        request.environ[self.ENV_QUERY_STRING_KEY_KEY] = query_string_key

    def bind(self, id_):
        self.inner.bind(id_)
        try:
            cookie_item = self.inner.cookie[self.inner.key]
            self.inner.request.environ[self.ENV_SESSION_RESTORER_KEY] = cookie_item.coded_value if cookie_item.value else None
        except KeyError:
            pass

    def unbind(self, id_):
        self.inner.unbind(id_)

    def get(self):
        return self.inner.get()

    def modify_response(self, resp):
        self.inner.modify_response(resp)


def http_backend_factory(request, query_string_key, secret=None, key='beaker.session.id', **kwargs):
    if IMobileRequest.providedBy(request):
        return HybridHTTPBackend(request, query_string_key=query_string_key, secret=secret, key=key, **kwargs)
    else:
        return CookieSessionBinder(
            cookie=get_cookie_factory(secret)(input=request.environ.get('HTTP_COOKIE')),
            request=request,
            key=key,
            **kwargs
            )
