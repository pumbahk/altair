import radix
import hashlib
import logging
from markupsafe import Markup, escape
from urlparse import urlparse, urlunparse
from zope.interface import implementer, directlyProvides
from pyramid.threadlocal import manager
from uamobile import detect
from uamobile.context import Context
from uamobile.docomo import DoCoMoUserAgent
from uamobile.ezweb import EZwebUserAgent
from uamobile.softbank import SoftBankUserAgent
from uamobile.willcom import WillcomUserAgent
from uamobile.nonmobile import NonMobileUserAgent

from .interfaces import (
    IMobileUserAgent,
    IMobileUserAgentDisplayInfo,
    IMobileRequest,
    IMobileCarrierDetector,
    IMobileRequestMaker,
    )
from .carriers import (
    carriers,
    DoCoMo,
    EZweb,
    SoftBank,
    Willcom,
    NonMobile,
    )
from .session import HybridHTTPBackend

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

def _get_query_string_key(request):
    return request.environ.get(HybridHTTPBackend.ENV_QUERY_STRING_KEY_KEY)

def _get_session_restorer(request):
    return request.environ.get(HybridHTTPBackend.ENV_SESSION_RESTORER_KEY)

overridden_url_methods = [
    'route_url',
    'route_path',
    'resource_url',
    'resource_path',
    'current_route_url',
    'current_route_path',
    ]

@implementer(IMobileRequestMaker)
class MobileRequestMaker(object):
    hash_key = __name__ + '.ua_hash'

    def __init__(self):
        pass

    def revalidate_session(self, request):
        hash = request.session.get(self.hash_key)
        _hash = hashlib.sha1(request.user_agent).hexdigest()
        if hash is not None and hash != _hash:
            logger.error('UA hash mismatch')
            request.session.invalidate()
        request.session[self.hash_key] = _hash

    def _retouch_request(self, request):
        query_string_key = _get_query_string_key(request)
        if query_string_key is None:
            return

        session_restorer = _get_session_restorer(request)
        def decorate(orig):
            def _(*args, **kwargs):
                kwargs.setdefault('_query', {})[query_string_key] = session_restorer
                return orig(*args, **kwargs)
            return _

        for k in overridden_url_methods:
            orig = getattr(request, k, None)
            if orig is not None:
                setattr(request, k, decorate(orig))

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
            if query_string_key is not None:
                html.append(u'<input type="hidden" name="')
                html.append(escape(query_string_key))
                html.append(u'" value="')
                html.append(escape(session_restorer))
                html.append(u'"/ >')
            return Markup(u''.join(html))
        request.open_form_tag_for_get = open_form_tag_for_get

    def __call__(self, request):
        # the following is needed to differentiate the kind of the request in HTTP backend module
        directlyProvides(request, IMobileRequest)
        self.revalidate_session(request)
        kept_session = request.session
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
        decoded.session = kept_session
        self._retouch_request(decoded)
        return decoded
