from unittest import TestCase

from requests import Response

from altair.app.ticketing.cooperation.rakuten_live import actions, models
from altair.app.ticketing.testing import _setup_db, _teardown_db
from pyramid.urldispatch import Route

from pyramid.interfaces import IRoutesMapper

from mock import patch

from pyramid import testing


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

    @patch('{}.validate_authorization_header'.format(actions.__name__))
    def test_session_stored(self, mock_validate_auth_header):
        mock_validate_auth_header.return_value = True
        self.request.registry.registerUtility(MockRoutesMapper(res=True), IRoutesMapper)
        actions.store_r_live_request_param(self.request)

        actual_session = self.request.session[self.SESSION_KEY]
        # assert all of post params stored in session
        self.assertTrue(type(actual_session) is models.RakutenLiveSession)
        for k, v in actual_session.as_dict().iteritems():
            self.assertEqual(self.REQUEST_PARAM[k], v)
        # assert performance_id also stored in case of cart url
        self.assertIsNotNone(actual_session.performance_id)
        self.assertIsNone(actual_session.lot_id)

    @patch('{}.validate_authorization_header'.format(actions.__name__))
    def test_session_not_stored(self, mock_validate_auth_header):
        mock_validate_auth_header.return_value = True
        # referer is different
        referer_test_request = self.request
        referer_test_request.referer = 'https://example.com/'
        referer_test_request.registry.registerUtility(MockRoutesMapper(res=True), IRoutesMapper)
        actions.store_r_live_request_param(referer_test_request)
        self.assertIsNone(referer_test_request.session.get(self.SESSION_KEY))

        # route is different
        route_test_request = self.request
        route_test_request.registry.registerUtility(MockRoutesMapper(res=False), IRoutesMapper)
        actions.store_r_live_request_param(route_test_request)
        self.assertIsNone(route_test_request.session.get(self.SESSION_KEY))

        # auth header value is invalid
        auth_header_test_request = self.request
        mock_validate_auth_header.return_value = False
        auth_header_test_request.registry.registerUtility(MockRoutesMapper(res=True), IRoutesMapper)
        actions.store_r_live_request_param(auth_header_test_request)
        self.assertIsNone(auth_header_test_request.session.get(self.SESSION_KEY))


class MockCommunicator(object):
    def __init__(self, res=False):
        self.res = res

    def post(self, data):
        response = Response()
        response.status_code = 200 if self.res else 500
        return response


class RakutenLiveRequestRecordTest(TestCase):
    R_LIVE_PARAM = {'user_id': 1, 'stream_id': 3, 'slug': 'test', 'channel_id': 3, 'product_id': 1}

    def setUp(self):
        self.r_live_session = models.RakutenLiveSession(**self.R_LIVE_PARAM)
        from altair.app.ticketing.orders import models as order_model
        self.session = _setup_db(modules=[order_model.__name__, models.__name__])
        self.order_entry_no = u'RT000000027F'

    def tearDown(self):
        _teardown_db()

    def test_r_live_order_data_sent(self):
        communicator = MockCommunicator(res=True)
        actions.send_r_live_data(communicator, {}, self.r_live_session, self.order_entry_no)
        added_data = self.session.query(models.RakutenLiveRequest).filter_by(order_entry_no=self.order_entry_no).one()
        # assert r-live data sent successfully to become with status set to `SENT`
        self.assertEqual(int(models.RakutenLiveStatus.SENT), added_data.status)

    def test_r_live_order_data_failed_to_send(self):
        communicator = MockCommunicator()
        actions.send_r_live_data(communicator, {}, self.r_live_session, self.order_entry_no)
        added_data = self.session.query(models.RakutenLiveRequest).filter_by(order_entry_no=self.order_entry_no).one()
        # assert r-live data sent successfully to become with status set to `SENT`
        self.assertEqual(int(models.RakutenLiveStatus.UNSENT), added_data.status)
