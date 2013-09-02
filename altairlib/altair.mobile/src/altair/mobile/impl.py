from uamobile import detect
from uamobile.context import Context
from uamobile.docomo import DoCoMoUserAgent
from uamobile.ezweb import EZwebUserAgent
from uamobile.softbank import SoftBankUserAgent
from uamobile.willcom import WillcomUserAgent
from uamobile.nonmobile import NonMobileUserAgent
import radix
import hashlib
import logging
from zope.interface import implementer, directlyProvides
from pyramid.threadlocal import manager
from markupsafe import Markup, escape
from urlparse import urlparse, urlunparse
from .interfaces import IMobileUserAgent, IMobileUserAgentDisplayInfo, IMobileRequest, IMobileCarrierDetector, IMobileRequestMaker, ISessionObjectImplCompanion
from .carriers import carriers, DoCoMo, EZweb, SoftBank, Willcom, NonMobile

logger = logging.getLogger(__name__)

@implementer(IMobileUserAgent)
class UAMobileUserAgentWrapper(object):
    impl_map = {
        DoCoMoUserAgent.__name__: DoCoMo,
        EZwebUserAgent.__name__: EZweb,
        SoftBankUserAgent.__name__: SoftBank,
        WillcomUserAgent.__name__: Willcom,
        NonMobileUserAgent.__name__: NonMobile
        }

    uo_fetcher_map = {
        DoCoMoUserAgent.__name__: lambda impl: impl.serialnumber,
        EZwebUserAgent.__name__: lambda impl: impl.serialnumber,
        SoftBankUserAgent.__name__: lambda impl: impl.jphone_uid,
        WillcomUserAgent.__name__: lambda impl: None,
        NonMobileUserAgent.__name__: lambda impl: None,
        }

    @property
    def carrier(self):
       return self._carrier

    @property
    def normalized_string(self):
        return self.impl.strip_serialnumber()

    @property
    def string(self):
        return self.impl.useragent

    @property
    def unique_opaque(self):
        return self._uo_fetcher(self.impl)

    @property
    def supports_cookie(Self):
        return self.impl.supports_cookie()

    def get_display_info(self):
        return self.impl.make_display()

    def __init__(self, impl):
        self.impl = impl
        self._carrier = self.impl_map[impl.__class__.__name__]
        self._uo_fetcher = self.uo_fetcher_map[impl.__class__.__name__]

@implementer(IMobileCarrierDetector)
class DefaultCarrierDetector(object):
    def detect_from_fqdn(self, fqdn):
        return self.fqdn_map.get(fqdn, NonMobile)

    def detect_from_wsgi_environment(self, environ):
        return UAMobileUserAgentWrapper(detect(environ, self.uamobile_context)) # XXX

    def detect_from_ip_address(self, address):
        node = self.cidr_block_trie.search_best(address)
        if node is None:
            return NonMobile
        return node.data['carrier']

    def __init__(self, uamobile_context=None):
        self.uamobile_context = uamobile_context or Context()
        self.cidr_block_trie = radix.Radix()
        self.fqdn_map = {}
        # XXX: assuming UAMobile context to be immutable
        for carrier in carriers:
            for cidr_block in self.uamobile_context.get_ip(carrier.id):
                node = self.cidr_block_trie.add(str(cidr_block))
                node.data['carrier'] = carrier
            for fqdn in carrier.email_address_fqdns:
                self.fqdn_map[fqdn] = carrier

import urllib

overridden_url_methods = [
    'route_url',
    'route_path',
    'resource_url',
    'resource_path',
    'current_route_url',
    'current_route_path',
    ]

def parse_query_string(query_string):
    return (tuple(urllib.unquote(kv) for kv in c.partition(b'=')) for c in query_string.split(b'&'))


