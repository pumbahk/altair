# -*- coding: utf-8 -*-
import unittest
import mock
import json

from pyramid import testing

# STG環境のPGWのAPIと実際に通信する場合はTrueに書き換えてください
API_CALL = True

"""
STG環境のPGWと疎通する場合

カードトークンを取得する必要があります
一度取得したトークンは有効期限等制限がないので今後継続して利用可能です

セキュリティコードのトークンはワンタイムトークンのため
毎回新規でトークン化してAPIをコールする必要があります
対象：authorize, authorize_and_capture

トークン化する場合は以下のコマンドを実行してください
※カード番号や有効期限, セキュリティコードは適宜書き換えてください

# カードも一緒にトークン化する場合
curl https://payvault-stg.global.rakuten.com/api/pv/Card/V3/Add \
-i \
-H "Content-Type: application/json;charset=utf-8"  \
-d '{                   
 "serviceId": "stg-all-webportal",                        
 "timestamp": "2019-05-01 00:00:00.000",                
 "fullCardDetails":                              
   {                                                  
    "expirationYear": "2020",
    "expirationMonth": "01",
    "cardNumber": "4297690077068692",
    "cvv": "123"                           
   }                                                      
}'

# セキュリティコードのみトークン化する場合
curl https://payvault-stg.global.rakuten.com/api/pv/Card/V3/Add \
-i \
-H "Content-Type: application/json;charset=utf-8"  \
-d '{                   
 "serviceId": "stg-all-webportal",                        
 "timestamp": "2019-05-01 00:00:00.000",                
 "fullCardDetails":                              
   {                                                  
     "cvv": "123"                           
   }                                                      
}'

"""


