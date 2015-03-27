# -*- coding:utf-8 -*-

import unittest
from pyramid import testing
from pyramid.testing import DummySession
from altair.app.ticketing.testing import _setup_db, _teardown_db
from altair.app.ticketing.testing import DummyRequest
from altair.multicheckout.impl import Checkout3D
import mock

def _setup_test_db(config):
    session = _setup_db([
        'altair.app.ticketing.core.models',
        'altair.app.ticketing.cart.models',
        'altair.app.ticketing.orders.models',
        ])
    from altair.sqlahelper import register_sessionmaker_with_engine
    register_sessionmaker_with_engine(
        config.registry,
        'slave',
        session.bind
        )
    from altair.app.ticketing.core.models import Host, Organization, OrganizationSetting
    organization = Organization(id=1, short_name='TEST')
    host = Host(
        organization=organization,
        host_name='example.com:80'
        )
    settings = OrganizationSetting(
        organization=organization,
        cart_item_name=u'テストテスト'
        )
    session.add(organization)
    session.flush()
    return session, organization


class MultiCheckoutViewTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.config.include('altair.app.ticketing.cart.request')
        self._register_dummy_card_brand_detector()
        self._register_cart_interface()
        self.session, self.organization = _setup_test_db(self.config)
        from altair.sqlahelper import register_sessionmaker_with_engine
        register_sessionmaker_with_engine(
            self.config.registry,
            'slave',
            self.session.bind
            )

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

    def _register_cart_interface(self):
        from altair.app.ticketing.payments.interfaces import ICartInterface
        class DummyCartInterface(object):
            def __init__(self, outer):
                self.outer = outer

            def get_cart(self, request, retrieve_invalidated=False):
                return request._cart

            def get_success_url(self, request):
                return 'http://example.com/payment_confirm'

        self.config.registry.utilities.register([], ICartInterface, "", DummyCartInterface(self))

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
        self.config.add_route('payment.secure3d_result', '/this-is-secure3d-callback')
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
            payment_delivery_pair=testing.DummyModel(id=1),
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
        from .. import api as p_api
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
        self.config.add_route('payment.secure3d_result', '/this-is-secure3d-callback')
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
            performance=testing.DummyModel(id=1),
            payment_delivery_pair=testing.DummyModel(id=1),
            )

        request = DummyRequest(
            params=params,
            _cart=dummy_cart,
            session=DummySession(order=params)
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
        from .. import api as p_api
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
        self.config.add_route('payment.secure3d_result', '/this-is-secure3d-callback')
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
            performance=testing.DummyModel(id=1),
            payment_delivery_pair=testing.DummyModel(id=1),
            )

        request = DummyRequest(
            params=params,
            _cart=dummy_cart,
            session=DummySession(order=params)
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
        from .. import api as p_api
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
            order_no='000000000000',
            payment_delivery_pair=testing.DummyModel(id=1),
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
            session=DummySession(order=session_order)
            )
        target = self._makeOne(request)

        result = target.card_info_secure3d_callback()

        self.assertEqual(result.location, 'http://example.com/payment_confirm')

    @mock.patch('altair.multicheckout.impl.Checkout3D.request_card_auth')
    @mock.patch('altair.multicheckout.impl.Checkout3D.secure3d_auth')
    @mock.patch('altair.multicheckout.api.get_multicheckout_impl')
    @mock.patch('altair.multicheckout.api.Multicheckout3DAPI.save_api_response')
    def test_card_info_secure3d_callback_fail(self, save_api_response, get_multicheckout_impl, secure3d_auth, request_card_auth):
        from .. import api as p_api
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
            order_no='000000000000',
            payment_delivery_pair=testing.DummyModel(id=1),
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
            session=DummySession(order=session_order)
            )

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
        self.session, self.organization = _setup_test_db(self.config)
        from altair.sqlahelper import register_sessionmaker_with_engine
        register_sessionmaker_with_engine(
            self.config.registry,
            'slave',
            self.session.bind
            )
        self.config.add_route('payment.secure3d', '/payment.secure3d')
        self._register_dummy_card_brand_detector()
        from altair.multicheckout import models as mc_models
        mc_models._session.remove()
        mc_models.Base.metadata.create_all()

    def tearDown(self):
        testing.tearDown()
        _teardown_db()
        from altair.multicheckout import models as mc_models
        mc_models._session.remove()
        mc_models.Base.metadata.drop_all()
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
    @mock.patch('altair.app.ticketing.orders.models.Order.create_from_cart')
    @mock.patch('altair.multicheckout.impl.Checkout3D.request_card_cancel_auth')
    @mock.patch('altair.multicheckout.impl.Checkout3D.request_card_sales')
    @mock.patch('altair.multicheckout.api.get_multicheckout_impl')
    @mock.patch('altair.multicheckout.api.Multicheckout3DAPI.save_api_response')
    @mock.patch('altair.multicheckout.api.Multicheckout3DAPI.get_authorized_amount')
    def test_finish_success(self, get_authorized_amount, save_api_response, get_multicheckout_impl, request_card_sales, request_card_cancel_auth, create_from_cart, commit):
        from .. import api as p_api
        from altair.multicheckout import models as mc_models
        from altair.app.ticketing.cart import models as cart_models
        from altair.app.ticketing.core import models as core_models
        get_authorized_amount.return_value = 1234
        get_multicheckout_impl.return_value = Checkout3D(
            auth_id='auth_id',
            auth_password='password',
            shop_code='000000',
            api_base_url='http://example.com/',
            api_timeout=90,
            )
        request_card_sales.return_value = mc_models.MultiCheckoutResponseCard(
            CmnErrorCd='000000'
            )
        request_card_cancel_auth.return_value = mc_models.MultiCheckoutResponseCard(
            CmnErrorCd='000000'
            )
        create_from_cart.return_value = testing.DummyModel()

        self.config.registry.settings['cart.item_name'] = u'楽天チケット'
        self.config.registry.settings['altair_cart.expire_time'] = 15
        cart_id = 500
        dummy_cart = cart_models.Cart(
            id=cart_id,
            organization_id=1,
            performance=core_models.Performance(id=100, name=u'テスト公演'),
            products=[],
            is_expired=lambda self, *args: False,
            finished_at=None,
            _order_no='000000000000',
            shipping_address=core_models.ShippingAddress(),
            sales_segment=core_models.SalesSegment(),
            payment_delivery_pair=core_models.PaymentDeliveryMethodPair(
                transaction_fee=0,
                delivery_fee_per_order=0,
                delivery_fee_per_principal_ticket=0,
                delivery_fee_per_subticket=0,
                system_fee=0,
                special_fee=0,
                payment_method=core_models.PaymentMethod(fee_type=core_models.FeeTypeEnum.Once.v)
                ),
            items=[
                cart_models.CartedProduct(
                    product=core_models.Product(price=1234),
                    quantity=1
                    )
                ]
            )

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
            session=DummySession(order=session_order)
            )

        target = self._makeOne()

        try:
            target.finish(request, dummy_cart)
            self.assertTrue(True)
        except Exception as e:
            self.fail(e)
        self.assertFalse(request_card_cancel_auth.called)

    @mock.patch('transaction._transaction.Transaction.commit')
    @mock.patch('altair.app.ticketing.orders.models.Order.create_from_cart')
    @mock.patch('altair.multicheckout.impl.Checkout3D.request_card_cancel_auth')
    @mock.patch('altair.multicheckout.impl.Checkout3D.request_card_sales')
    @mock.patch('altair.multicheckout.api.get_multicheckout_impl')
    @mock.patch('altair.multicheckout.api.Multicheckout3DAPI.save_api_response')
    @mock.patch('altair.multicheckout.api.Multicheckout3DAPI.get_authorized_amount')
    def test_finish_fail(self, get_authorized_amount, save_api_response, get_multicheckout_impl, request_card_sales, request_card_cancel_auth, create_from_cart, commit):
        from .. import api as p_api
        from altair.multicheckout import models as mc_models
        get_authorized_amount.return_value = 1234
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
            organization_id=1,
            total_amount=1234,
            performance=testing.DummyModel(id=100, name=u'テスト公演'),
            products=[],
            is_expired=lambda self, *args: False,
            finished_at=None,
            order_no='000000000000',
            shipping_address=testing.DummyModel(),
            payment_delivery_pair=testing.DummyModel(id=1),
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
            session=DummySession(order=session_order)
            )

        target = self._makeOne()

        from multicheckout import MultiCheckoutSettlementFailure
        with self.assertRaises(MultiCheckoutSettlementFailure) as m:
            target.finish(request, dummy_cart)
        self.assertEqual(m.exception.error_code, '000001')
        self.assertTrue(request_card_cancel_auth.called)

    @mock.patch('transaction._transaction.Transaction.commit')
    @mock.patch('altair.app.ticketing.orders.models.Order.create_from_cart')
    @mock.patch('altair.multicheckout.impl.Checkout3D.request_card_cancel_auth')
    @mock.patch('altair.multicheckout.impl.Checkout3D.request_card_sales')
    @mock.patch('altair.multicheckout.api.get_multicheckout_impl')
    @mock.patch('altair.multicheckout.api.Multicheckout3DAPI.save_api_response')
    @mock.patch('altair.multicheckout.api.Multicheckout3DAPI.get_authorized_amount')
    def test_finish_api_fail(self, get_authorized_amount, save_api_response, get_multicheckout_impl, request_card_sales, request_card_cancel_auth, create_from_cart, commit):
        from .. import api as p_api
        from altair.multicheckout import models as mc_models
        get_authorized_amount.return_value = 1234
        get_multicheckout_impl.return_value = Checkout3D(
            auth_id='auth_id',
            auth_password='password',
            shop_code='000000',
            api_base_url='http://example.com/',
            api_timeout=90,
            )
        def raise_api_exception(*args, **kwargs):
            from altair.multicheckout.exceptions import MultiCheckoutAPIError
            raise MultiCheckoutAPIError('oops')
        request_card_sales.side_effect = raise_api_exception
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
            organization_id=1,
            performance=testing.DummyModel(id=100, name=u'テスト公演'),
            products=[],
            is_expired=lambda self, *args: False,
            finished_at=None,
            order_no='000000000000',
            shipping_address=testing.DummyModel(),
            payment_delivery_pair=testing.DummyModel(id=1),
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
            session=DummySession(order=session_order)
            )

        target = self._makeOne()

        from multicheckout import MultiCheckoutSettlementFailure
        with self.assertRaises(MultiCheckoutSettlementFailure) as m:
            target.finish(request, dummy_cart)
        self.assertEqual(m.exception.error_code, None)
        self.assertTrue(request_card_cancel_auth.called)

    @mock.patch('transaction._transaction.Transaction.commit')
    @mock.patch('altair.app.ticketing.orders.models.Order.create_from_cart')
    @mock.patch('altair.multicheckout.impl.Checkout3D.request_card_cancel_auth')
    @mock.patch('altair.multicheckout.impl.Checkout3D.request_card_sales')
    @mock.patch('altair.multicheckout.api.get_multicheckout_impl')
    @mock.patch('altair.multicheckout.api.Multicheckout3DAPI.save_api_response')
    @mock.patch('altair.multicheckout.api.Multicheckout3DAPI.get_authorized_amount')
    def test_finish_api_fail_keep_auth(self, get_authorized_amount, save_api_response, get_multicheckout_impl, request_card_sales, request_card_cancel_auth, create_from_cart, commit):
        from .. import api as p_api
        from altair.multicheckout import models as mc_models
        get_authorized_amount.return_value = 1234
        get_multicheckout_impl.return_value = Checkout3D(
            auth_id='auth_id',
            auth_password='password',
            shop_code='000000',
            api_base_url='http://example.com/',
            api_timeout=90,
            )
        def raise_api_exception(*args, **kwargs):
            from altair.multicheckout.exceptions import MultiCheckoutAPIError
            raise MultiCheckoutAPIError('oops')
        request_card_sales.side_effect = raise_api_exception
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
            organization_id=1,
            performance=testing.DummyModel(id=100, name=u'テスト公演'),
            products=[],
            is_expired=lambda self, *args: False,
            finished_at=None,
            order_no='000000000000',
            shipping_address=testing.DummyModel(),
            payment_delivery_pair=testing.DummyModel(id=1),
        )
        dummy_cart.finish = lambda: None

        mc_models._session.add(mc_models.MultiCheckoutOrderStatus(
            OrderNo=dummy_cart.order_no,
            Storecd=get_multicheckout_impl.return_value.shop_code,
            Status='110',
            KeepAuthFor='something_good'
            ))
        mc_models._session.flush()

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
            session=DummySession(order=session_order)
            )

        target = self._makeOne()

        from multicheckout import MultiCheckoutSettlementFailure
        with self.assertRaises(MultiCheckoutSettlementFailure) as m:
            target.finish(request, dummy_cart)
        self.assertEqual(m.exception.error_code, None)
        self.assertFalse(request_card_cancel_auth.called)

    @mock.patch('transaction._transaction.Transaction.commit')
    @mock.patch('altair.multicheckout.impl.Checkout3D.request_card_sales_part_cancel')
    @mock.patch('altair.multicheckout.impl.Checkout3D.request_card_inquiry')
    @mock.patch('altair.multicheckout.api.get_multicheckout_impl')
    @mock.patch('altair.multicheckout.api.Multicheckout3DAPI.save_api_response')
    def test_refresh_success(self, save_api_response, get_multicheckout_impl, request_card_inquiry, request_card_sales_part_cancel, commit):
        from .. import api as p_api
        from altair.multicheckout import models as mc_models
        from altair.app.ticketing.core import models as core_models
        from altair.app.ticketing.orders import models as orders_models

        order = orders_models.Order(
            organization_id=1,
            items=[
                orders_models.OrderedProduct(
                    price=10,
                    product=core_models.Product(price=10),
                    quantity=1,
                    elements=[
                        orders_models.OrderedProductItem(
                            price=10,
                            product_item=core_models.ProductItem(price=10),
                            quantity=1,
                            tokens=[
                                orders_models.OrderedProductItemToken(valid=True)
                                ],
                            seats=[]
                            )
                        ]
                    )
                ],
            total_amount=10
            )
        get_multicheckout_impl.return_value = Checkout3D(
            auth_id='auth_id',
            auth_password='password',
            shop_code='000000',
            api_base_url='http://example.com/',
            api_timeout=90,
            )
        request_card_inquiry.return_value = mc_models.MultiCheckoutInquiryResponseCard(
            CmnErrorCd='000000',
            Status=str(mc_models.MultiCheckoutStatusEnum.Settled),
            SalesAmount=15
            )
        request_card_sales_part_cancel.return_value = mc_models.MultiCheckoutResponseCard(
            CmnErrorCd='000000'
            )

        request = DummyRequest()
        target = self._makeOne()

        try:
            target.refresh(request, order)
            self.assertTrue(True)
        except Exception as e:
            raise
            self.fail()
        self.assertTrue(request_card_sales_part_cancel.called)

    @mock.patch('transaction._transaction.Transaction.commit')
    @mock.patch('altair.multicheckout.api.get_multicheckout_impl')
    @mock.patch('altair.multicheckout.api.Multicheckout3DAPI.save_api_response')
    def test_validate_success(self, save_api_response, get_multicheckout_impl, commit):
        from .. import api as p_api
        from altair.multicheckout import models as mc_models
        from altair.app.ticketing.core import models as core_models
        from altair.app.ticketing.orders import models as orders_models
        status = mc_models.MultiCheckoutOrderStatus(
            OrderNo='000000000000',
            Status=str(mc_models.MultiCheckoutStatusEnum.Authorized)
            )
        mc_models._session.add(status)
        mc_models._session.flush()
        cart_id = 500
        dummy_cart = testing.DummyModel(
            id=cart_id,
            name=u"99999999",
            total_amount=1234,
            organization_id=1,
            performance=testing.DummyModel(id=100, name=u'テスト公演'),
            products=[],
            is_expired=lambda self, *args: False,
            finished_at=None,
            order_no='000000000000',
            payment_delivery_pair=testing.DummyModel(id=1),
        )
        dummy_cart.finish = lambda: None

        request = DummyRequest()
        target = self._makeOne()

        try:
            target.validate(request, dummy_cart)
            self.assertTrue(True)
        except Exception as e:
            raise
            self.fail()

    @mock.patch('transaction._transaction.Transaction.commit')
    @mock.patch('altair.multicheckout.api.get_multicheckout_impl')
    @mock.patch('altair.multicheckout.api.Multicheckout3DAPI.save_api_response')
    def test_validate_fail(self, save_api_response, get_multicheckout_impl, commit):
        from .. import api as p_api
        from altair.multicheckout import models as mc_models
        from altair.app.ticketing.core import models as core_models
        from altair.app.ticketing.orders import models as orders_models
        status = mc_models.MultiCheckoutOrderStatus(
            OrderNo='000000000000',
            Status=str(mc_models.MultiCheckoutStatusEnum.NotAuthorized)
            )
        mc_models._session.add(status)
        mc_models._session.flush()
        cart_id = 500
        dummy_cart = testing.DummyModel(
            id=cart_id,
            name=u"99999999",
            total_amount=1234,
            organization_id=1,
            performance=testing.DummyModel(id=100, name=u'テスト公演'),
            products=[],
            is_expired=lambda self, *args: False,
            finished_at=None,
            order_no='000000000000',
            payment_delivery_pair=testing.DummyModel(id=1),
        )
        dummy_cart.finish = lambda: None

        request = DummyRequest()
        target = self._makeOne()

        from multicheckout import MultiCheckoutSettlementFailure
        with self.assertRaises(MultiCheckoutSettlementFailure):
            target.validate(request, dummy_cart)