@implementer(ISessionObjectImplCompanion)
class BeakerSessionObjectCompanion(object):
    def get_cookie_key_from_session(self):
        return getattr(self.session, 'key')

    def get_session_restorer(self):
        cookie_key = self.get_cookie_key_from_session()

        session_restorer = None
        cookie = getattr(self.session, 'cookie')
        if cookie:
            return cookie[cookie_key].coded_value
        else:
            return None 

    def renew_session(self, request):
        self.session = self.session.__class__(request)

    def __init__(self, session):
        self.session = session

def make_session_object_impl_companion(adaptee):
    try:
        from beaker.session import SessionObject
        if isinstance(adaptee, SessionObject):
            return BeakerSessionObjectCompanion(adaptee)
    except:
        pass
    return None

@implementer(IMobileRequestMaker)
class MobileRequestMaker(object):
    hash_key = __name__ + '.ua_hash'

    def __init__(self, query_string_key):
        self.query_string_key = query_string_key

    def fetch_session(self, request, companion):
        if self.query_string_key is not None:
            query_string = request.environ.get('QUERY_STRING')
            cookie_key = companion.get_cookie_key_from_session()
            if query_string is not None:
                session_restorer = None
                for k, _, v in parse_query_string(query_string):
                    if k == self.query_string_key:
                        session_restorer = v
                if session_restorer is not None:
                    request.cookies[cookie_key] = session_restorer
                    companion.renew_session(request)

    def revalidate_session(self, request, companion):
        hash = companion.session.get(self.hash_key)
        _hash = hashlib.sha1(request.user_agent).hexdigest()
        if hash is not None and hash != _hash:
            logger.error('UA hash mismatch')
            companion.session.clear()
        companion.session[self.hash_key] = _hash
        return companion.session

    def override_url_methods(self, request, companion):
        def _mix_query(kw):
            session_restorer = companion.get_session_restorer()
            if session_restorer is not None:
                kw.setdefault('_query', {})[self.query_string_key] = session_restorer

        def decorate(orig):
            def _(*args, **kwargs):
                _mix_query(kwargs)
                return orig(*args, **kwargs)
            return _

        for k in overridden_url_methods:
            orig = getattr(request, k, None)
            if orig is not None:
                setattr(request, k, decorate(orig))

    def retouch_request(self, request, companion):
        if self.query_string_key is not None:
            self.override_url_methods(request, companion)
            try:
                del request.params[self.query_string_key]
            except KeyError:
                pass
            try:
                del request.GET[self.query_string_key]
            except KeyError:
                pass

        def open_form_tag_for_get(**attrs):
            attrs.pop('method', None)
            html = [u'<form method="get"']
            action = attrs.pop('action', None)
            if action:
                parsed_url = urlparse(action)
                attrs['action'] = urlunparse((parsed_url[0], parsed_url[1], parsed_url[2], parsed_url[3], '', parsed_url[5]))
            for k, v in attrs.items():
                html.append(u' %s="%s"' % (escape(k), escape(v)))
            html.append(u'>')
            if self.query_string_key is not None:
                html.append(u'<input type="hidden" name="')
                html.append(escape(self.query_string_key))
                html.append('" value="')
                html.append(escape(companion.get_session_restorer()))
                html.append('"/ >')
            return Markup(u''.join(html))

        request.open_form_tag_for_get = open_form_tag_for_get
        return request

    def __call__(self, request):
        companion = request.registry.queryAdapter(
            getattr(request, 'session', None),
            ISessionObjectImplCompanion
            )
        if companion is not None:
            self.fetch_session(request, companion)
            self.revalidate_session(request, companion)
        decoded = request.decode("cp932:normalized-tilde")
        request.environ.update(decoded.environ)
        decoded.environ = request.environ
        manager.get()['request'] = decoded # hack!
        decoded.is_mobile = True
        directlyProvides(decoded, IMobileRequest)
        decoded.registry = request.registry
        decoded.mobile_ua = request.mobile_ua
        ## todo:remove.
        decoded.is_docomo = request.mobile_ua.carrier.is_docomo #cms, usersite compatibility
        if companion is not None:
            self.retouch_request(decoded, companion)
            decoded.session = companion.session
        return decoded


