import hashlib
import logging
from markupsafe import Markup, escape
from urlparse import urlparse, urlunparse
from zope.interface import implementer, directlyProvides, noLongerProvides
from pyramid.threadlocal import manager

from .interfaces import (
    IMobileRequest,
    ISmartphoneRequest,
    IMobileMiddleware,
    ISmartphoneSupportPredicate,
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
from .api import smartphone_support_enabled_for, detect

logger = logging.getLogger(__name__)

overridden_url_methods = [
    'route_url',
    'route_path',
    'resource_url',
    'resource_path',
    'current_route_url',
    'current_route_path',
    ]

@implementer(IMobileMiddleware)
class MobileMiddleware(object):
    hash_key = __name__ + '.ua_hash'

    def __init__(self, encoding='Shift_JIS', codec=None, errors='strict', on_error_handler=None, preverify_request_parameter_encoding=False):
        if codec is None:
            codec = encoding
            # XXX: tentative
            if codec.lower() == 'shift_jis':
                codec = 'cp932:normalized-tilde'
        self.encoding = encoding
        self.codec = codec
        self.errors = errors
        self.on_error_handler = on_error_handler
        self.preverify_request_parameter_encoding = preverify_request_parameter_encoding

    def _is_text_response(self, response):
        return response.content_type is not None and \
               response.content_type.startswith("text")

    def _convert_response_for_docomo(self, response):
        if response.content_type is not None and response.content_type.startswith('text/html'):
            response.content_type = 'application/xhtml+xml'
        return response

    def _convert_response_encoding(self, response):
        if self._is_text_response(response) and response.charset is not None:
            response.unicode_errors = self.errors
            if response.charset != self.encoding:
                response.body = response.text.encode(self.codec, self.errors)
                response.charset = self.encoding
        return response

    def _convert_response(self, mobile_ua, request, response):
        response = self._convert_response_encoding(response)
        if mobile_ua.carrier.is_docomo:
            response = self._convert_response_for_docomo(response)
        return response

    def _revalidate_session(self, request):
        hash = request.session.get(self.hash_key)
        _hash = hashlib.sha1(request.user_agent).hexdigest()
        if hash is not None and hash != _hash:
            logger.error('UA hash mismatch')
            request.session.invalidate()
        request.session[self.hash_key] = _hash

    def _retouch_request(self, request):
        query_string_key = HybridHTTPBackend.get_query_string_key(request)
        session_restorer = HybridHTTPBackend.get_session_restorer(request)
        def decorate(orig):
            def _(*args, **kwargs):
                query = kwargs.setdefault('_query', {})
                if query_string_key and session_restorer:
                    query[query_string_key] = session_restorer
                for k in query:
                    if isinstance(query[k], unicode):
                        query[k] = query[k].encode(self.codec)
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
        request.io_codec = self.codec

    def _attach_smartphone_request_if_necessary(self, mobile_ua, request):
        if smartphone_support_enabled_for(request):
            if mobile_ua.is_smartphone:
                directlyProvides(request, ISmartphoneRequest)
        return request

    def _make_mobile_request(self, request):
        # the following is needed to differentiate the kind of the request in HTTP backend module
        directlyProvides(request, IMobileRequest) # for HybridHTTPSession
        request.copy_body()
        kept_session = request.session
        self._revalidate_session(request)
        noLongerProvides(request, IMobileRequest)
        decoded = request.decode(self.codec, self.errors)
        new_environ = request.environ.copy()
        new_environ.update(decoded.environ)
        decoded.environ = new_environ
        decoded.response_callbacks = request.response_callbacks
        manager.get()['request'] = decoded # hack!
        decoded.is_mobile = True
        directlyProvides(decoded, IMobileRequest)
        decoded.registry = request.registry
        decoded.mobile_ua = getattr(request, 'mobile_ua', None)
        decoded.session = kept_session
        self._retouch_request(decoded)
        return decoded

    def _detect(self, request):
        return detect(request)

    def __call__(self, handler, request):
        mobile_ua = self._detect(request)
        original_request = request
        if not mobile_ua.carrier.is_nonmobile:
            try:
                request = self._make_mobile_request(request)
            except UnicodeDecodeError as e:
                logger.info('error occurred during converting request', exc_info=True)
                if self.on_error_handler is not None:
                    try:
                        request.mobile_ua = mobile_ua
                        return self.on_error_handler(e, request)
                    except Exception as e:
                        logger.exception('exception raised within error handler')
                raise
        else:
            request = self._attach_smartphone_request_if_necessary(mobile_ua, request)

        request.mobile_ua = mobile_ua
        # TODO:remove.
        # cms, usersite compatibility
        request.is_docomo = mobile_ua.carrier.is_docomo
        request.original_request = original_request if request is not original_request else None

        if self.preverify_request_parameter_encoding:
            try:
                request.params
            except UnicodeDecodeError as e:
                if self.on_error_handler is not None:
                    try:
                        return self.on_error_handler(e, request)
                    except Exception as e:
                        logger.exception('exception raised within error handler')
                raise

        response = handler(request)

        if response is not None:
            if not mobile_ua.carrier.is_nonmobile:
                try:
                    response = self._convert_response(mobile_ua, request, response)
                except (UnicodeDecodeError, UnicodeEncodeError) as e:
                    logger.info('error occurred during converting response', exc_info=True)
                    if self.on_error_handler is not None:
                        return self.on_error_handler(e, request)
                    else:
                        raise
        return response

