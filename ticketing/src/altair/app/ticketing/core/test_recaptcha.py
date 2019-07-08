import hashlib
import hmac
from unittest import TestCase

from altair.app.ticketing.core.recaptcha import recaptcha_exempt
from pyramid import testing


class ReCAPTCHAExemptTest(TestCase):
    AUTH_PREFIX = 'RAKUTEN'
    AUTH_KEY = 'wErWhTPn9t8Fc2IaYalQjMB6BfzrCXxVz4Uu5uGp'
    AUTH_SECRET = 'kpu15kPa7IJEId64uGfqrWLfXZDr4UoRv0lnuv2d'

    def setUp(self):
        self.request = testing.DummyRequest()
        self.config = testing.setUp(settings={
            'recaptcha.exempt.targets': 'rakuten-test',
            'recaptcha.exempt.rakuten-test.prefix': self.AUTH_PREFIX,
            'recaptcha.exempt.rakuten-test.auth_key': self.AUTH_KEY,
            'recaptcha.exempt.rakuten-test.auth_secret': self.AUTH_SECRET,
        })

    def test_recaptcha_exempt(self):
        # assert request has valid authorization header
        hasher = hmac.new(self.AUTH_KEY, self.AUTH_SECRET, digestmod=hashlib.sha256)
        self.request.headers['Authorization'] = '{} {}'.format(self.AUTH_PREFIX, hasher.hexdigest())
        self.assertTrue(recaptcha_exempt(self.request))

    def test_invalid_authorization(self):
        # assert request has invalid format of authorization value
        self.request.headers['Authorization'] = 'test'
        self.assertFalse(recaptcha_exempt(self.request))

        # assert request has invalid authorization value
        self.request.headers['Authorization'] = '{} test'.format(self.AUTH_PREFIX)
        self.assertFalse(recaptcha_exempt(self.request))