class AuthorizeTest(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.config.registry.settings = {
            'altair.pgw.authentication_key': '455FD3D78FD5E295C6D3DCD7AFC8D81484CC30BE0DDFA9A1D997C739039024DD',
            'altair.pgw.endpoint': 'https://payment-stg.global.rakuten.com/gp',
            'altair.pgw.service_id': 'stg-all-webportal',
            'altair.pgw.timeout': 20
        }
        self.config.include('altair.pgw')

    def _callFUT(self, *args, **kwargs):
        from . import api
        if not API_CALL:
            pgw_dummy_result = mock.MagicMock(return_value=self.create_authorize_response())
            api.authorize = pgw_dummy_result
        return api.authorize(*args, **kwargs)

    def test_authorize(self):
        """ authorizeの正常系テスト """
        sub_service_id = 'stg-all-webportal'
        payment_id = 'tkt_authorize_test'
        gross_amount = 100
        card_amount = 100
        card_token = '19051807001VmIB9HzS6s8zL7ZdY8692'
        cvv_token = ''
        email = 'stg-hrs01@rakuten.com'

        request = testing.DummyRequest()
        result = self._callFUT(
            request=request,
            sub_service_id=sub_service_id,
            payment_id=payment_id,
            gross_amount=gross_amount,
            card_amount=card_amount,
            card_token=card_token,
            cvv_token=cvv_token,
            email=email
        )
        print(result)
        self.assertEqual(result['resultType'], u'success')

    @staticmethod
    def create_authorize_response():
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
            "paymentId": "tkt_authorize_test",
            "agencyCode": "rakutencard",
            "agencyRequestId": "tkt_authorize_test-01",
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
        return json.loads(pgw_result)


class CaptureTest(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.config.registry.settings = {
            'altair.pgw.authentication_key': '455FD3D78FD5E295C6D3DCD7AFC8D81484CC30BE0DDFA9A1D997C739039024DD',
            'altair.pgw.endpoint': 'https://payment-stg.global.rakuten.com/gp',
            'altair.pgw.service_id': 'stg-all-webportal',
            'altair.pgw.timeout': 20
        }
        self.config.include('altair.pgw')

    def _callFUT(self, *args, **kwargs):
        from . import api
        if not API_CALL:
            pgw_dummy_result = mock.MagicMock(return_value=self.create_capture_response())
            api.capture = pgw_dummy_result
        return api.capture(*args, **kwargs)

    def test_capture(self):
        """ captureの正常系テスト """
        payment_id = 'tkt_capture_test'
        capture_amount = 100

        request = testing.DummyRequest()
        result = self._callFUT(
            request=request,
            payment_id=payment_id,
            capture_amount=capture_amount
        )
        print(result)
        self.assertEqual(result['resultType'], u'success')

    @staticmethod
    def create_capture_response():
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
        return json.loads(pgw_result)


class AuthorizeAndCaptureTest(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.config.registry.settings = {
            'altair.pgw.authentication_key': '455FD3D78FD5E295C6D3DCD7AFC8D81484CC30BE0DDFA9A1D997C739039024DD',
            'altair.pgw.endpoint': 'https://payment-stg.global.rakuten.com/gp',
            'altair.pgw.service_id': 'stg-all-webportal',
            'altair.pgw.timeout': 20
        }
        self.config.include('altair.pgw')

    def _callFUT(self, *args, **kwargs):
        from . import api
        if not API_CALL:
            pgw_dummy_result = mock.MagicMock(return_value=self.create_authorize_and_capture_response())
            api.authorize_and_capture = pgw_dummy_result
        return api.authorize_and_capture(*args, **kwargs)

    def test_authorize_and_capture(self):
        """ authorize_and_captureの正常系テスト """
        sub_service_id = 'stg-all-webportal'
        payment_id = 'tkt_authorize_and_capture_test'
        gross_amount = 500
        card_amount = 500
        card_token = '19051808001KkQY4CTFfNNRen4Il8692'
        cvv_token = ''
        email = 'stg-hrs01@rakuten.com'

        request = testing.DummyRequest()
        result = self._callFUT(
            request=request,
            sub_service_id=sub_service_id,
            payment_id=payment_id,
            gross_amount=gross_amount,
            card_amount=card_amount,
            card_token=card_token,
            cvv_token=cvv_token,
            email=email
        )
        print(result)
        self.assertEqual(result['resultType'], u'success')

    @staticmethod
    def create_authorize_and_capture_response():
        pgw_response = {
            "resultType": "success",
            "transactionTime": "2019-05-01 00:00:00.000",
            "reference": {
                "rakutenCardCaptureDate": "2019-05-01 00:00:00.000",
                "rakutenCardResult": {
                    "errCd": "000000"
                },
                "hasMemberId": "false"
            },
            "serviceId": "stg-all-webportal",
            "subServiceId": "stg-all-webportal",
            "paymentId": "tkt_authorize_and_capture_test",
            "agencyCode": "rakutencard",
            "agencyRequestId": "tkt_authorize_and_capture_test-01",
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
        return json.loads(pgw_result)


class FindTest(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.config.registry.settings = {
            'altair.pgw.authentication_key': '455FD3D78FD5E295C6D3DCD7AFC8D81484CC30BE0DDFA9A1D997C739039024DD',
            'altair.pgw.endpoint': 'https://payment-stg.global.rakuten.com/gp',
            'altair.pgw.service_id': 'stg-all-webportal',
            'altair.pgw.timeout': 20
        }
        self.config.include('altair.pgw')

    def _callFUT(self, *args, **kwargs):
        from . import api
        if not API_CALL:
            pgw_dummy_result = mock.MagicMock(return_value=self.create_find_response())
            api.find = pgw_dummy_result
        return api.find(*args, **kwargs)

    def test_find(self):
        """ findの正常系テスト """
        # 複数の場合は'a,b,c'のようなカンマ区切りで記述してください
        target_payment_id = 'TKT000013'
        payment_ids = target_payment_id.split(',')
        search_type = 'current'

        request = testing.DummyRequest()
        result = self._callFUT(
            request=request,
            payment_ids=payment_ids,
            search_type=search_type
        )
        print(result)
        self.assertEqual(result['resultType'], u'success')

    @staticmethod
    def create_find_response():
        """
        payment_idsを複数指定した場合(2件)のレスポンスを生成しています
        """
        pgw_response = {
            "resultType": "success",
            "transactionTime": "2019-05-01 00:00:00.000",
            "details": [{
                "agencyCode": "rakutencard",
                "serviceId": "stg-all-webportal",
                "subServiceId": "stg-all-webportal",
                "paymentId": "tkt_find_test_1",
                "paymentMethodCode": "card",
                "paymentStatusType": "initialized",
                "requestType": "cancel_or_refund",
                "grossAmount": "100",
                "currencyCode": "JPY",
                "resultType": "success",
                "transactionTime": "2019-05-01 00:00:00.000",
                "agencyRequestId": "tkt_find_test_1-01",
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
                "paymentId": "tkt_find_test_2",
                "paymentMethodCode": "card",
                "paymentStatusType": "captured",
                "requestType": "capture",
                "grossAmount": "100",
                "currencyCode": "JPY",
                "resultType": "success",
                "transactionTime": "2019-05-01 00:00:00.000",
                "agencyRequestId": "tkt_find_test_2-01",
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
        return json.loads(pgw_result)


class CancelOrRefundTest(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.config.registry.settings = {
            'altair.pgw.authentication_key': '455FD3D78FD5E295C6D3DCD7AFC8D81484CC30BE0DDFA9A1D997C739039024DD',
            'altair.pgw.endpoint': 'https://payment-stg.global.rakuten.com/gp',
            'altair.pgw.service_id': 'stg-all-webportal',
            'altair.pgw.timeout': 20
        }
        self.config.include('altair.pgw')

    def _callFUT(self, *args, **kwargs):
        from . import api
        if not API_CALL:
            pgw_dummy_result = mock.MagicMock(return_value=self.create_cancel_or_refund_response())
            api.cancel_or_refund = pgw_dummy_result
        return api.cancel_or_refund(*args, **kwargs)

    def test_cancel_or_refund(self):
        """ cancel_or_refundの正常系テスト """
        payment_id = 'tkt_cancel_or_refund_test'

        request = testing.DummyRequest()
        result = self._callFUT(
            request=request,
            payment_id=payment_id
        )
        print(result)
        self.assertEqual(result['resultType'], u'success')

    @staticmethod
    def create_cancel_or_refund_response():
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
        return json.loads(pgw_result)


class ModifyTest(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.config.registry.settings = {
            'altair.pgw.authentication_key': '455FD3D78FD5E295C6D3DCD7AFC8D81484CC30BE0DDFA9A1D997C739039024DD',
            'altair.pgw.endpoint': 'https://payment-stg.global.rakuten.com/gp',
            'altair.pgw.service_id': 'stg-all-webportal',
            'altair.pgw.timeout': 20
        }
        self.config.include('altair.pgw')

    def _callFUT(self, *args, **kwargs):
        from . import api
        if not API_CALL:
            pgw_dummy_result = mock.MagicMock(return_value=self.create_modify_response())
            api.modify = pgw_dummy_result
        return api.modify(*args, **kwargs)

    def test_modify(self):
        """ modifyの正常系テスト """
        payment_id = 'tkt_modify_test'
        modified_amount = 50

        request = testing.DummyRequest()
        result = self._callFUT(
            request=request,
            payment_id=payment_id,
            modified_amount=modified_amount
        )
        print(result)
        self.assertEqual(result['resultType'], u'success')

    @staticmethod
    def create_modify_response():
        pgw_response = {
            "resultType": "success",
            "transactionTime": "2019-05-01 00:00:00.000",
            "reference": {
                "rakutenCardResult": {
                    "errCd": "000000"
                },
                "hasMemberId": "false"
            },
            "paymentId": "tkt_modify_test",
            "agencyCode": "rakutencard",
            "agencyRequestId": "tkt_modify_test-01",
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
        return json.loads(pgw_result)


class ThreeDSecureEnrollmentCheck(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.config.registry.settings = {
            'altair.pgw.authentication_key': '455FD3D78FD5E295C6D3DCD7AFC8D81484CC30BE0DDFA9A1D997C739039024DD',
            'altair.pgw.endpoint': 'https://payment-stg.global.rakuten.com/gp',
            'altair.pgw.service_id': 'stg-all-webportal',
            'altair.pgw.timeout': 20
        }
        self.config.include('altair.pgw')

    def _callFUT(self, *args, **kwargs):
        from . import api
        return api.three_d_secure_enrollment_check(*args, **kwargs)

    def test_three_d_secure_enrollment_check(self):
        """ three_d_secure_enrollment_checkの正常系テスト """
        sub_service_id = 'stg-all-webportal'
        enrollment_id = ''
        callback_url = 'http://rt.stg.altr.jp/'
        amount = 100
        card_token = ''

        request = testing.DummyRequest()
        result = self._callFUT(
            request=request,
            sub_service_id=sub_service_id,
            enrollment_id=enrollment_id,
            callback_url=callback_url,
            amount=amount,
            card_token=card_token
        )
        print(result)
        self.assertEqual(result['resultType'], u'success')
