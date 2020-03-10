# -*- coding:utf-8 -*-

import unittest
from altair.app.ticketing.testing import DummyRequest, _setup_db, _teardown_db
import mock
from pyramid.testing import DummyModel


class PaymentGatewayCreditCardViewTest(unittest.TestCase):

    @staticmethod
    def _getTestTarget(*args, **kwargs):
        from .. import pgw_credit_card
        return pgw_credit_card.PaymentGatewayCreditCardView(*args, **kwargs)

    @mock.patch('altair.app.ticketing.payments.plugins.pgw_credit_card.cart_api.get_or_create_user')
    def test_show_card_form(self, get_or_create_user):
        """ show_card_formの正常系テスト """
        request = DummyRequest(
            session={},
            altair_auth_info=u'test_info'
        )
        get_or_create_user.return_value = None
        test_view = self._getTestTarget(request)

        card_form_dict = test_view.show_card_form()
        self.assertIsNotNone(card_form_dict)
        self.assertIsNotNone(card_form_dict.get('form'))
        self.assertIsNone(card_form_dict.get('latest_card_info'))

    @mock.patch('altair.app.ticketing.payments.plugins.pgw_credit_card.pgw_api.get_pgw_masked_card_detail')
    @mock.patch('altair.app.ticketing.payments.plugins.pgw_credit_card.cart_api.get_or_create_user')
    def test_show_card_form_with_latest_card_info(self, get_or_create_user, get_pgw_masked_card_detail):
        """ show_card_formの正常系テスト """
        request = DummyRequest(
            session={},
            altair_auth_info=u'test_info'
        )
        get_or_create_user.return_value = DummyModel(id=123456)
        test_card_brand_code = u'VISA'
        test_card_last4digits = u'2222'
        test_card_expiration_month=u'05'
        test_card_expiration_year=u'2025'
        get_pgw_masked_card_detail.return_value = DummyModel(
            card_brand_code=test_card_brand_code,
            card_last4digits=test_card_last4digits,
            card_expiration_month=test_card_expiration_month,
            card_expiration_year=test_card_expiration_year
        )
        test_view = self._getTestTarget(request)

        card_form_dict = test_view.show_card_form()
        self.assertIsNotNone(card_form_dict)
        self.assertIsNotNone(card_form_dict.get('form'))
        self.assertEqual(card_form_dict.get('latest_card_info'),
                         u'{} {} {}/{}'.format(test_card_brand_code, test_card_last4digits, test_card_expiration_month,
                                               test_card_expiration_year))

    def test_redirect_card_form_with_payment_error(self):
        from pyramid.httpexceptions import HTTPFound

        test_flash_msg = []

        def mock_flash(msg):
            test_flash_msg.append(msg)

        def mock_route_url(arg1):
            return 'http://dummy_route_url'

        request = DummyRequest(
            session=DummyModel(
                flash=mock_flash
            ),
            route_url=mock_route_url
        )

        test_view = self._getTestTarget(request)
        http_exception = test_view.redirect_card_form_with_payment_error()
        self.assertIsInstance(http_exception, HTTPFound)
        self.assertTrue(len(test_flash_msg) > 0)

    @mock.patch('altair.app.ticketing.payments.plugins.pgw_credit_card.get_confirm_url')
    @mock.patch('altair.app.ticketing.payments.plugins.pgw_credit_card.pgw_api.initialize_pgw_order_status')
    @mock.patch('altair.formhelpers.form.SecureFormMixin._validate_csrf_token')
    @mock.patch('altair.app.ticketing.payments.plugins.pgw_credit_card.get_cart')
    def test_process_card_token_using_new_card(self, get_cart, _validate_csrf_token, initialize_pgw_order_status,
                                               get_confirm_url):
        """ process_card_tokenの正常系テスト 新規カード利用"""
        from pyramid.httpexceptions import HTTPFound
        test_order_no = u'TEST000001'
        test_params = {
            u'radioBtnUseCard': u'new_card',
            u'cardToken': u'test_card_token',
            u'cvvToken': u'test_cvv_token',
            u'last4digits': u'1234',
            u'expirationYear': u'2100',
            u'expirationMonth': u'08'
        }
        request = DummyRequest(
            session={},
            params=test_params,
            organization=DummyModel(
                setting=DummyModel(
                    pgw_sub_service_id=u'12345'
                )
            )
        )
        _validate_csrf_token.return_value = True
        get_cart.return_value = DummyModel(
            order_no=test_order_no,
            payment_amount=1000
        )
        initialize_pgw_order_status.return_value= None
        get_confirm_url.return_value = u'http://example.com'
        test_view = self._getTestTarget(request)

        http_exception = test_view.process_card_token()
        self.assertIsInstance(http_exception, HTTPFound)
        safe_card_info = request.session.get(u'pgw_safe_card_info_{}'.format(test_order_no))
        self.assertIsNotNone(safe_card_info)
        self.assertEqual(safe_card_info[u'last4digits'], test_params[u'last4digits'])
        self.assertEqual(safe_card_info[u'expirationYear'], test_params[u'expirationYear'])
        self.assertEqual(safe_card_info[u'expirationMonth'], test_params[u'expirationMonth'])

    @mock.patch('altair.formhelpers.form.SecureFormMixin._validate_csrf_token')
    @mock.patch('altair.app.ticketing.payments.plugins.pgw_credit_card.get_cart')
    def test_process_card_token_validation_error_using_new_card(self, get_cart, _validate_csrf_token):
        """ process_card_tokenの異常系テスト 新規カード利用でバリデーションエラー"""
        from altair.app.ticketing.payments.plugins.pgw_credit_card import PgwCardPaymentPluginFailure
        test_order_no = u'TEST000001'
        test_params = {
            u'radioBtnUseCard': u'new_card'
        }
        request = DummyRequest(
            session={},
            params=test_params
        )
        _validate_csrf_token.return_value = True
        get_cart.return_value = DummyModel(
            order_no=test_order_no
        )
        test_view = self._getTestTarget(request)

        with self.assertRaises(PgwCardPaymentPluginFailure):
            test_view.process_card_token()
        safe_card_info = request.session.get(u'pgw_safe_card_info_{}'.format(test_order_no))
        self.assertIsNone(safe_card_info)

    @mock.patch('altair.formhelpers.form.SecureFormMixin._validate_csrf_token')
    @mock.patch('altair.app.ticketing.payments.plugins.pgw_credit_card.get_cart')
    def test_process_card_token_payvault_error_using_new_card(self, get_cart, _validate_csrf_token):
        """ process_card_tokenの異常系テスト 新規カード利用でPayVaultエラー"""
        from altair.app.ticketing.payments.plugins.pgw_credit_card import PgwCardPaymentPluginFailure
        test_order_no = u'TEST000001'
        test_params = {
            u'radioBtnUseCard': u'new_card',
            u'errorCode': 'test-error',
            u'errorMessage': 'test-error occurred'
        }
        request = DummyRequest(
            session={},
            params=test_params
        )
        _validate_csrf_token.return_value = True
        get_cart.return_value = DummyModel(
            order_no=test_order_no
        )
        test_view = self._getTestTarget(request)

        with self.assertRaises(PgwCardPaymentPluginFailure):
            test_view.process_card_token()
        safe_card_info = request.session.get(u'pgw_safe_card_info_{}'.format(test_order_no))
        self.assertIsNone(safe_card_info)

    @mock.patch('altair.formhelpers.form.SecureFormMixin._validate_csrf_token')
    @mock.patch('altair.app.ticketing.payments.plugins.pgw_credit_card.get_cart')
    def test_process_card_token_payvault_invalid_request_parameter_using_new_card(self, get_cart, _validate_csrf_token):
        """ process_card_tokenの異常系テスト 新規カード利用でPayVault invalid_parameter_error """
        from pyramid.httpexceptions import HTTPFound

        class MockSession(dict):
            def __init__(self):
                self.flash_message = []

            def flash(self, msg):
                self.flash_message.append(msg)

        def mock_route_url(arg1):
            return u'http://example.com'

        test_order_no = u'TEST000001'
        test_params = {
            u'radioBtnUseCard': u'new_card',
            u'errorCode': 'invalid_request_parameter',
            u'errorMessage': 'invalid_parameter_error occurred'
        }
        request = DummyRequest(
            session=MockSession(),
            params=test_params,
            route_url=mock_route_url
        )
        _validate_csrf_token.return_value = True
        get_cart.return_value = DummyModel(
            order_no=test_order_no
        )
        test_view = self._getTestTarget(request)

        view_data = test_view.process_card_token()
        self.assertIsInstance(view_data, HTTPFound)
        self.assertTrue(len(request.session.flash_message) > 0)

    @mock.patch('altair.app.ticketing.payments.plugins.pgw_credit_card.get_confirm_url')
    @mock.patch('altair.app.ticketing.payments.plugins.pgw_credit_card.pgw_api.initialize_pgw_order_status')
    @mock.patch('altair.app.ticketing.payments.plugins.pgw_credit_card.pgw_api.get_pgw_masked_card_detail')
    @mock.patch('altair.app.ticketing.payments.plugins.pgw_credit_card.cart_api.get_or_create_user')
    @mock.patch('altair.formhelpers.form.SecureFormMixin._validate_csrf_token')
    @mock.patch('altair.app.ticketing.payments.plugins.pgw_credit_card.get_cart')
    def test_process_card_token_using_latest_card(self, get_cart, _validate_csrf_token, get_or_create_user,
                                                  get_pgw_masked_card_detail, initialize_pgw_order_status,
                                                  get_confirm_url):
        """ process_card_tokenの正常系テスト 前回カード利用"""
        from pyramid.httpexceptions import HTTPFound
        test_order_no = u'TEST000001'
        test_params = {
            u'radioBtnUseCard': u'latest_card',
            u'cvvToken': u'test_cvv_token'
        }
        request = DummyRequest(
            session={},
            params=test_params,
            organization=DummyModel(
                setting=DummyModel(
                    pgw_sub_service_id=u'12345'
                )
            ),
            altair_auth_info=u'test_auth_info'
        )
        _validate_csrf_token.return_value = True
        get_cart.return_value = DummyModel(
            order_no=test_order_no,
            payment_amount=1000
        )
        get_or_create_user.return_value = DummyModel(id=12345)
        test_card_last4digits = u'2222'
        test_card_expiration_month = u'05'
        test_card_expiration_year = u'2025'
        test_card_token = u'test_card_token'
        get_pgw_masked_card_detail.return_value = DummyModel(
            card_last4digits=test_card_last4digits,
            card_expiration_month=test_card_expiration_month,
            card_expiration_year=test_card_expiration_year,
            card_token=test_card_token
        )
        initialize_pgw_order_status.return_value = None
        get_confirm_url.return_value = u'http://example.com'
        test_view = self._getTestTarget(request)

        http_exception = test_view.process_card_token()
        self.assertIsInstance(http_exception, HTTPFound)
        safe_card_info = request.session.get(u'pgw_safe_card_info_{}'.format(test_order_no))
        self.assertEqual(safe_card_info[u'last4digits'], test_card_last4digits)
        self.assertEqual(safe_card_info[u'expirationYear'], test_card_expiration_year)
        self.assertEqual(safe_card_info[u'expirationMonth'], test_card_expiration_month)

    @mock.patch('altair.formhelpers.form.SecureFormMixin._validate_csrf_token')
    @mock.patch('altair.app.ticketing.payments.plugins.pgw_credit_card.get_cart')
    def test_process_card_token_validation_error_using_latest_card(self, get_cart, _validate_csrf_token):
        """ process_card_tokenの異常系テスト 前回カード利用でバリデーションエラー"""
        from altair.app.ticketing.payments.plugins.pgw_credit_card import PgwCardPaymentPluginFailure
        test_order_no = u'TEST000001'
        test_params = {
            u'radioBtnUseCard': u'latest_card'
        }
        request = DummyRequest(
            session={},
            params=test_params
        )
        _validate_csrf_token.return_value = True
        get_cart.return_value = DummyModel(
            order_no=test_order_no
        )
        test_view = self._getTestTarget(request)

        with self.assertRaises(PgwCardPaymentPluginFailure):
            test_view.process_card_token()
        safe_card_info = request.session.get(u'pgw_safe_card_info_{}'.format(test_order_no))
        self.assertIsNone(safe_card_info)

    @mock.patch('altair.formhelpers.form.SecureFormMixin._validate_csrf_token')
    @mock.patch('altair.app.ticketing.payments.plugins.pgw_credit_card.get_cart')
    def test_process_card_token_payvault_error_using_latest_card(self, get_cart, _validate_csrf_token):
        """ process_card_tokenの異常系テスト 前回カード利用でPayVaultエラー"""
        from altair.app.ticketing.payments.plugins.pgw_credit_card import PgwCardPaymentPluginFailure
        test_order_no = u'TEST000001'
        test_params = {
            u'radioBtnUseCard': u'latest_card',
            u'errorCode': 'test-error',
            u'errorMessage': 'test-error occurred'
        }
        request = DummyRequest(
            session={},
            params=test_params
        )
        _validate_csrf_token.return_value = True
        get_cart.return_value = DummyModel(
            order_no=test_order_no
        )
        test_view = self._getTestTarget(request)

        with self.assertRaises(PgwCardPaymentPluginFailure):
            test_view.process_card_token()
        safe_card_info = request.session.get(u'pgw_safe_card_info_{}'.format(test_order_no))
        self.assertIsNone(safe_card_info)

    @mock.patch('altair.formhelpers.form.SecureFormMixin._validate_csrf_token')
    @mock.patch('altair.app.ticketing.payments.plugins.pgw_credit_card.get_cart')
    def test_process_card_token_payvault_invalid_request_parameter_using_latest_card(self, get_cart, _validate_csrf_token):
        """ process_card_tokenの異常系テスト 前回カード利用でPayVaultエラー"""
        from pyramid.httpexceptions import HTTPFound

        class MockSession(dict):
            def __init__(self):
                self.flash_message = []

            def flash(self, msg):
                self.flash_message.append(msg)

        def mock_route_url(arg1):
            return u'http://example.com'

        test_order_no = u'TEST000001'
        test_params = {
            u'radioBtnUseCard': u'latest_card',
            u'errorCode': 'invalid_request_parameter',
            u'errorMessage': 'test-error occurred'
        }
        request = DummyRequest(
            session=MockSession(),
            params=test_params,
            route_url=mock_route_url
        )
        _validate_csrf_token.return_value = True
        get_cart.return_value = DummyModel(
            order_no=test_order_no
        )
        test_view = self._getTestTarget(request)

        view_data = test_view.process_card_token()
        self.assertIsInstance(view_data, HTTPFound)
        self.assertTrue(len(request.session.flash_message) > 0)

    @mock.patch('altair.app.ticketing.payments.plugins.pgw_credit_card.pgw_api.get_pgw_masked_card_detail')
    @mock.patch('altair.app.ticketing.payments.plugins.pgw_credit_card.cart_api.get_or_create_user')
    @mock.patch('altair.formhelpers.form.SecureFormMixin._validate_csrf_token')
    @mock.patch('altair.app.ticketing.payments.plugins.pgw_credit_card.get_cart')
    def test_process_card_token_using_latest_card_with_no_user(
            self, get_cart, _validate_csrf_token, get_or_create_user,get_pgw_masked_card_detail):
        """ process_card_tokenの正常系テスト 前回カード利用"""
        from pyramid.httpexceptions import HTTPFound
        test_order_no = u'TEST000001'
        test_params = {
            u'radioBtnUseCard': u'latest_card',
            u'cvvToken': u'test_cvv_token'
        }

        class MockSession(dict):
            def __init__(self):
                self.flash_message = []

            def flash(self, msg):
                self.flash_message.append(msg)

        def mock_route_url(arg1):
            return u'http://example.com'

        request = DummyRequest(
            session=MockSession(),
            params=test_params,
            organization=DummyModel(
                setting=DummyModel(
                    pgw_sub_service_id=u'12345'
                )
            ),
            altair_auth_info=u'test_auth_info',
            route_url=mock_route_url
        )
        _validate_csrf_token.return_value = True
        get_cart.return_value = DummyModel(
            order_no=test_order_no,
            payment_amount=1000
        )
        get_or_create_user.return_value = None
        test_view = self._getTestTarget(request)

        view_data = test_view.process_card_token()
        self.assertIsInstance(view_data, HTTPFound)
        self.assertTrue(len(request.session.flash_message) > 0)
        self.assertFalse(get_pgw_masked_card_detail.called)

    @mock.patch('altair.app.ticketing.payments.plugins.pgw_credit_card.pgw_api.get_pgw_masked_card_detail')
    @mock.patch('altair.app.ticketing.payments.plugins.pgw_credit_card.cart_api.get_or_create_user')
    @mock.patch('altair.formhelpers.form.SecureFormMixin._validate_csrf_token')
    @mock.patch('altair.app.ticketing.payments.plugins.pgw_credit_card.get_cart')
    def test_process_card_token_using_latest_card_with_no_pgw_masked_card_detail(
            self, get_cart, _validate_csrf_token, get_or_create_user, get_pgw_masked_card_detail):
        """ process_card_tokenの正常系テスト 前回カード利用"""
        from pyramid.httpexceptions import HTTPFound
        test_order_no = u'TEST000001'
        test_params = {
            u'radioBtnUseCard': u'latest_card',
            u'cvvToken': u'test_cvv_token'
        }

        class MockSession(dict):
            def __init__(self):
                self.flash_message = []

            def flash(self, msg):
                self.flash_message.append(msg)

        def mock_route_url(arg1):
            return u'http://example.com'

        request = DummyRequest(
            session=MockSession(),
            params=test_params,
            organization=DummyModel(
                setting=DummyModel(
                    pgw_sub_service_id=u'12345'
                )
            ),
            altair_auth_info=u'test_auth_info',
            route_url=mock_route_url
        )
        _validate_csrf_token.return_value = True
        get_cart.return_value = DummyModel(
            order_no=test_order_no,
            payment_amount=1000
        )
        get_or_create_user.return_value = DummyModel(id=12345)
        get_pgw_masked_card_detail.return_value = None
        test_view = self._getTestTarget(request)

        view_data = test_view.process_card_token()
        self.assertIsInstance(view_data, HTTPFound)
        self.assertTrue(len(request.session.flash_message) > 0)
