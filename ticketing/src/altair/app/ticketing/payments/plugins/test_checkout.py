import unittest
import mock
from pyramid import testing
from webtest import TestApp
from altair.app.ticketing.testing import _setup_db, _teardown_db
from altair.app.ticketing.core.testing import CoreTestMixin

class TestCheckoutViews(unittest.TestCase, CoreTestMixin):
    SET_CART_URL = '/set_cart'
    LOGIN_URL = '/checkout/login'
    COMPLETE_URL = '/checkout/order_complete'

    def _dummy_root_factory(self, request):
        return testing.DummyResource()

    def _dummy_session_factory(self, request):
        return self.session_data

    def setUp(self):
        from decimal import Decimal
        from pyramid.config import Configurator
        from webtest import TestApp
        from altair.app.ticketing.core.models import SalesSegmentGroup, SalesSegment, PaymentDeliveryMethodPair
        from altair.app.ticketing.cart.models import Cart
        from altair.app.ticketing.checkout.models import RakutenCheckoutSetting
        from . import CHECKOUT_PAYMENT_PLUGIN_ID, SHIPPING_DELIVERY_PLUGIN_ID
        from datetime import datetime
        self.session = _setup_db([
            'altair.app.ticketing.core.models',
            'altair.app.ticketing.orders.models',
            'altair.app.ticketing.lots.models',
            'altair.app.ticketing.cart.models',
            'altair.app.ticketing.checkout.models',
            ])
        CoreTestMixin.setUp(self)
        self.session.add(RakutenCheckoutSetting(
            organization=self.organization,
            channel=1,
            auth_method='HMAC-SHA1'
            ))
        self.sales_segment_group = SalesSegmentGroup(event=self.event)
        self.payment_delivery_method_pair = PaymentDeliveryMethodPair(
            sales_segment_group=self.sales_segment_group,
            system_fee=Decimal(0.),
            system_fee_type=0,
            transaction_fee=Decimal(0.),
            delivery_fee_per_order=Decimal(0.),
            delivery_fee_per_principal_ticket=Decimal(0.),
            delivery_fee_per_subticket=Decimal(0.),
            special_fee=Decimal(0.),
            special_fee_type=0,
            discount=Decimal(0.),
            discount_unit=0,
            public=True,
            payment_method=self.payment_methods[CHECKOUT_PAYMENT_PLUGIN_ID],
            delivery_method=self.delivery_methods[SHIPPING_DELIVERY_PLUGIN_ID],
            issuing_interval_days=5
            )
        self.sales_segment = SalesSegment(
            sales_segment_group=self.sales_segment_group,
            performance=self.performance,
            payment_delivery_method_pairs=[self.payment_delivery_method_pair],
            start_at=datetime(1, 1, 1),
            end_at=None
            )
        self.session.add(self.sales_segment_group)
        self.session.add(self.payment_delivery_method_pair)
        self.session.add(self.sales_segment)
        self.session.flush()
        self.session_data = {}
        config = Configurator(settings={
            'altair.sej.template_file': '',
            'altair_cart.expire_time': '1000000', # XXX: number large enough
            'altair_checkout.checkin_url': repr(self),
            },
            root_factory=self._dummy_root_factory,
            session_factory=self._dummy_session_factory)
        config.add_renderer('.html' , 'pyramid.mako_templating.renderer_factory')
        config.include('altair.mobile')
        config.include('altair.browserid')
        config.include('altair.app.ticketing.payments')
        config.include('altair.app.ticketing.payments.plugins')
        config.add_view(self._set_cart, route_name='set_cart')
        config.add_route('set_cart', self.SET_CART_URL)
        config.add_route('payment.checkout.login', self.LOGIN_URL)
        config.add_route('payment.checkout.order_complete', self.COMPLETE_URL)
        self.cart = Cart(
            id=10,
            performance=self.sales_segment.performance,
            sales_segment=self.sales_segment,
            payment_delivery_pair=self.payment_delivery_method_pair,
            _order_no='XX0000000000'
            )
        self.session.add(self.cart)
        self.session.flush()
        self.test_app = TestApp(config.make_wsgi_app())
        self.test_app.get(self.SET_CART_URL)

    def tearDown(self):
        _teardown_db()

    def _set_cart(self, context, request):
        from altair.app.ticketing.cart.api import set_cart
        from pyramid.httpexceptions import HTTPOk
        set_cart(request, self.cart)
        self.callback_success_url = request.route_url('payment.checkout.callback.success')
        self.callback_error_url = request.route_url('payment.checkout.callback.error')
        return HTTPOk()

    @mock.patch('altair.app.ticketing.checkout.api.AnshinCheckoutAPI')
    def test_login(self, checkout_class):
        form_html = '<form></form>'
        checkout_class.return_value.build_checkout_request_form.return_value = (testing.DummyModel(), form_html)
        resp = self.test_app.post(self.LOGIN_URL, {})
        checkout_class.return_value.build_checkout_request_form.assert_called_once_with(
            self.cart,
            success_url=self.callback_success_url,
            fail_url=self.callback_error_url
            )
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(form_html in resp.body)

    @mock.patch('altair.app.ticketing.checkout.api.AnshinCheckoutAPI')
    def test_complete(self, checkout_class):
        from datetime import datetime
        class dummy_datetime(datetime):
            @classmethod
            def now(cls):
                return cls(2014, 1, 1)
        with mock.patch('altair.app.ticketing.checkout.api.datetime', new_callable=lambda:dummy_datetime):
            with mock.patch('altair.app.ticketing.payments.plugins.checkout.datetime', new_callable=lambda:dummy_datetime):
                checkout = testing.DummyModel(
                    orderCartId=u'XX0000000000',
                    orderCartId_old=10
                    )
                dummy_response = '<dummy-response></dummy-response>'
                checkout_class.return_value.create_order_complete_response_xml.return_value = dummy_response
                checkout_class.return_value.save_order_complete.return_value = checkout
                resp = self.test_app.post(self.COMPLETE_URL, {})
                checkout_class.return_value.create_order_complete_response_xml.assert_called_once_with(0, dummy_datetime.now())
                checkout_class.return_value.save_order_complete.assert_called_once()
                self.assertEqual(resp.status_code, 200)
                self.assertTrue(dummy_response in resp.body)
