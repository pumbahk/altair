from unittest import TestCase

from altair.app.ticketing.cooperation.rakuten_live import actions, models
from altair.app.ticketing.testing import _setup_db, _teardown_db
from requests import Response


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
