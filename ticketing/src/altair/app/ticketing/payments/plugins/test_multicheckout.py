# -*- coding:utf-8 -*-

import unittest
from pyramid import testing
from pyramid.testing import DummySession
from altair.app.ticketing.testing import _setup_db, _teardown_db
from altair.app.ticketing.testing import DummyRequest
from altair.multicheckout.impl import Checkout3D
import mock

def _setup_test_db():
    session = _setup_db(['altair.app.ticketing.core.models'])
    from altair.app.ticketing.core.models import Host, Organization, OrganizationSetting
    org = Organization(short_name='TEST')
    host = Host(host_name='example.com:80')
    settings = OrganizationSetting(cart_item_name=u'テストテスト')
    host.organization = org
    settings.organization = org
    session.add(org)
    return session


class MultiCheckoutViewTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self._register_dummy_card_brand_detector()
        self._register_cart_getter()
        self.session = _setup_test_db()

    def tearDown(self):
        testing.tearDown()
        _teardown_db()

    def _getTarget(self):
        from . import multicheckout
        return multicheckout.MultiCheckoutView

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def _register_dummy_card_brand_detector(self):
        from altair.multicheckout.interfaces import ICardBrandDetecter
        self.config.registry.utilities.register([], ICardBrandDetecter, "", lambda card_number: "TEST")

    def _register_cart_getter(self):
        from altair.app.ticketing.payments.interfaces import IGetCart
        self.config.registry.utilities.register([], IGetCart, "", 
                                                lambda request: request._cart)

    @mock.patch('wtforms.ext.csrf.SecureForm.validate')
    @mock.patch('altair.multicheckout.impl.Checkout3D.secure3d_enrol')
    @mock.patch('altair.multicheckout.api.get_multicheckout_impl')
    @mock.patch('altair.multicheckout.api.Multicheckout3DAPI.save_api_response')
    def test_card_info_secure3d_enable_api(self, save_api_response, get_multicheckout_impl, secure3d_enrol, validate):
        from altair.multicheckout import models as mc_models
        get_multicheckout_impl.return_value = Checkout3D(
            auth_id='auth_id',
            auth_password='password',
            shop_code='000000',
            api_base_url='http://example.com/',
            api_timeout=90,
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
            name=u"99999999",
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
    @mock.patch('altair.multicheckout.impl.Checkout3D.request_card_auth')
    @mock.patch('altair.multicheckout.impl.Checkout3D.secure3d_enrol')
    @mock.patch('altair.multicheckout.api.get_multicheckout_impl')
    @mock.patch('altair.multicheckout.api.Multicheckout3DAPI.save_api_response')
    def test_card_info_secure3d_disabled_api(self, save_api_response, get_multicheckout_impl, secure3d_enrol, request_card_auth, validate):
        from altair.multicheckout import models as mc_models
        get_multicheckout_impl.return_value = Checkout3D(
            auth_id='auth_id',
            auth_password='password',
            shop_code='000000',
            api_base_url='http://example.com/',
            api_timeout=90,
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
        #self.config.registry.settings['cart.item_name'] = '楽天チケット' # configはバイト読み取り
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
            name=u"99999999",
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
    @mock.patch('altair.multicheckout.impl.Checkout3D.request_card_auth')
    @mock.patch('altair.multicheckout.impl.Checkout3D.secure3d_enrol')
    @mock.patch('altair.multicheckout.api.get_multicheckout_impl')
    @mock.patch('altair.multicheckout.api.Multicheckout3DAPI.save_api_response')
    def test_card_info_secure3d_disabled_api_fail(self, save_api_response, get_multicheckout_impl, secure3d_enrol, request_card_auth, validate):
        from altair.multicheckout import models as mc_models
        get_multicheckout_impl.return_value = Checkout3D(
            auth_id='auth_id',
            auth_password='password',
            shop_code='000000',
            api_base_url='http://example.com/',
            api_timeout=90,
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
        # self.config.registry.settings['cart.item_name'] = '楽天チケット' # configはバイト読み取り
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
            name=u"99999999",
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


    @mock.patch('altair.multicheckout.impl.Checkout3D.request_card_auth')
    @mock.patch('altair.multicheckout.impl.Checkout3D.secure3d_auth')
    @mock.patch('altair.multicheckout.api.get_multicheckout_impl')
    @mock.patch('altair.multicheckout.api.Multicheckout3DAPI.save_api_response')
    def test_card_info_secure3d_callback(self, save_api_response, get_multicheckout_impl, secure3d_auth, request_card_auth):
        from altair.multicheckout import models as mc_models
        get_multicheckout_impl.return_value = Checkout3D(
            auth_id='auth_id',
            auth_password='password',
            shop_code='000000',
            api_base_url='http://example.com/',
            api_timeout=90,
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
        userdata = {'claimed_id': 'http://example.com/this-is-openid'}
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
            name=u"99999999",
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

    @mock.patch('altair.multicheckout.impl.Checkout3D.request_card_auth')
    @mock.patch('altair.multicheckout.impl.Checkout3D.secure3d_auth')
    @mock.patch('altair.multicheckout.api.get_multicheckout_impl')
    @mock.patch('altair.multicheckout.api.Multicheckout3DAPI.save_api_response')
    def test_card_info_secure3d_callback_fail(self, save_api_response, get_multicheckout_impl, secure3d_auth, request_card_auth):
        from altair.multicheckout import models as mc_models
        get_multicheckout_impl.return_value = Checkout3D(
            auth_id='auth_id',
            auth_password='password',
            shop_code='000000',
            api_base_url='http://example.com/',
            api_timeout=90,
            )
        request_card_auth.return_value = mc_models.MultiCheckoutResponseCard(
            CmnErrorCd='000000')

        self.config.registry.settings['altair_cart.expire_time'] = 15
        # dummy rakuten user
        self.config.add_route('payment.secure3d', 'secure3d')
        userdata = {'claimed_id': 'http://example.com/this-is-openid'}
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
            name=u"99999999",
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
        self.session = _setup_test_db()


    def tearDown(self):
        testing.tearDown()
        _teardown_db()
        import transaction
        transaction.abort()


    def _getTarget(self):
        from . import multicheckout
        return multicheckout.MultiCheckoutPlugin

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def _register_dummy_card_brand_detector(self):
        from altair.multicheckout.interfaces import ICardBrandDetecter
        self.config.registry.utilities.register([], ICardBrandDetecter, "", lambda card_number: "TEST")

    @mock.patch('transaction._transaction.Transaction.commit')
    @mock.patch('altair.app.ticketing.core.models.Order.create_from_cart')
    @mock.patch('altair.multicheckout.impl.Checkout3D.request_card_cancel_auth')
    @mock.patch('altair.multicheckout.impl.Checkout3D.request_card_sales')
    @mock.patch('altair.multicheckout.api.get_multicheckout_impl')
    @mock.patch('altair.multicheckout.api.Multicheckout3DAPI.save_api_response')
    def test_finish(self, save_api_response, get_multicheckout_impl, request_card_sales, request_card_cancel_auth, create_from_cart, commit):
        from altair.multicheckout import models as mc_models
        get_multicheckout_impl.return_value = Checkout3D(
            auth_id='auth_id',
            auth_password='password',
            shop_code='000000',
            api_base_url='http://example.com/',
            api_timeout=90,
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
            name=u"9999999999",
            total_amount=1234,
            performance=testing.DummyModel(id=100, name=u'テスト公演'),
            products=[],
            is_expired=lambda self, *args: False,
            finished_at=None,
            order_no='000000000000',
            shipping_address=testing.DummyModel(),
            has_different_amount=False,
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
            target.finish(request, dummy_cart)
        self.assertEqual(m.exception.error_code, '000001')
