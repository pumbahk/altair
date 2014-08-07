from unittest import TestCase
from pyramid import testing 
import mock

class RegressionTest(TestCase):
    def setUp(self):
        config = testing.setUp()
        config.include('.'.join(__name__.split('.')[0:-1]))
        self.config = config

    def tearDown(self):
        testing.tearDown()

    def test_detect_from_email_address(self):
        from .api import detect_from_email_address
        from .carriers import NonMobile, DoCoMo
        self.assertEqual(
            detect_from_email_address(self.config.registry, 'test@example.com'),
            NonMobile)
        self.assertEqual(
            detect_from_email_address(self.config.registry, 'test@docomo.ne.jp'),
            DoCoMo)

    def test_middleware_hybrid(self):
        from .api import get_middleware
        from . import install_mobile_middleware
        from .session import HybridHTTPBackend
        from .interfaces import ISmartphoneSupportPredicate
        from pyramid.request import Request, Response
        install_mobile_middleware(self.config)
        self.config.registry.registerUtility(
            lambda request: False,
            ISmartphoneSupportPredicate
            )
        request = Request(
            environ={
                'QUERY_STRING': 'a=b&c=d&e=f&g=h+i&k=l%20m',
                'HTTP_USER_AGENT': 'DoCoMo/2.0',
                }
            )
        request.registry = self.config.registry
        request.session = testing.DummySession()
        request.mobile_ua = testing.DummyModel(
            carrier=testing.DummyModel(
                is_docomo=True
                )
            )

        def handler(request):
            self.assertEqual(request.params['a'], 'b')
            self.assertEqual(request.params['c'], 'd')
            self.assertTrue('e' not in request.params)
            self.assertEqual(request.params['g'], 'h i')
            self.assertEqual(request.params['k'], 'l m')
            return Response()

        HybridHTTPBackend(request, 'e')
        middleware = get_middleware(request)
        middleware(handler, request)


class MobileMiddlewareTest(TestCase):
    def setUp(self):
        config = testing.setUp()
        self.config = config

    def tearDown(self):
        testing.tearDown()

    def _getTarget(self):
        from .middleware import MobileMiddleware
        return MobileMiddleware

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_revalidate_session1(self):
        import hashlib
        request = mock.MagicMock()
        request.user_agent = 'USER_AGENT'
        request.session.get.return_value = hashlib.sha1('USER_AGENT').hexdigest()
        target = self._makeOne()
        target._revalidate_session(request)
        request.session.get.assert_called_with_argument('altair.mobile.impl.us_hash')
        request.session.invalidate.assert_not_called()

    def test_revalidate_session2(self):
        import hashlib
        request = mock.MagicMock()
        request.user_agent = 'USER_AGENT'
        request.session.get.return_value = hashlib.sha1('OOPS').hexdigest()
        target = self._makeOne()
        target._revalidate_session(request)
        request.session.get.assert_called_with_argument('altair.mobile.impl.us_hash')
        request.session.invalidate.assert_called()

    def test_smartphone_predicate_1(self):
        from .interfaces import IMobileCarrierDetector, ISmartphoneSupportPredicate, ISmartphoneRequest
        from pyramid.testing import DummyRequest
        detector = mock.Mock()
        detector.detect_from_wsgi_environment.return_value.carrier.is_nonmobile = True
        request = DummyRequest()
        request.registry.registerUtility(
            detector,
            IMobileCarrierDetector
            )
        request.registry.registerUtility(
            lambda request: False,
            ISmartphoneSupportPredicate
            )
        target = self._makeOne()
        def handler(request):
            self.assertFalse(ISmartphoneRequest.providedBy(request))
            return None
        target(handler, request)

    def test_smartphone_predicate_2(self):
        from .interfaces import IMobileCarrierDetector, ISmartphoneSupportPredicate, ISmartphoneRequest
        from pyramid.testing import DummyRequest
        detector = mock.Mock()
        detector.detect_from_wsgi_environment.return_value.carrier.is_nonmobile = True
        request = DummyRequest()
        request.user_agent = 'Dummy'
        request.decode = lambda *args: request
        request.registry.registerUtility(
            detector,
            IMobileCarrierDetector
            )
        request.registry.registerUtility(
            lambda request: True,
            ISmartphoneSupportPredicate
            )
        target = self._makeOne()
        def handler(request):
            self.assertTrue(ISmartphoneRequest.providedBy(request))
            return None
        target(handler, request)

        detector.detect_from_wsgi_environment.return_value.carrier.is_nonmobile = False
        target = self._makeOne()
        def handler(request):
            self.assertFalse(ISmartphoneRequest.providedBy(request))
            return None
        target(handler, request)

    def test_decode_fail(self):
        from .interfaces import IMobileCarrierDetector, ISmartphoneSupportPredicate, ISmartphoneRequest
        from pyramid.request import Request
        from pyramid.testing import DummySession
        detector = mock.Mock()
        detector.detect_from_wsgi_environment.return_value.carrier.is_nonmobile = False
        session = DummySession()
        from altair.extracodecs import register_codecs
        register_codecs()
        self.config.set_session_factory(lambda request: session)
        self.config.registry.registerUtility(
            detector,
            IMobileCarrierDetector
            )
        self.config.registry.registerUtility(
            lambda request: False,
            ISmartphoneSupportPredicate
            )
        on_error_handler = mock.Mock()
        target = self._makeOne(
            encoding='Shift_JIS',
            on_error_handler=on_error_handler
            )
        request = Request(environ={
            'HTTP_USER_AGENT': 'DoCoMo/2.0 ',
            'QUERY_STRING': b'a=\x81\x31',
            })
        request.registry = self.config.registry
        target(lambda request: None, request)
        self.assertTrue(on_error_handler.called)
