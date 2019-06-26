import hashlib
import hmac
from unittest import TestCase

from altair.app.ticketing.cooperation.rakuten_live.models import RakutenLiveSession
from altair.app.ticketing.cooperation.rakuten_live.utils import get_r_live_session, pop_r_live_session, \
    has_r_live_session, validate_authorization_header, is_r_live_referer
from pyramid import testing


class RakutenLiveRequestTest(TestCase):
    SECRET_KEY = 'rakuten.live.request'
    API_KEY = 'wErWhTPn9t8Fc2IaYalQjMB6BfzrCXxVz4Uu5uGp'
    API_SECRET = 'kpu15kPa7IJEId64uGfqrWLfXZDr4UoRv0lnuv2d'
    REFERER = 'https://live.rakuten.co.jp/app-test'

    def setUp(self):
        self.request = testing.DummyRequest(
            session={self.SECRET_KEY: RakutenLiveSession()},
            referer=self.REFERER,
        )
        self.config = testing.setUp(settings={
            'r-live.session_key': self.SECRET_KEY,
            'r-live.api_key': self.API_KEY,
            'r-live.api_secret': self.API_SECRET,
            'r-live.referer': self.REFERER,
        })
        self._set_auth_header()

    def _set_auth_header(self):
        hasher = hmac.new(self.API_KEY, self.API_SECRET, digestmod=hashlib.sha256)
        self.request.headers['Authorization'] = 'LIVE {}'.format(hasher.hexdigest())

    def test_check_session_existence(self):
        actual = get_r_live_session(self.request)
        # assert request has session key to store RakutenLiveSession model
        self.assertEqual(RakutenLiveSession, type(actual))
        self.assertTrue(has_r_live_session(self.request))

        request = self.request
        del request.session[self.SECRET_KEY]
        # assert request has no session key to store RakutenLiveSession model
        self.assertIsNone(get_r_live_session(request))
        self.assertFalse(has_r_live_session(request))

    def test_pop_session(self):
        actual = pop_r_live_session(self.request)
        # assert session key to store RakutenLiveSession model is popped from request
        self.assertEqual(RakutenLiveSession, type(actual))
        self.assertIsNone(self.request.session.get(self.SECRET_KEY))

        # assert None returned as there is no corresponding session key
        self.assertIsNone(pop_r_live_session(self.request))

    def test_referer(self):
        # assert request referer is R-Live
        self.assertTrue(is_r_live_referer(self.request))

        request = self.request
        request.referer = 'http://example.com'
        # assert request referer is not R-Live
        self.assertFalse(is_r_live_referer(request))

    def test_auth_header(self):
        # assert the same hasing value is generated
        self.assertTrue(validate_authorization_header(self.request))
