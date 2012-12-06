# -*- coding:utf8 -*-

import unittest
from pyramid import testing
from ..testing import DummyRequest, DummySecure3D
import mock

class MultiCheckoutViewTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        #self.session = _setup_db()

    def tearDown(self):
        testing.tearDown()
        #_teardown_db()

    def _getTarget(self):
        from . import multicheckout
        return multicheckout.MultiCheckoutView

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def _register_dummy_secure3d(self, *args, **kwargs):
        from ticketing.multicheckout import interfaces
        dummy = DummySecure3D(*args, **kwargs)
        self.config.registry.utilities.register([], interfaces.IMultiCheckout, "", dummy)
        return dummy

    def test_card_info_secure3d_enable_api(self):
        self.config.add_route('cart.secure3d_result', '/this-is-secure3d-callback')
        dummy_secure3d = self._register_dummy_secure3d(AcsUrl='http://example.com/AcsUrl', PaReq='this-is-pareq', Md='this-is-Md')
        params = {
            'card_number': 'XXXXXXXXXXXXXXXX',
            'exp_year': '13',
            'exp_month': '07',
            'client_name': u'楽天太郎',
            'card_holder_name': u'RAKUTEN TAROU',
            'mail_address': u'ticketstar@example.com',
            }

        cart_id = 500
        dummy_cart = testing.DummyModel(id=cart_id, total_amount=1234)

        request = DummyRequest(params=params, _cart=dummy_cart)
        request.session['order'] = {}
        target = self._makeOne(request)

        result = target.card_info_secure3d()

        self.assertEqual(result.text, "<form name='PAReqForm' method='POST' action='http://example.com/AcsUrl'>\n        <input type='hidden' name='PaReq' value='this-is-pareq'>\n        <input type='hidden' name='TermUrl' value='http://example.com/this-is-secure3d-callback'>\n        <input type='hidden' name='MD' value='this-is-Md'>\n        </form>\n        <script type='text/javascript'>function onLoadHandler(){document.PAReqForm.submit();};window.onload = onLoadHandler; </script>\n        ")
        #self.assertIsNotNone(result.get('form'))
        #form = result['form']
        #self.assertIn('http://example.com/AcsUrl', form)
        #self.assertIn('this-is-pareq', form)
        #self.assertIn('this-is-Md', form)
        #self.assertIn('/this-is-secure3d-callback', form)

        #self.assertEqual(dummy_secure3d.called[0][0], 'secure3d_enrol')
        #self.assertEqual(dummy_secure3d.called[0][1][0], 500)
        #self.assertEqual(dummy_secure3d.called[0][1][1].CardNumber, "XXXXXXXXXXXXXXXX")
        #self.assertEqual(dummy_secure3d.called[0][1][1].ExpYear, "13")
        #self.assertEqual(dummy_secure3d.called[0][1][1].ExpMonth, "07")

        #self.assertEqual(dummy_secure3d.called[1],('is_enable_auth_api', (), {}))

        session_order = request.session['order']
        self.assertEqual(session_order['card_number'], 'XXXXXXXXXXXXXXXX')
        #self.assertEqual(session_order['client_name'], u'楽天太郎')
        #self.assertEqual(session_order['mail_address'], u'ticketstar@example.com')
        self.assertEqual(session_order['exp_year'], '13')
        self.assertEqual(session_order['exp_month'], '07')
        self.assertEqual(session_order['card_holder_name'], u'RAKUTEN TAROU')

    def test_card_info_secure3d_disabled_api(self):
        self.config.add_route('cart.secure3d_result', '/this-is-secure3d-callback')
        dummy_secure3d = self._register_dummy_secure3d(AcsUrl='http://example.com/AcsUrl', PaReq='this-is-pareq', Md='this-is-Md', enable_auth_api=False)
        params = {
            'card_number': 'XXXXXXXXXXXXXXXX',
            'exp_year': '13',
            'exp_month': '07',
            'client_name': u'楽天太郎',
            'card_holder_name': u'RAKUTEN TAROU',
            'mail_address': u'ticketstar@example.com',
        }

        cart_id = 500
        dummy_cart = testing.DummyModel(id=cart_id, total_amount=1234)

        request = DummyRequest(params=params, _cart=dummy_cart)
        request.session['order'] = {}
        target = self._makeOne(request)

        result = target.card_info_secure3d()

#        self.assertIsNotNone(result.get('form'))
#        form = result['form']
#        self.assertIn('http://example.com/AcsUrl', form)
#        self.assertIn('this-is-pareq', form)
#        self.assertIn('this-is-Md', form)
#        self.assertIn('/this-is-secure3d-callback', form)

        self.assertEqual(dummy_secure3d.called[0][0], 'secure3d_enrol')
        self.assertEqual(dummy_secure3d.called[0][1][0], 500)
        self.assertEqual(dummy_secure3d.called[0][1][1].CardNumber, "XXXXXXXXXXXXXXXX")
        self.assertEqual(dummy_secure3d.called[0][1][1].ExpYear, "13")
        self.assertEqual(dummy_secure3d.called[0][1][1].ExpMonth, "07")

        self.assertEqual(dummy_secure3d.called[1],('is_enable_auth_api', (), {}))

        self.assertEqual(dummy_secure3d.called[2],('is_enable_secure3d', (), {}))

    def test_card_info_secure3d_callback(self):
        # dummy rakuten user
        self.config.add_route('payment.secure3d', 'secure3d')
        userdata = {'clamed_id': 'http://example.com/this-is-openid'}
        import pickle
        userdata = pickle.dumps(userdata).encode('base64')
        self.config.testing_securitypolicy(userid=userdata)
        dummy_secure3d = self._register_dummy_secure3d(AcsUrl='http://example.com/AcsUrl', PaReq='this-is-pareq', Md='this-is-Md', enable_auth_api=False)
        self.config.registry.settings['cart.item_name'] = '楽天チケット' # configはバイト読み取り
        params = {
            'PaRes': 'this-is-pa-res',
            'MD': 'this-is-md',
        }
        cart_id = 500
        dummy_cart = testing.DummyModel(id=cart_id, total_amount=1234,
            performance=testing.DummyModel(id=100, name=u'テスト公演'),
            products=[],
        )
        dummy_cart.finish = lambda: None

        session_order = {
            'client_name': u'楽天太郎',
            'mail_address': u'ticketstar@example.com',
            'card_number': u'XXXXXXXXXXXXXXXX',
            'exp_year': '12',
            'exp_month': '06',
            'card_holder_name': u'RAKUTEN TAROU',
        }
        request = DummyRequest(params=params, _cart=dummy_cart, session=dict(order=session_order))
        target = self._makeOne(request)

        result = target.card_info_secure3d_callback()


