import json
from unittest import TestCase

from altair.app.ticketing.cooperation.rakuten_live import actions, models
from altair.app.ticketing.cooperation.rakuten_live.communicator import RakutenLiveApiCode
from altair.app.ticketing.cooperation.rakuten_live.exceptions import RakutenLiveApiRequestFailed, \
    RakutenLiveApiInternalServerError, RakutenLiveApiAccessTokenInvalid
from altair.app.ticketing.testing import _setup_db, _teardown_db
from requests import Response


class MockCommunicator(object):
    def __init__(self, status_code=200, code=1):
        self.status_code = status_code
        self.code = code

    def post(self, data):
        response = Response()
        response.status_code = self.status_code
        response._content = json.dumps({
            'Code': self.code,
            'Data': True,
            'Message': '',
            'CodeDetails': None,
        })
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
        communicator = MockCommunicator()
        actions.send_r_live_data(communicator, {}, self.r_live_session, self.order_entry_no)
        added_data = self.session.query(models.RakutenLiveRequest).filter_by(order_entry_no=self.order_entry_no).one()
        # assert r-live data sent successfully to become with status set to `SENT`
        self.assertEqual(int(models.RakutenLiveStatus.SENT), added_data.status)

    def test_r_live_order_data_failed_to_send_due_to_status_code(self):
        communicator = MockCommunicator(status_code=500, code=1)
        # assert error raised due to bad status code
        self.assertRaises(RakutenLiveApiRequestFailed, actions.send_r_live_data,
                          communicator=communicator, data={},
                          r_live_session=self.r_live_session, order_entry_no=self.order_entry_no)

        added_data = self.session.query(models.RakutenLiveRequest).filter_by(order_entry_no=self.order_entry_no).one()
        # assert r-live data sent successfully to become with status set to `SENT`
        self.assertEqual(int(models.RakutenLiveStatus.UNSENT), added_data.status)

    def test_r_live_order_data_failed_to_send_due_to_bad_code(self):
        for code, excClass in ((int(RakutenLiveApiCode.INTERNAL_SERVER_ERROR), RakutenLiveApiInternalServerError),
                               (int(RakutenLiveApiCode.ACCESS_TOKEN_INVALID), RakutenLiveApiAccessTokenInvalid),
                               (None, RakutenLiveApiRequestFailed)):
            communicator = MockCommunicator(status_code=200, code=code)
            # assert error raised due to bad code
            self.assertRaises(excClass, actions.send_r_live_data,
                              communicator=communicator, data={},
                              r_live_session=self.r_live_session, order_entry_no=self.order_entry_no)

            added_data = self.session.query(models.RakutenLiveRequest).filter_by(order_entry_no=self.order_entry_no).one()
            # assert r-live data sent successfully to become with status set to `SENT`
            self.assertEqual(int(models.RakutenLiveStatus.UNSENT), added_data.status)
            self.session.delete(added_data)
