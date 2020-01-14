# coding=utf-8
import inspect
import urllib2
from datetime import datetime, timedelta

import mock
from altair.skidata.api import make_whitelist, make_event_ts_property, make_blacklist
from altair.skidata.exceptions import SkidataWebServiceError
from altair.skidata.interfaces import ISkidataSession
from altair.skidata.marshaller import SkidataXmlMarshaller
from altair.skidata.models import TSOption, TSAction, ProcessRequestResponse, Envelope, Body, HSHData, Error, \
    HSHErrorType, HSHErrorNumber, BlockingReason
from altair.skidata.sessions import XML_ENCODING
from altair.skidata.tests.tests import SkidataBaseTest
from pyramid import testing


class MockResponse(object):
    def __init__(self, status_code, model):
        self._status_code = status_code
        self._text = SkidataXmlMarshaller.marshal(model, encoding=XML_ENCODING)

    def getcode(self):
        return self._status_code

    def read(self):
        return self._text


class SkidataWebServiceSessionTest(SkidataBaseTest):
    def setUp(self):
        settings = {
            'altair.skidata.webservice.timeout': '20',
            'altair.skidata.webservice.url': 'http://localhost/ImporterWebService',
            'altair.skidata.webservice.header.version': 'HSHIF25',
            'altair.skidata.webservice.header.issuer': '1',
            'altair.skidata.webservice.header.receiver': '1',
        }
        self.config = testing.setUp(settings=settings)
        self.config.include('altair.skidata.sessions')
        self.request = testing.DummyRequest()

        self.event_start_date = datetime(2020, 8, 5, 12, 30, 0)
        self.event_id = 'RE{start_date}'.format(start_date=self.event_start_date.strftime('%Y%m%d%H%M%S'))

    def _make_header(self, header_id=None):
        session = self.request.registry.getUtility(ISkidataSession)
        return session.make_header(header_id=header_id)

    def _make_mock_response(self, error=None):
        process_response = ProcessRequestResponse()
        envelope = Envelope(body=Body(process_response=process_response))

        hsh_data = HSHData(header=self._make_header(), error=error)
        marshaled_hsh_data = SkidataXmlMarshaller.marshal(hsh_data, XML_ENCODING)
        process_response.set_hsh_data(marshaled_hsh_data.decode(XML_ENCODING))
        return MockResponse(status_code=200, model=envelope)

    def _make_ts_option(self, order_no, seat_name):
        return TSOption(
            order_no=order_no,
            open_date=self.event_start_date - timedelta(hours=1),
            start_date=self.event_start_date,
            stock_type=u'1塁側指定席',
            product_name=u'1塁側指定席',
            product_item_name=u'1塁側指定席',
            gate='GATE A',
            seat_name=seat_name,
            sales_segment=u'一般発売',
            ticket_type=0,
            person_category=1,
            event=self.event_id
        )

    def _send_data_and_assert(self, event_ts_property=None, whitelist=None, blacklist=None, assert_func=None):
        # Get a session from utilities
        session = self.request.registry.getUtility(ISkidataSession)
        # Send a data to HSH
        resp = session.send(event_ts_property=event_ts_property, whitelist=whitelist, blacklist=blacklist)

        # print(resp.text)

        # Assert the status code
        self.assertEqual(resp.status_code, 200)

        hsh_data = resp.hsh_data
        header = hsh_data.header()
        expected_header = self._make_header()

        # Assert Header Element
        self.assertEqual(expected_header.version(), header.version())
        self.assertEqual(expected_header.issuer(), header.issuer())
        self.assertEqual(expected_header.receiver(), header.receiver())

        if inspect.isfunction(assert_func):
            # custom function for assertion
            assert_func(resp)

    @mock.patch('altair.skidata.sessions.urllib2.urlopen')
    def test_insert_events_scenario(self, mock_url_open):
        # success case
        mock_url_open.return_value = self._make_mock_response()

        # event expire is the end of the year when the skidata event starts
        expire = datetime(year=self.event_start_date.year, month=12, day=31, hour=23, minute=59, second=59)

        event_ts_property = [
            make_event_ts_property(
                action=TSAction.INSERT,
                event_id=self.event_id,
                name=u'東北楽天ゴールデンイーグルス vs 北海道日本ハムファイターズ',
                expire=expire,
                start_date_or_time=self.event_start_date.date()
            )
        ]

        second_start_date = datetime(2020, 9, 5, 12, 30, 0)
        second_event_id = 'RE{start_date}'.format(start_date=second_start_date.strftime('%Y%m%d%H%M%S'))
        # event expire is the end of the year when the skidata event starts
        second_expire = datetime(year=second_start_date.year, month=12, day=31, hour=23, minute=59, second=59)

        event_ts_property.append(
            make_event_ts_property(
                action=TSAction.INSERT,
                event_id=second_event_id,
                name=u'東北楽天ゴールデンイーグルス vs 埼玉西武ライオンズ',
                expire=second_expire,
                start_date_or_time=second_start_date.date()
            )
        )

        self._send_data_and_assert(event_ts_property=event_ts_property)

        # error case: All events not inserted
        error = [
            Error(type_=HSHErrorType.STOP, number=HSHErrorNumber.HSH_INTERNAL_ERROR,
                  description='HSH internal error', event_ts_property=ts_property)
            for ts_property in event_ts_property
        ]
        mock_url_open.return_value = self._make_mock_response(error=error)

        def assert_error(resp):
            self.assertTrue(len(resp.errors) == len(event_ts_property))
            for e in resp.errors:
                self.assertEqual(HSHErrorType.STOP, e.type())
                self.assertEqual(HSHErrorNumber.HSH_INTERNAL_ERROR, e.number())
                self.assertEqual('HSH internal error', e.description())
                self.assertTrue(e.event_ts_property().property_id() in (self.event_id, second_event_id))

        self._send_data_and_assert(event_ts_property=event_ts_property, assert_func=assert_error)

    @mock.patch('altair.skidata.sessions.urllib2.urlopen')
    def test_insert_whitelist_scenario(self, mock_url_open):
        # success case
        mock_url_open.return_value = self._make_mock_response()

        # whitelist expire is the end of the year when the skidata event starts
        expire = datetime(year=self.event_start_date.year, month=12, day=31, hour=23, minute=59, second=59)

        qr_code = '97SEJPEMBI8IH134859255TMQ'
        first_whitelist = make_whitelist(action=TSAction.INSERT, qr_code=qr_code,
                                         ts_option=self._make_ts_option('RE0000000001', u'A列 10'), expire=expire)

        second_whitelist = make_whitelist(action=TSAction.INSERT, qr_code='97WOI33F4I8IH134834255TMW',
                                          ts_option=self._make_ts_option('RE0000000002', u'A列 11'), expire=expire)

        whitelist = [first_whitelist, second_whitelist]
        self._send_data_and_assert(whitelist=whitelist)

        # error case: one whitelist not inserted
        error = Error(type_=HSHErrorType.ERROR, number=HSHErrorNumber.INVALID_DATA_TYPE,
                      description='Invalid Data Type', whitelist=first_whitelist)

        mock_url_open.return_value = self._make_mock_response(error=error)

        def assert_error(resp):
            self.assertTrue(len(resp.errors), 1)

            _error = resp.hsh_data.error()
            self.assertEqual(HSHErrorType.ERROR, _error.type())
            self.assertEqual(HSHErrorNumber.INVALID_DATA_TYPE, _error.number())
            self.assertEqual('Invalid Data Type', _error.description())
            self.assertEqual(qr_code, _error.whitelist().utid())

        self._send_data_and_assert(whitelist=whitelist, assert_func=assert_error)

    @mock.patch('altair.skidata.sessions.urllib2.urlopen')
    def test_delete_whitelist_scenario(self, mock_url_open):
        # success case
        mock_url_open.return_value = self._make_mock_response()

        qr_code = '97SEJPEMBI8IH134859255TMQ'
        whitelist = make_whitelist(action=TSAction.DELETE, qr_code=qr_code)

        self._send_data_and_assert(whitelist=whitelist)

        # error case: whitelist not deleted
        error = Error(type_=HSHErrorType.STOP, number=HSHErrorNumber.HSH_INTERNAL_ERROR,
                      description='HSH internal error', whitelist=whitelist)

        mock_url_open.return_value = self._make_mock_response(error=error)

        def assert_error(resp):
            self.assertTrue(len(resp.errors), 1)

            _error = resp.hsh_data.error()
            self.assertEqual(HSHErrorType.STOP, _error.type())
            self.assertEqual(HSHErrorNumber.HSH_INTERNAL_ERROR, _error.number())
            self.assertEqual('HSH internal error', _error.description())
            self.assertEqual(qr_code, _error.whitelist().utid())

        self._send_data_and_assert(whitelist=whitelist, assert_func=assert_error)

    @mock.patch('altair.skidata.sessions.urllib2.urlopen')
    def test_insert_blacklist_scenario(self, mock_url_open):
        # success case
        mock_url_open.return_value = self._make_mock_response()

        # blacklist expire is the end of the year when the skidata event starts
        expire = datetime(year=self.event_start_date.year, month=12, day=31, hour=23, minute=59, second=59)

        qr_code = '97SEJPEMBI8IH134859255TMQ'
        blacklist = make_blacklist(action=TSAction.INSERT, qr_code=qr_code,
                                   blocking_reason=BlockingReason.CANCELED, expire=expire)

        self._send_data_and_assert(blacklist=blacklist)

        # error case: blacklist not inserted
        error = Error(type_=HSHErrorType.ERROR, number=HSHErrorNumber.NON_EXISTING_PERMISSION,
                      description='Non Existing Permission', blacklist=blacklist)

        mock_url_open.return_value = self._make_mock_response(error=error)

        def assert_error(resp):
            self.assertTrue(len(resp.errors), 1)

            _error = resp.hsh_data.error()
            self.assertEqual(HSHErrorType.ERROR, _error.type())
            self.assertEqual(HSHErrorNumber.NON_EXISTING_PERMISSION, _error.number())
            self.assertEqual('Non Existing Permission', _error.description())
            self.assertEqual(qr_code, _error.blacklist().blocking_whitelist().utid())

        self._send_data_and_assert(blacklist=blacklist, assert_func=assert_error)

    @mock.patch('altair.skidata.sessions.urllib2.urlopen')
    def test_delete_blacklist_scenario(self, mock_url_open):
        # success case
        mock_url_open.return_value = self._make_mock_response()

        qr_code = '97SEJPEMBI8IH134859255TMQ'
        blacklist = make_blacklist(action=TSAction.DELETE, qr_code=qr_code,
                                   blocking_reason=BlockingReason.CANCELED)

        self._send_data_and_assert(blacklist=blacklist)

        # error case: blacklist not deleted
        error = Error(type_=HSHErrorType.ERROR, number=HSHErrorNumber.NON_EXISTING_PERMISSION,
                      description='Non Existing Permission', blacklist=blacklist)

        mock_url_open.return_value = self._make_mock_response(error=error)

        def assert_error(resp):
            self.assertTrue(len(resp.errors), 1)

            _error = resp.hsh_data.error()
            self.assertEqual(HSHErrorType.ERROR, _error.type())
            self.assertEqual(HSHErrorNumber.NON_EXISTING_PERMISSION, _error.number())
            self.assertEqual('Non Existing Permission', _error.description())
            self.assertEqual(qr_code, _error.blacklist().blocking_whitelist().utid())

        self._send_data_and_assert(blacklist=blacklist, assert_func=assert_error)

    @mock.patch('altair.skidata.sessions.urllib2.urlopen')
    def test_send_ts_data_and_raise_error(self, mock_url_open):
        mock_url_open.side_effect = urllib2.URLError('an error occurred')
        session = self.request.registry.getUtility(ISkidataSession)
        self.assertRaises(SkidataWebServiceError, session.send)
