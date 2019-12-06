# coding=utf-8
import urllib2
from datetime import datetime

from lxml import etree

import mock
from altair.skidata.api import make_whitelist
from altair.skidata.exceptions import SkidataWebServiceError
from altair.skidata.interfaces import ISkidataSession
from altair.skidata.marshaller import SkidataXmlMarshaller
from altair.skidata.models import TSOption, TSAction, ProcessRequestResponse, Envelope, Body, HSHData, Error, \
    HSHErrorType, HSHErrorNumber
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
            'altair.skidata.webservice.enabled': 'true',
            'altair.skidata.webservice.header.version': 'HSHIF25',
            'altair.skidata.webservice.header.issuer': '1',
            'altair.skidata.webservice.header.receiver': '1',
        }
        self.config = testing.setUp(settings=settings)
        self.config.include('altair.skidata.sessions')
        self.request = testing.DummyRequest()

        start_date = datetime(2020, 8, 5, 12, 30, 0)
        event_id = 'RE{start_date}'.format(start_date=start_date.strftime('%Y%m%d%H%M%S'))

        self.ts_option = TSOption(
            order_no='RE0000000001',
            open_date=datetime(2020, 8, 5, 11, 0, 0),
            start_date=start_date,
            stock_type=u'1塁側指定席',
            product_name=u'1塁側指定席',
            product_item_name=u'1塁側指定席',
            gate='GATE A',
            seat_name=u'指定席',
            sales_segment=u'一般発売',
            ticket_type=0,
            person_category=1,
            event=event_id
        )

    def _make_header(self, request_id=None):
        session = self.request.registry.getUtility(ISkidataSession)
        return session.make_header(request_id=request_id)

    def _make_response(self, request_id=None, error=None):
        process_response = ProcessRequestResponse()
        envelope = Envelope(body=Body(process_response=process_response))

        hsh_data = HSHData(header=self._make_header(request_id))
        if isinstance(error, Error):
            hsh_data.set_error(error)

        marshaled_hsh_data = SkidataXmlMarshaller.marshal(hsh_data, XML_ENCODING)
        process_response.set_hsh_data(marshaled_hsh_data.decode(XML_ENCODING))
        return MockResponse(status_code=200, model=envelope)

    @mock.patch('altair.skidata.sessions.urllib2.urlopen')
    def test_send_ts_data_and_get_hsh_data(self, mock_url_open):
        mock_url_open.return_value = self._make_response()

        expire = datetime(year=datetime.now().year, month=12, day=31, hour=23, minute=59, second=59)
        whitelist = [
            make_whitelist(action=TSAction.INSERT, qr_code='97SEJPEMBI8IH134859255TMQ',
                           ts_option=self.ts_option, expire=expire),
            make_whitelist(action=TSAction.INSERT, qr_code='97WOI33F4I8IH134834255TMW',
                           ts_option=self.ts_option, expire=expire),
        ]

        session = self.request.registry.getUtility(ISkidataSession)
        resp = session.send(whitelist=whitelist)

        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.success)

        hsh_data = resp.hsh_data
        # print(resp.text)

        header_elem = etree.fromstring(SkidataXmlMarshaller.marshal(self._make_header()))
        self.assert_header(hsh_data.header(), header_elem)
        self.assertIsNone(hsh_data.error())

    @mock.patch('altair.skidata.sessions.urllib2.urlopen')
    def test_send_ts_data_and_get_hsh_data_with_error(self, mock_url_open):
        # Set invalid action value `X`
        whitelist = [
            make_whitelist(action='X', ts_option=self.ts_option, qr_code='97SEJPEMBI8IH134859255TMB',
                           expire=datetime(2019, 12, 2, 0, 0, 0)),
        ]

        request_id = 1
        error = Error(type_=HSHErrorType.ERROR, number=HSHErrorNumber.INVALID_ACTION_TYPE,
                      description='Invalid Action Type', whitelist=whitelist)
        mock_url_open.return_value = self._make_response(request_id, error)

        session = self.request.registry.getUtility(ISkidataSession)
        resp = session.send(request_id=request_id, whitelist=whitelist)

        self.assertEqual(resp.status_code, 200)
        self.assertFalse(resp.success)

        hsh_data = resp.hsh_data
        # print(resp.text)

        header_elem = etree.fromstring(SkidataXmlMarshaller.marshal(self._make_header(request_id)))
        self.assert_header(hsh_data.header(), header_elem)

        error_elem = etree.fromstring(SkidataXmlMarshaller.marshal(error))
        self.assert_error(resp.errors()[0], error_elem)

        hsh_data_elem = etree.fromstring(SkidataXmlMarshaller.marshal(resp.hsh_data))
        self.assert_whitelist(whitelist[0], hsh_data_elem.find('Error'))

    @mock.patch('altair.skidata.sessions.urllib2.urlopen')
    def test_send_ts_data_and_raise_error(self, mock_url_open):
        mock_url_open.side_effect = urllib2.URLError('an error occurred')
        session = self.request.registry.getUtility(ISkidataSession)
        self.assertRaises(SkidataWebServiceError, session.send, request_id=1)
