# -*- coding:utf8 -*-

import unittest
from pyramid import testing
from pyramid.testing import DummySession
from ...testing import DummyRequest
from ...multicheckout.testing import DummySecure3D
from ...multicheckout.api import Checkout3D
import mock

class MultiCheckoutViewTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self._register_dummy_card_brand_detector()

    def tearDown(self):
        testing.tearDown()

    def _getTarget(self):
        from . import multicheckout
        return multicheckout.MultiCheckoutView

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def _register_dummy_card_brand_detector(self):
        from ticketing.multicheckout.interfaces import ICardBrandDetecter
        self.config.registry.utilities.register([], ICardBrandDetecter, "", lambda card_number: "TEST")

    @mock.patch('wtforms.ext.csrf.SecureForm.validate')
    @mock.patch('ticketing.multicheckout.api.Checkout3D.secure3d_enrol')
    @mock.patch('ticketing.multicheckout.api.get_multicheckout_service')
    @mock.patch('ticketing.multicheckout.api.save_api_response')
    def test_card_info_secure3d_enable_api(self, save_api_response, get_multicheckout_service, secure3d_enrol, validate):
        from ...multicheckout import models as mc_models
        get_multicheckout_service.return_value = Checkout3D(
            auth_id='auth_id',
            auth_password='password',
            shop_code='000000',
            api_base_url='http://example.com/'
            )
        secure3d_enrol.return_value = mc_models.Secure3DReqEnrolResponse(
            ErrorCd='000000',
            RetCd='0',
            AcsUrl='http://example.com/AcsUrl',
            Md='this-is-Md',
            PaReq='this-is-pareq'
            )
        validate.return_value = True
        self.config.registry.settings['altair_cart.expire_time'] = 15
        self.config.add_route('cart.secure3d_result', '/this-is-secure3d-callback')
        params = {
            'card_number': 'XXXXXXXXXXXXXXXX',
            'exp_year': '13',
            'exp_month': '07',
            'client_name': u'楽天太郎',
            'card_holder_name': u'RAKUTEN TAROU',
            'email_1': u'ticketstar@example.com',
            }

        cart_id = 500
        dummy_cart = testing.DummyModel(
            id=cart_id,
            total_amount=1234,
            is_expired=lambda self, *args: False,
            finished_at=None,
            order_no='000000000000'
            )

        request = DummyRequest(params=params, _cart=dummy_cart)
        request.session['order'] = {}
        target = self._makeOne(request)

        result = target.card_info_secure3d()

        self.assertEqual(result.text.strip(), """
<form name='PAReqForm' method='POST' action='http://example.com/AcsUrl'>
        <input type='hidden' name='PaReq' value='this-is-pareq'>
        <input type='hidden' name='TermUrl' value='http://example.com/this-is-secure3d-callback'>
        <input type='hidden' name='MD' value='this-is-Md'>
        </form>
        <script type='text/javascript'>function onLoadHandler(){document.PAReqForm.submit();};window.onload = onLoadHandler; </script>
        """.strip())

        session_order = request.session['order']
        self.assertEqual(session_order['card_number'], 'XXXXXXXXXXXXXXXX')
        self.assertEqual(session_order['exp_year'], '13')
        self.assertEqual(session_order['exp_month'], '07')
        self.assertEqual(session_order['card_holder_name'], u'RAKUTEN TAROU')

    @mock.patch('wtforms.ext.csrf.SecureForm.validate')
    @mock.patch('ticketing.multicheckout.api.Checkout3D.request_card_auth')
    @mock.patch('ticketing.multicheckout.api.Checkout3D.secure3d_enrol')
    @mock.patch('ticketing.multicheckout.api.get_multicheckout_service')
    @mock.patch('ticketing.multicheckout.api.save_api_response')
    def test_card_info_secure3d_disabled_api(self, save_api_response, get_multicheckout_service, secure3d_enrol, request_card_auth, validate):
        from ...multicheckout import models as mc_models
        get_multicheckout_service.return_value = Checkout3D(
            auth_id='auth_id',
            auth_password='password',
            shop_code='000000',
            api_base_url='http://example.com/'
            )
        secure3d_enrol.return_value = mc_models.Secure3DReqEnrolResponse(
            ErrorCd='000000',
            RetCd='4',
            AcsUrl='http://example.com/AcsUrl',
            Md='this-is-Md',
            PaReq='this-is-pareq'
            )
        request_card_auth.return_value = mc_models.MultiCheckoutResponseCard(
            CmnErrorCd='000000')
        validate.return_value = True
        self.config.registry.settings['altair_cart.expire_time'] = 15
        self.config.registry.settings['cart.item_name'] = '楽天チケット' # configはバイト読み取り
        self.config.add_route('cart.secure3d_result', '/this-is-secure3d-callback')
        params = {
            'card_number': 'XXXXXXXXXXXXXXXX',
            'exp_year': '13',
            'exp_month': '07',
            'client_name': u'楽天太郎',
            'card_holder_name': u'RAKUTEN TAROU',
            'email_1': u'ticketstar@example.com',
        }

        cart_id = 500
        dummy_cart = testing.DummyModel(
            id=cart_id,
            total_amount=1234,
            is_expired=lambda self, *args: False,
            finished_at=None,
            order_no='000000000000',
            performance=testing.DummyModel(id=1)
            )

        request = DummyRequest(
            params=params,
            _cart=dummy_cart,
            session=DummySession(
                order=params,
                payment_confirm_url='http://example.com/payment_confirm'
                )
            )
        target = self._makeOne(request)

        result = target.card_info_secure3d()
        self.assertTrue(secure3d_enrol.called)
        self.assertTrue(request_card_auth.called)

    @mock.patch('wtforms.ext.csrf.SecureForm.validate')
    @mock.patch('ticketing.multicheckout.api.Checkout3D.request_card_auth')
    @mock.patch('ticketing.multicheckout.api.Checkout3D.secure3d_enrol')
    @mock.patch('ticketing.multicheckout.api.get_multicheckout_service')
    @mock.patch('ticketing.multicheckout.api.save_api_response')
    def test_card_info_secure3d_disabled_api_fail(self, save_api_response, get_multicheckout_service, secure3d_enrol, request_card_auth, validate):
        from ...multicheckout import models as mc_models
        get_multicheckout_service.return_value = Checkout3D(
            auth_id='auth_id',
            auth_password='password',
            shop_code='000000',
            api_base_url='http://example.com/'
            )
        secure3d_enrol.return_value = mc_models.Secure3DReqEnrolResponse(
            ErrorCd='000000',
            RetCd='4',
            AcsUrl='http://example.com/AcsUrl',
            Md='this-is-Md',
            PaReq='this-is-pareq'
            )
        request_card_auth.return_value = mc_models.MultiCheckoutResponseCard(
            CmnErrorCd='000001')
        validate.return_value = True
        self.config.registry.settings['altair_cart.expire_time'] = 15
        self.config.registry.settings['cart.item_name'] = '楽天チケット' # configはバイト読み取り
        self.config.add_route('payment.secure3d', 'secure3d')
        self.config.add_route('cart.secure3d_result', '/this-is-secure3d-callback')
        params = {
            'card_number': 'XXXXXXXXXXXXXXXX',
            'exp_year': '13',
            'exp_month': '07',
            'client_name': u'楽天太郎',
            'card_holder_name': u'RAKUTEN TAROU',
            'email_1': u'ticketstar@example.com',
        }

        cart_id = 500
        dummy_cart = testing.DummyModel(
            id=cart_id,
            total_amount=1234,
            is_expired=lambda self, *args: False,
            finished_at=None,
            order_no='000000000000',
            performance=testing.DummyModel(id=1)
            )

        request = DummyRequest(
            params=params,
            _cart=dummy_cart,
            session=DummySession(
                order=params,
                payment_confirm_url='http://example.com/payment_confirm'
                )
            )
        target = self._makeOne(request)

        from multicheckout import MultiCheckoutSettlementFailure
        with self.assertRaises(MultiCheckoutSettlementFailure) as m:
            target.card_info_secure3d()
        self.assertEqual(m.exception.error_code, '000001')


    @mock.patch('ticketing.multicheckout.api.Checkout3D.request_card_auth')
    @mock.patch('ticketing.multicheckout.api.Checkout3D.secure3d_auth')
    @mock.patch('ticketing.multicheckout.api.get_multicheckout_service')
    @mock.patch('ticketing.multicheckout.api.save_api_response')
    def test_card_info_secure3d_callback(self, save_api_response, get_multicheckout_service, secure3d_auth, request_card_auth):
        from ...multicheckout import models as mc_models
        get_multicheckout_service.return_value = Checkout3D(
            auth_id='auth_id',
            auth_password='password',
            shop_code='000000',
            api_base_url='http://example.com/'
            )
        secure3d_auth.return_value = mc_models.Secure3DAuthResponse(
            ErrorCd='000000',
            RetCd='0'
            )
        request_card_auth.return_value = mc_models.MultiCheckoutResponseCard(
            CmnErrorCd='000000')

        self.config.registry.settings['altair_cart.expire_time'] = 15
        # dummy rakuten user
        self.config.add_route('payment.secure3d', 'secure3d')
        userdata = {'clamed_id': 'http://example.com/this-is-openid'}
        import pickle
        userdata = pickle.dumps(userdata).encode('base64')
        self.config.testing_securitypolicy(userid=userdata)
        self.config.registry.settings['cart.item_name'] = '楽天チケット' # configはバイト読み取り
        params = {
            'PaRes': 'this-is-pa-res',
            'MD': 'this-is-md',
        }
        cart_id = 500
        dummy_cart = testing.DummyModel(
            id=cart_id,
            total_amount=1234,
            performance=testing.DummyModel(id=100, name=u'テスト公演'),
            products=[],
            is_expired=lambda self, now: False,
            finished_at=None,
            order_no='000000000000'
        )
        dummy_cart.finish = lambda: None

        session_order = {
            'client_name': u'楽天太郎',
            'email_1': u'ticketstar@example.com',
            'card_number': u'XXXXXXXXXXXXXXXX',
            'exp_year': '12',
            'exp_month': '06',
            'card_holder_name': u'RAKUTEN TAROU',
        }
        request = DummyRequest(
            params=params,
            _cart=dummy_cart,
            session=DummySession(
                order=session_order,
                payment_confirm_url='http://example.com/payment_confirm'
                ))
        target = self._makeOne(request)

        result = target.card_info_secure3d_callback()

        self.assertEqual(result.location, 'http://example.com/payment_confirm')

    @mock.patch('ticketing.multicheckout.api.Checkout3D.request_card_auth')
    @mock.patch('ticketing.multicheckout.api.Checkout3D.secure3d_auth')
    @mock.patch('ticketing.multicheckout.api.get_multicheckout_service')
    @mock.patch('ticketing.multicheckout.api.save_api_response')
    def test_card_info_secure3d_callback_fail(self, save_api_response, get_multicheckout_service, secure3d_auth, request_card_auth):
        from ...multicheckout import models as mc_models
        get_multicheckout_service.return_value = Checkout3D(
            auth_id='auth_id',
            auth_password='password',
            shop_code='000000',
            api_base_url='http://example.com/'
            )
        request_card_auth.return_value = mc_models.MultiCheckoutResponseCard(
            CmnErrorCd='000000')

        self.config.registry.settings['altair_cart.expire_time'] = 15
        # dummy rakuten user
        self.config.add_route('payment.secure3d', 'secure3d')
        userdata = {'clamed_id': 'http://example.com/this-is-openid'}
        import pickle
        userdata = pickle.dumps(userdata).encode('base64')
        self.config.testing_securitypolicy(userid=userdata)
        self.config.registry.settings['cart.item_name'] = '楽天チケット' # configはバイト読み取り
        params = {
            'PaRes': 'this-is-pa-res',
            'MD': 'this-is-md',
        }
        cart_id = 500
        dummy_cart = testing.DummyModel(
            id=cart_id,
            total_amount=1234,
            performance=testing.DummyModel(id=100, name=u'テスト公演'),
            products=[],
            is_expired=lambda self, *args: False,
            finished_at=None,
            order_no='000000000000'
        )
        dummy_cart.finish = lambda: None

        session_order = {
            'client_name': u'楽天太郎',
            'email_1': u'ticketstar@example.com',
            'card_number': u'XXXXXXXXXXXXXXXX',
            'exp_year': '12',
            'exp_month': '06',
            'card_holder_name': u'RAKUTEN TAROU',
        }
        request = DummyRequest(
            params=params,
            _cart=dummy_cart,
            session=DummySession(
                order=session_order,
                payment_confirm_url='http://example.com/payment_confirm'
                ))

        for error_code, return_code in [('000000', '4'), ('000001', '0')]:
            secure3d_auth.return_value = mc_models.Secure3DAuthResponse(
                ErrorCd=error_code,
                RetCd=return_code
                )
            target = self._makeOne(request)

            from multicheckout import MultiCheckoutSettlementFailure
            with self.assertRaises(MultiCheckoutSettlementFailure) as m:
                target.card_info_secure3d_callback()

            self.assertEqual(m.exception.error_code, error_code)
            self.assertEqual(m.exception.return_code, return_code)


class MultiCheckoutPluginTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.config.add_route('payment.secure3d', '/payment.secure3d')
        self._register_dummy_card_brand_detector()

    def tearDown(self):
        import transaction
        transaction.abort()
        testing.tearDown()

    def _getTarget(self):
        from . import multicheckout
        return multicheckout.MultiCheckoutPlugin

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def _register_dummy_card_brand_detector(self):
        from ticketing.multicheckout.interfaces import ICardBrandDetecter
        self.config.registry.utilities.register([], ICardBrandDetecter, "", lambda card_number: "TEST")

    @mock.patch('ticketing.core.models.Order.create_from_cart')
    @mock.patch('ticketing.multicheckout.api.Checkout3D.request_card_sales')
    @mock.patch('ticketing.multicheckout.api.get_multicheckout_service')
    @mock.patch('ticketing.multicheckout.api.save_api_response')
    def test_finish_secure_3d(self, save_api_response, get_multicheckout_service, request_card_sales, create_from_cart):
        from ...multicheckout import models as mc_models
        get_multicheckout_service.return_value = Checkout3D(
            auth_id='auth_id',
            auth_password='password',
            shop_code='000000',
            api_base_url='http://example.com/'
            )
        request_card_sales.return_value = mc_models.MultiCheckoutResponseCard(
            CmnErrorCd='000000'
            )
        create_from_cart.return_value = testing.DummyModel()

        self.config.registry.settings['cart.item_name'] = '楽天チケット' # configはバイト読み取り
        self.config.registry.settings['altair_cart.expire_time'] = 15
        cart_id = 500
        dummy_cart = testing.DummyModel(
            id=cart_id,
            total_amount=1234,
            performance=testing.DummyModel(id=100, name=u'テスト公演'),
            products=[],
            is_expired=lambda self, *args: False,
            finished_at=None,
            order_no='000000000000',
            shipping_address=testing.DummyModel()
        )
        dummy_cart.finish = lambda: None

        session_order = {
            'client_name': u'楽天太郎',
            'email_1': u'ticketstar@example.com',
            'card_number': u'XXXXXXXXXXXXXXXX',
            'exp_year': '12',
            'exp_month': '06',
            'card_holder_name': u'RAKUTEN TAROU',
            'order_no': '000000000000',
            'pares': '*pares*',
            'md': '*md*',
            'tran': {
                'mvn': '*tran*',
                'xid': '*xid*',
                'ts': '*ts*',
                'eci': '*eci*',
                'cavv': '*cavv*',
                'cavv_algorithm': '*cavv_algorithm*',
                },
            }
        params = {
            'PaRes': 'this-is-pa-res',
            'MD': 'this-is-md',
        }
        request = DummyRequest(
            params=params,
            _cart=dummy_cart,
            session=DummySession(
                order=session_order,
                payment_confirm_url='http://example.com/payment_confirm'
                ))

        target = self._makeOne()

        result = target.finish_secure_3d(request, dummy_cart)

    @mock.patch('transaction._transaction.Transaction.commit')
    @mock.patch('ticketing.core.models.Order.create_from_cart')
    @mock.patch('ticketing.multicheckout.api.Checkout3D.request_card_cancel_auth')
    @mock.patch('ticketing.multicheckout.api.Checkout3D.request_card_sales')
    @mock.patch('ticketing.multicheckout.api.get_multicheckout_service')
    @mock.patch('ticketing.multicheckout.api.save_api_response')
    def test_finish_secure_3d_fail(self, save_api_response, get_multicheckout_service, request_card_sales, request_card_cancel_auth, create_from_cart, commit):
        from ...multicheckout import models as mc_models
        get_multicheckout_service.return_value = Checkout3D(
            auth_id='auth_id',
            auth_password='password',
            shop_code='000000',
            api_base_url='http://example.com/'
            )
        request_card_sales.return_value = mc_models.MultiCheckoutResponseCard(
            CmnErrorCd='000001'
            )
        request_card_cancel_auth.return_value = mc_models.MultiCheckoutResponseCard(
            CmnErrorCd='000000'
            )
        create_from_cart.return_value = testing.DummyModel()

        self.config.registry.settings['cart.item_name'] = u'楽天チケット'
        self.config.registry.settings['altair_cart.expire_time'] = 15
        cart_id = 500
        dummy_cart = testing.DummyModel(
            id=cart_id,
            total_amount=1234,
            performance=testing.DummyModel(id=100, name=u'テスト公演'),
            products=[],
            is_expired=lambda self, *args: False,
            finished_at=None,
            order_no='000000000000',
            shipping_address=testing.DummyModel()
        )
        dummy_cart.finish = lambda: None

        session_order = {
            'client_name': u'楽天太郎',
            'email_1': u'ticketstar@example.com',
            'card_number': u'XXXXXXXXXXXXXXXX',
            'exp_year': '12',
            'exp_month': '06',
            'card_holder_name': u'RAKUTEN TAROU',
            'order_no': '000000000000',
            'pares': '*pares*',
            'md': '*md*',
            'tran': {
                'mvn': '*tran*',
                'xid': '*xid*',
                'ts': '*ts*',
                'eci': '*eci*',
                'cavv': '*cavv*',
                'cavv_algorithm': '*cavv_algorithm*',
                },
            }
        params = {
            'PaRes': 'this-is-pa-res',
            'MD': 'this-is-md',
        }
        request = DummyRequest(
            params=params,
            _cart=dummy_cart,
            session=DummySession(
                order=session_order,
                payment_confirm_url='http://example.com/payment_confirm'
                ))

        target = self._makeOne()

        from multicheckout import MultiCheckoutSettlementFailure
        with self.assertRaises(MultiCheckoutSettlementFailure) as m:
            target.finish_secure_3d(request, dummy_cart)
        self.assertEqual(m.exception.error_code, '000001')

    @mock.patch('ticketing.core.models.Order.create_from_cart')
    @mock.patch('ticketing.multicheckout.api.Checkout3D.request_card_sales')
    @mock.patch('ticketing.multicheckout.api.get_multicheckout_service')
    @mock.patch('ticketing.multicheckout.api.save_api_response')
    def test_finish_secure_code(self, save_api_response, get_multicheckout_service, request_card_sales, create_from_cart):
        from ...multicheckout import models as mc_models
        get_multicheckout_service.return_value = Checkout3D(
            auth_id='auth_id',
            auth_password='password',
            shop_code='000000',
            api_base_url='http://example.com/'
            )
        request_card_sales.return_value = mc_models.MultiCheckoutResponseCard(
            CmnErrorCd='000000'
            )
        create_from_cart.return_value = testing.DummyModel()

        self.config.registry.settings['cart.item_name'] = u'楽天チケット'
        self.config.registry.settings['altair_cart.expire_time'] = 15
        cart_id = 500
        dummy_cart = testing.DummyModel(
            id=cart_id,
            total_amount=1234,
            performance=testing.DummyModel(id=100, name=u'テスト公演'),
            products=[],
            is_expired=lambda self, *args: False,
            finished_at=None,
            order_no='000000000000',
            shipping_address=testing.DummyModel()
        )
        dummy_cart.finish = lambda: None

        session_order = {
            'client_name': u'楽天太郎',
            'email_1': u'ticketstar@example.com',
            'card_number': u'XXXXXXXXXXXXXXXX',
            'exp_year': '12',
            'exp_month': '06',
            'card_holder_name': u'RAKUTEN TAROU',
            'order_no': '000000000000',
            'secure_code': '000',
            'pares': '*pares*',
            'md': '*md*',
            'tran': {
                'mvn': '*tran*',
                'xid': '*xid*',
                'ts': '*ts*',
                'eci': '*eci*',
                'cavv': '*cavv*',
                'cavv_algorithm': '*cavv_algorithm*',
                },
            }
        params = {
            'PaRes': 'this-is-pa-res',
            'MD': 'this-is-md',
        }
        request = DummyRequest(
            params=params,
            _cart=dummy_cart,
            session=DummySession(
                order=session_order,
                payment_confirm_url='http://example.com/payment_confirm'
                ))

        target = self._makeOne()

        target.finish_secure_code(request, dummy_cart)

    @mock.patch('transaction._transaction.Transaction.commit')
    @mock.patch('ticketing.core.models.Order.create_from_cart')
    @mock.patch('ticketing.multicheckout.api.Checkout3D.request_card_cancel_auth')
    @mock.patch('ticketing.multicheckout.api.Checkout3D.request_card_sales')
    @mock.patch('ticketing.multicheckout.api.get_multicheckout_service')
    @mock.patch('ticketing.multicheckout.api.save_api_response')
    def test_finish_secure_code(self, save_api_response, get_multicheckout_service, request_card_sales, request_card_cancel_auth, create_from_cart, commit):
        from ...multicheckout import models as mc_models
        get_multicheckout_service.return_value = Checkout3D(
            auth_id='auth_id',
            auth_password='password',
            shop_code='000000',
            api_base_url='http://example.com/'
            )
        request_card_sales.return_value = mc_models.MultiCheckoutResponseCard(
            CmnErrorCd='000002'
            )
        create_from_cart.return_value = testing.DummyModel()

        self.config.registry.settings['cart.item_name'] = u'楽天チケット'
        self.config.registry.settings['altair_cart.expire_time'] = 15
        cart_id = 500
        dummy_cart = testing.DummyModel(
            id=cart_id,
            total_amount=1234,
            performance=testing.DummyModel(id=100, name=u'テスト公演'),
            products=[],
            is_expired=lambda self, *args: False,
            finished_at=None,
            order_no='000000000000',
            shipping_address=testing.DummyModel()
        )
        dummy_cart.finish = lambda: None

        session_order = {
            'client_name': u'楽天太郎',
            'email_1': u'ticketstar@example.com',
            'card_number': u'XXXXXXXXXXXXXXXX',
            'exp_year': '12',
            'exp_month': '06',
            'card_holder_name': u'RAKUTEN TAROU',
            'order_no': '000000000000',
            'secure_code': '000',
            'pares': '*pares*',
            'md': '*md*',
            'tran': {
                'mvn': '*tran*',
                'xid': '*xid*',
                'ts': '*ts*',
                'eci': '*eci*',
                'cavv': '*cavv*',
                'cavv_algorithm': '*cavv_algorithm*',
                },
            }
        params = {
            'PaRes': 'this-is-pa-res',
            'MD': 'this-is-md',
        }
        request = DummyRequest(
            params=params,
            _cart=dummy_cart,
            session=DummySession(
                order=session_order,
                payment_confirm_url='http://example.com/payment_confirm'
                ))

        target = self._makeOne()

        from multicheckout import MultiCheckoutSettlementFailure
        with self.assertRaises(MultiCheckoutSettlementFailure) as m:
            target.finish_secure_code(request, dummy_cart)

        self.assertEqual(m.exception.error_code, '000002')
