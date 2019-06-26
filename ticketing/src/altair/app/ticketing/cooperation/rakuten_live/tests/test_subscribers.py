from unittest import TestCase

from pyramid.events import NewRequest

from altair.app.ticketing.cooperation.rakuten_live import subscribers, models
from pyramid.interfaces import IRoutesMapper

from mock import patch

from pyramid import testing
from pyramid.urldispatch import Route


class MockRoutesMapper(object):
    def __init__(self, res=False):
        self.res = res

    def __call__(self, request):
        if self.res:
            return {
                'route': Route(name='cart.index2', pattern='cart/performances/{performance_id}*anything'),
                'match': {'performance_id': u'24', 'anything': ()}
            }
        else:
            return None


class RakutenLiveSessionStoreTests(TestCase):
    SESSION_KEY = 'rakuten.live.request'
    REQUEST_PARAM = {'user_id': 1, 'stream_id': 3, 'slug': 'test', 'channel_id': 3, 'product_id': 1}

    def setUp(self):
        self.request = testing.DummyRequest(
            post=self.REQUEST_PARAM,
        )
        self.config = testing.setUp(settings={
            'r-live.session_key': self.SESSION_KEY,
        })

    @patch('{}.validate_authorization_header'.format(subscribers.__name__))
    def test_session_stored(self, mock_validate_auth_header):
        mock_validate_auth_header.return_value = True
        self.request.registry.registerUtility(MockRoutesMapper(res=True), IRoutesMapper)
        subscribers.r_live_session_store_subscriber(NewRequest(self.request))

        actual_session = self.request.session[self.SESSION_KEY]
        # assert all of post params stored in session
        self.assertTrue(type(actual_session) is models.RakutenLiveSession)
        for k, v in actual_session.as_dict().iteritems():
            self.assertEqual(self.REQUEST_PARAM[k], v)
        # assert performance_id also stored in case of cart url
        self.assertIsNotNone(actual_session.performance_id)
        self.assertIsNone(actual_session.lot_id)

    @patch('{}.validate_authorization_header'.format(subscribers.__name__))
    def test_session_not_stored(self, mock_validate_auth_header):
        # auth header value is invalid
        auth_header_test_request = self.request
        mock_validate_auth_header.return_value = False
        auth_header_test_request.registry.registerUtility(MockRoutesMapper(res=True), IRoutesMapper)
        subscribers.r_live_session_store_subscriber(NewRequest(auth_header_test_request))
        self.assertIsNone(auth_header_test_request.session.get(self.SESSION_KEY))

        # request method is not post
        http_method_test_request = self.request
        http_method_test_request.method = 'GET'
        subscribers.r_live_session_store_subscriber(NewRequest(http_method_test_request))
        self.assertIsNone(http_method_test_request.session.get(self.SESSION_KEY))
