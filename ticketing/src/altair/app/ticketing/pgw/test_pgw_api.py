# -*- coding: utf-8 -*-
import unittest
import mock
import json

from pyramid import testing
from altair.app.ticketing.testing import _setup_db, _teardown_db
from altair.app.ticketing.testing import DummyRequest
from .models import PGWOrderStatus


class PGWFunctionTests(unittest.TestCase):
    def setUp(self):
        self.session = _setup_db([
            'altair.app.ticketing.pgw.models',
        ])

    def tearDown(self):
        testing.tearDown()
        _teardown_db()

    @staticmethod
    def _getTarget():
        from . import api
        return api

    @mock.patch('altair.app.ticketing.pgw.models.PGWOrderStatus.update_pgw_order_status')
    @mock.patch('altair.pgw.api.authorize')
    @mock.patch('altair.app.ticketing.pgw.api.get_pgw_order_status')
    def test_authorize(self, get_pgw_order_status, authorize, update_pgw_order_status):
        """ authorizeメソッドの正常系テスト """
        api = self._getTarget()

        request = DummyRequest()
        payment_id = 'tkt_auth_01'
        email = 'tkt_auth_01@rakuten.com'
        user_id = '100000001'

        get_pgw_order_status.return_value = self._create_pgw_order_status()

        pgw_response = {
            "resultType": "success",
            "transactionTime": "2019-05-01 00:00:00.000",
            "reference": {
                "rakutenCardResult": {
                    "errCd": "000000"
                },
                "hasMemberId": "false"
            },
            "serviceId": "stg-all-webportal",
            "subServiceId": "stg-all-webportal",
            "paymentId": "tkt_auth_01",
            "agencyCode": "rakutencard",
            "agencyRequestId": "tkt_auth_01-01",
            "card": {
                "cardToken": "19051808001KkQY4CTFfNNRen4Il8692",
                "cardBrand": "Visa",
                "brandCode": "Visa",
                "iin": "429769",
                "last4digits": "8692",
                "expirationMonth": "01",
                "expirationYear": "2020",
                "isRakutenCard": "true"
            }
        }

        # PGWの仕様と同様にレスポンスをJSON形式に変換して、受け取ったレスポンスをdictにして返す
        pgw_result = json.dumps(pgw_response)
        authorize.return_value = json.loads(pgw_result)

        update_pgw_order_status.return_value = {}

        api.authorize(request=request, payment_id=payment_id, email=email, user_id=user_id)

    @mock.patch('altair.app.ticketing.pgw.models.PGWOrderStatus.update_pgw_order_status')
    @mock.patch('altair.pgw.api.capture')
    @mock.patch('altair.app.ticketing.pgw.api.get_pgw_order_status')
    def test_capture(self, get_pgw_order_status, capture, update_pgw_order_status):
        """ captureメソッドの正常系テスト """
        api = self._getTarget()

        request = DummyRequest()
        payment_id = 'tkt_capture_01'

        get_pgw_order_status.return_value = self._create_pgw_order_status()

        pgw_response = {
            "resultType": "success",
            "transactionTime": "2019-05-01 00:00:00.000",
            "reference": {
                "rakutenCardCaptureDate": "2019-05-01 00:00:00.000",
                "rakutenCardResult": {
                    "errCd": "000000"
                }
            }
        }

        # PGWの仕様と同様にレスポンスをJSON形式に変換して、受け取ったレスポンスをdictにして返す
        pgw_result = json.dumps(pgw_response)
        capture.return_value = json.loads(pgw_result)

        update_pgw_order_status.return_value = {}

        api.capture(request=request, payment_id=payment_id)

    @mock.patch('altair.app.ticketing.pgw.models.PGWOrderStatus.update_pgw_order_status')
    @mock.patch('altair.pgw.api.authorize_and_capture')
    @mock.patch('altair.app.ticketing.pgw.api.get_pgw_order_status')
    def test_authorize_and_capture(self, get_pgw_order_status, authorize_and_capture, update_pgw_order_status):
        """ authorize_and_captureメソッドの正常系テスト """
        api = self._getTarget()

        request = DummyRequest()
        payment_id = 'tkt_authorize_and_capture_01'
        email = 'tkt_authorize_and_capture_01@rakuten.com'
        user_id = '100000001'

        get_pgw_order_status.return_value = self._create_pgw_order_status()

        pgw_response = {
            "resultType": "success",
            "transactionTime": "2019-05-01 00:00:00.000",
            "reference": {
                "rakutenCardResult": {
                    "errCd": "000000"
                },
                "hasMemberId": "false"
            },
            "serviceId": "stg-all-webportal",
            "subServiceId": "stg-all-webportal",
            "paymentId": "tkt_authorize_and_capture_01",
            "agencyCode": "rakutencard",
            "agencyRequestId": "tkt_authorize_and_capture_01-01",
            "card": {
                "cardToken": "19051808001KkQY4CTFfNNRen4Il8692",
                "cardBrand": "Visa",
                "brandCode": "Visa",
                "iin": "429769",
                "last4digits": "8692",
                "expirationMonth": "01",
                "expirationYear": "2020",
                "isRakutenCard": "true"
            }
        }

        # PGWの仕様と同様にレスポンスをJSON形式に変換して、受け取ったレスポンスをdictにして返す
        pgw_result = json.dumps(pgw_response)
        authorize_and_capture.return_value = json.loads(pgw_result)

        update_pgw_order_status.return_value = {}

        api.authorize_and_capture(request=request, payment_id=payment_id, email=email, user_id=user_id)

    @mock.patch('altair.pgw.api.find')
    def test_find(self, find):
        """ findメソッドの正常系テスト """
        api = self._getTarget()

        request = DummyRequest()
        payment_ids = 'tkt_find_01,tkt_find_02'

        pgw_response = {
            "resultType": "success",
            "transactionTime": "2019-05-01 00:00:00.000",
            "details": [{
                "agencyCode": "rakutencard",
                "serviceId": "stg-all-webportal",
                "subServiceId": "stg-all-webportal",
                "paymentId": "tkt_find_01",
                "paymentMethodCode": "card",
                "paymentStatusType": "initialized",
                "requestType": "cancel_or_refund",
                "grossAmount": "100",
                "currencyCode": "JPY",
                "resultType": "success",
                "transactionTime": "2019-05-01 00:00:00.000",
                "agencyRequestId": "tkt_find_01-01",
                "reference": {
                    "rakutenCardResult": {
                        "errCd": "000000"
                    },
                    "hasMemberId": "false"
                },
                "card": {
                    "cardToken": "19051808001KkQY4CTFfNNRen4Il8692",
                    "iin": "429769",
                    "last4digits": "8692",
                    "expirationMonth": "01",
                    "expirationYear": "2020",
                    "brandCode": "Visa",
                    "isRakutenCard": "true"
                }
            }, {
                "agencyCode": "rakutencard",
                "serviceId": "stg-all-webportal",
                "subServiceId": "stg-all-webportal",
                "paymentId": "tkt_find_02",
                "paymentMethodCode": "card",
                "paymentStatusType": "captured",
                "requestType": "capture",
                "grossAmount": "100",
                "currencyCode": "JPY",
                "resultType": "success",
                "transactionTime": "2019-05-01 00:00:00.000",
                "agencyRequestId": "tkt_find_02-01",
                "reference": {
                    "rakutenCardCaptureDate": "2019-05-01 00:00:00.000",
                    "rakutenCardResult": {
                        "errCd": "000000"
                    },
                    "hasMemberId": "false"
                },
                "card": {
                    "cardToken": "19051808001KkQY4CTFfNNRen4Il8692",
                    "iin": "429769",
                    "last4digits": "8692",
                    "expirationMonth": "01",
                    "expirationYear": "2020",
                    "brandCode": "Visa",
                    "isRakutenCard": "true"
                }
            }]
        }

        # PGWの仕様と同様にレスポンスをJSON形式に変換して、受け取ったレスポンスをdictにして返す
        pgw_result = json.dumps(pgw_response)
        find.return_value = json.loads(pgw_result)

        api.find(request=request, payment_ids=payment_ids)

    @mock.patch('altair.app.ticketing.pgw.models.PGWOrderStatus.update_pgw_order_status')
    @mock.patch('altair.pgw.api.cancel_or_refund')
    @mock.patch('altair.app.ticketing.pgw.api.get_pgw_order_status')
    def test_cancel_or_refund(self, get_pgw_order_status, cancel_or_refund, update_pgw_order_status):
        """ cancel_or_refundメソッドの正常系テスト """
        api = self._getTarget()

        request = DummyRequest()
        payment_id = 'tkt_cancel_or_refund_01'

        get_pgw_order_status.return_value = self._create_pgw_order_status()

        pgw_response = {
            "resultType": "success",
            "transactionTime": "2019-05-01 00:00:00.000",
            "reference": {
                "rakutenCardResult": {
                    "errCd": "000000"
                }
            }
        }

        # PGWの仕様と同様にレスポンスをJSON形式に変換して、受け取ったレスポンスをdictにして返す
        pgw_result = json.dumps(pgw_response)
        cancel_or_refund.return_value = json.loads(pgw_result)

        update_pgw_order_status.return_value = {}

        api.cancel_or_refund(request=request, payment_id=payment_id)

    @mock.patch('altair.app.ticketing.pgw.models.PGWOrderStatus.update_pgw_order_status')
    @mock.patch('altair.pgw.api.modify')
    @mock.patch('altair.app.ticketing.pgw.api.get_pgw_order_status')
    def test_modify(self, get_pgw_order_status, modify, update_pgw_order_status):
        """ modifyメソッドの正常系テスト """
        api = self._getTarget()

        request = DummyRequest()
        payment_id = 'tkt_modify_01'
        modified_amount = 200

        get_pgw_order_status.return_value = self._create_pgw_order_status()

        pgw_response = {
            "resultType": "success",
            "transactionTime": "2019-05-01 00:00:00.000",
            "reference": {
                "rakutenCardResult": {
                    "errCd": "000000"
                },
                "hasMemberId": "false"
            },
            "paymentId": "tkt_modify_01",
            "agencyCode": "rakutencard",
            "agencyRequestId": "tkt_modify_01-01",
            "subServiceId": "stg-all-webportal",
            "paymentStatusType": "authorized",
            "requestType": "modify",
            "grossAmount": "50",
            "currencyCode": "JPY",
            "paymentMethodCode": "card",
            "card": {
                "cardToken": "19051808001KkQY4CTFfNNRen4Il8692",
                "cardBrand": "Visa",
                "brandCode": "Visa",
                "iin": "429769",
                "last4digits": "8692",
                "expirationMonth": "01",
                "expirationYear": "2020",
                "isRakutenCard": "true"
            },
            "serviceId": "stg-all-webportal"
        }

        # PGWの仕様と同様にレスポンスをJSON形式に変換して、受け取ったレスポンスをdictにして返す
        pgw_result = json.dumps(pgw_response)
        modify.return_value = json.loads(pgw_result)

        update_pgw_order_status.return_value = {}

        api.modify(request=request, payment_id=payment_id, modified_amount=modified_amount)

    @mock.patch('altair.app.ticketing.pgw.models.PGWOrderStatus.update_pgw_order_status')
    @mock.patch('altair.pgw.api.three_d_secure_enrollment_check')
    @mock.patch('altair.app.ticketing.pgw.api.get_pgw_order_status')
    def test_three_d_secure_enrollment_check(self, get_pgw_order_status,
                                             three_d_secure_enrollment_check, update_pgw_order_status):
        """ three_d_secure_enrollment_checkメソッドの正常系テスト """
        api = self._getTarget()

        request = DummyRequest()
        payment_id = 'tkt_3d_enrollment_check_01'
        callback_url = 'http://rt.stg.altr.jp/'

        get_pgw_order_status.return_value = self._create_pgw_order_status()

        pgw_response = {
            "resultType": "success",
            "transactionTime": "2019-05-01 00:00:00.000",
        }

        # PGWの仕様と同様にレスポンスをJSON形式に変換して、受け取ったレスポンスをdictにして返す
        pgw_result = json.dumps(pgw_response)
        three_d_secure_enrollment_check.return_value = json.loads(pgw_result)

        update_pgw_order_status.return_value = {}

        api.three_d_secure_enrollment_check(request=request, payment_id=payment_id, callback_url=callback_url)

    @staticmethod
    def _create_pgw_order_status():
        return PGWOrderStatus(
            pgw_sub_service_id='stg-all-webportal',
            gross_amount=100,
            card_token='19051807001VmIB9HzS6s8zL7ZdY8692',
            cvv_token=''
        )




