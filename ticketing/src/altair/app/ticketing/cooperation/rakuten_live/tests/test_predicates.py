from unittest import TestCase

from pyramid.events import NewRequest

from altair.app.ticketing.cooperation.rakuten_live import predicates
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


class RakutenLiveRequestValidTests(TestCase):
    SESSION_KEY = 'rakuten.live.request'
    REFERER = 'https://live.rakuten.co.jp/app-test'
    REQUEST_PARAM = {'user_id': 1, 'stream_id': 3, 'slug': 'test', 'channel_id': 3, 'product_id': 1}

    def setUp(self):
        self.request = testing.DummyRequest(
            post=self.REQUEST_PARAM,
            referer=self.REFERER,
        )
        self.config = testing.setUp(settings={
            'r-live.session_key': self.SESSION_KEY,
            'r-live.referer': self.REFERER,
        })

    @patch('{}.validate_r_live_auth_header'.format(predicates.__name__))
    def test_predicate(self, mock_validate_r_live_auth_header):
        mock_validate_r_live_auth_header.return_value = True
        self.request.registry.registerUtility(MockRoutesMapper(res=True), IRoutesMapper)
        predicate = predicates.RakutenLiveRequestCorrespondingTo('cart.index2', None)
        # assert request is expected state
        self.assertTrue(predicate(NewRequest(self.request)))

        predicate = predicates.RakutenLiveRequestCorrespondingTo('cart.index', None)
        # assert request route is different
        self.assertFalse(predicate(NewRequest(self.request)))

        mock_validate_r_live_auth_header.return_value = False
        predicate = predicates.RakutenLiveRequestCorrespondingTo('cart.index2', None)
        # assert authorization header is different
        self.assertFalse(predicate(NewRequest(self.request)))
