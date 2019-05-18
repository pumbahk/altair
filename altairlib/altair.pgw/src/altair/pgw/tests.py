# -*- coding: utf-8 -*-
import unittest
import mock

from pyramid import testing


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
        return api.authorize(*args, **kwargs)

    def test_it(self):
        sub_service_id = "stg-all-webportal"
        payment_id = ''
        gross_amount = 100
        card_amount = 100
        card_token = ''
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
        return api.capture(*args, **kwargs)

    def test_it(self):
        payment_id = ''
        capture_amount = 100

        request = testing.DummyRequest()
        result = self._callFUT(
            request=request,
            payment_id=payment_id,
            capture_amount=capture_amount
        )
        print(result)


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
        return api.authorize_and_capture(*args, **kwargs)

    def test_it(self):
        sub_service_id = "stg-all-webportal"
        payment_id = 'TKT000005'
        gross_amount = 500
        card_amount = 500
        card_token = '19050903001ak6dP5BOhNaVu0AJP3426'
        cvv_token = 'cvv_e7983e8bc84e47319dd32f5eb130777f'
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
        return api.find(*args, **kwargs)

    def test_it(self):
        # 複数の場合は'a,b,c'のようなカンマ区切りで記述してください
        target_payment_id = ''
        payment_ids = target_payment_id.split(',')
        search_type = 'current'

        request = testing.DummyRequest()
        result = self._callFUT(
            request=request,
            payment_ids=payment_ids,
            search_type=search_type
        )
        print(result)


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
        return api.cancel_or_refund(*args, **kwargs)

    def test_it(self):
        payment_id = ''

        request = testing.DummyRequest()
        result = self._callFUT(
            request=request,
            payment_id=payment_id
        )
        print(result)


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
        return api.modify(*args, **kwargs)

    def test_it(self):
        payment_id = ''
        modified_amount = 300

        request = testing.DummyRequest()
        result = self._callFUT(
            request=request,
            payment_id=payment_id,
            modified_amount=modified_amount
        )
        print(result)


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

    def test_it(self):
        sub_service_id = "stg-all-webportal"
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
