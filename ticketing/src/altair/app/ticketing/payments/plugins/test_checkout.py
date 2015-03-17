import unittest
import mock
from pyramid import testing
from webtest import TestApp
from altair.app.ticketing.testing import _setup_db, _teardown_db
from altair.app.ticketing.core.testing import CoreTestMixin
import threading

class RWLock(object):
    class TLS(threading.local):
        lock_type = None

    def __init__(self):
        self.rcl = threading.Condition()
        self.wl = threading.Lock()
        self.rc = 0
        self.tls = self.TLS()

    def acquire_w(self):
        if self.tls.lock_type == 'w':
            return
        elif self.tls.lock_type == 'r':
            self.release_r()
        self.rcl.acquire()
        self.tls.lock_type = 'w'
        if self.rc > 0:
            self.rcl.wait()
        self.wl.acquire()

    def release_w(self):
        self.wl.release()
        self.tls.lock_type = None
        self.rcl.release()

    def acquire_r(self):
        if self.tls.lock_type is not None:
            return
        self.rcl.acquire()
        self.tls.lock_type = 'r'
        self.rc += 1
        self.rcl.release()

    def release_r(self):
        self.rcl.acquire()
        self.rc -= 1
        if self.rc == 0:
            self.rcl.notify()
        self.tls.lock_type = None
        self.rcl.release()

    def release(self):
        lock_type = self.tls.lock_type
        if lock_type == 'w':
            self.release_w()
        elif lock_type == 'r':
            self.release_r()
        else:
            raise Exception('WTF?')


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
        from altair.app.ticketing.core.models import (
            SalesSegmentGroup,
            SalesSegment,
            PaymentDeliveryMethodPair,
            DateCalculationBase,
            )
        from altair.app.ticketing.cart.models import Cart, CartSetting
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
        self.cart_setting = CartSetting(type='standard')
        self.session.add(self.cart_setting)
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
            payment_start_day_calculation_base=DateCalculationBase.OrderDate.v,
            payment_start_in_days=0,
            payment_due_day_calculation_base=DateCalculationBase.OrderDate.v,
            payment_period_days=3,
            issuing_start_day_calculation_base=DateCalculationBase.OrderDate.v,
            issuing_interval_days=5,
            issuing_end_day_calculation_base=DateCalculationBase.OrderDate.v,
            issuing_end_in_days=364,
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
        config.include('pyramid_mako')
        config.include('altair.pyramid_dynamic_renderer')
        config.add_mako_renderer('.html')
        config.include('altair.mobile')
        config.include('altair.browserid')
        config.include('altair.app.ticketing.cart.request')
        config.include('altair.app.ticketing.payments')
        config.include('altair.app.ticketing.payments.plugins')
        config.add_view(self._set_cart, route_name='set_cart')
        config.add_route('set_cart', self.SET_CART_URL)
        config.add_route('payment.checkout.login', self.LOGIN_URL)
        config.add_route('payment.checkout.order_complete', self.COMPLETE_URL)
        self.cart = Cart(
            id=10,
            cart_setting=self.cart_setting,
            performance=self.sales_segment.performance,
            sales_segment=self.sales_segment,
            payment_delivery_pair=self.payment_delivery_method_pair,
            _order_no='XX0000000000',
            created_at=datetime.now()
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
                    orderCartId=u'XX0000000000'
                    )
                dummy_response = '<dummy-response></dummy-response>'
                checkout_class.return_value.create_order_complete_response_xml.return_value = dummy_response
                checkout_class.return_value.save_order_complete.return_value = checkout
                resp = self.test_app.post(self.COMPLETE_URL, {})
                checkout_class.return_value.create_order_complete_response_xml.assert_called_once_with(0, dummy_datetime.now())
                checkout_class.return_value.save_order_complete.assert_called_once()
                self.assertEqual(resp.status_code, 200)
                self.assertTrue(dummy_response in resp.body)


class TestCheckoutLoginConcurrency(unittest.TestCase, CoreTestMixin):
    SET_CART_URL = '/set_cart'
    LOGIN_URL = '/checkout/login'

    def _dummy_root_factory(self, request):
        return testing.DummyResource()

    def patch_sqla_select(self):
        import sqlalchemy.sql
        self.prev_select_impl = sqlalchemy.sql.select
        def for_update_emulation(*args, **kwargs):
            for_update = self.tls.for_update = getattr(self.tls, 'for_update', False) or kwargs.pop('for_update', False)
            if for_update:
                self._acquire_conn_lock(True)
            return self.prev_select_impl(*args, **kwargs)
        sqlalchemy.sql.select = for_update_emulation

    def unpatch_sqla_select(self):
        import sqlalchemy.sql
        sqlalchemy.sql.select = self.prev_select_impl

    def _acquire_conn_lock(self, for_update):
        if for_update:
            self.conn_lock.acquire_w()
        else:
            self.conn_lock.acquire_r()

    def _release_conn_lock(self):
        self.conn_lock.release()
        self.tls.for_update = False

    def setUp(self):
        from decimal import Decimal
        from pyramid.config import Configurator
        from webtest import TestApp
        from altair.app.ticketing.core.models import (
            SalesSegmentGroup,
            SalesSegment,
            PaymentDeliveryMethodPair,
            DateCalculationBase,
            )
        from altair.app.ticketing.cart.models import Cart, CartSetting
        from altair.app.ticketing.checkout.models import RakutenCheckoutSetting
        from . import CHECKOUT_PAYMENT_PLUGIN_ID, SHIPPING_DELIVERY_PLUGIN_ID
        from datetime import datetime
        import tempfile
        from sqlalchemy import create_engine
        from altair.httpsession.pyramid import PyramidSessionFactory
        from altair.mobile.session import http_backend_factory 
        from altair.httpsession.pyramid.interfaces import ISessionHTTPBackendFactory, ISessionPersistenceBackendFactory
        from altair.httpsession.inmemory import factory as inmemory_session_backend_factory, stores as backing_session_stores

        self.tls = threading.local()
        self.tmp_db_file = tempfile.mktemp()
        engine = create_engine('sqlite:///' + self.tmp_db_file, echo=False)
        self.conn_lock = RWLock()
        prev_conn_factory = engine._connection_cls
        def conn_factory(*args, **kwargs):
            conn = prev_conn_factory(*args, **kwargs)
            prev_begin = conn.begin
            from sqlalchemy.engine.base import Transaction
            class WrappedTransaction(Transaction):
                def __init__(_self, inner):
                    _self.inner = inner
                    self._acquire_conn_lock(False)

                def close(_self):
                    self._release_conn_lock()
                    _self.inner.close()

                def rollback(_self):
                    self._release_conn_lock()
                    _self.inner.rollback()

                def commit(_self):
                    self._release_conn_lock()
                    _self.inner.commit()

            def patched_begin():
                return WrappedTransaction(prev_begin())
            conn.begin = patched_begin
            return conn
             
        engine._connection_cls = conn_factory
        self.session = _setup_db([
            'altair.app.ticketing.core.models',
            'altair.app.ticketing.orders.models',
            'altair.app.ticketing.lots.models',
            'altair.app.ticketing.cart.models',
            'altair.app.ticketing.checkout.models',
            ],
            engine=engine)
        CoreTestMixin.setUp(self)
        self.cart_setting = CartSetting(type='standard')
        self.session.add(self.cart_setting)
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
            payment_start_day_calculation_base=DateCalculationBase.OrderDate.v,
            payment_start_in_days=0,
            payment_due_day_calculation_base=DateCalculationBase.OrderDate.v,
            payment_period_days=3,
            issuing_start_day_calculation_base=DateCalculationBase.OrderDate.v,
            issuing_interval_days=5,
            issuing_end_day_calculation_base=DateCalculationBase.OrderDate.v,
            issuing_end_in_days=364,
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
            root_factory=self._dummy_root_factory
            )
        config.registry.registerUtility(
            lambda request: http_backend_factory(request, 'PHPSESSID', 'secret'),
            ISessionHTTPBackendFactory
            )
        config.registry.registerUtility(
            lambda request: inmemory_session_backend_factory(request),
            ISessionPersistenceBackendFactory
            )
        config.set_session_factory(PyramidSessionFactory())
        config.include('pyramid_mako')
        config.include('altair.pyramid_dynamic_renderer')
        config.add_mako_renderer('.html')
        config.include('altair.mobile')
        config.include('altair.browserid')
        config.include('altair.app.ticketing.cart.request')
        config.include('altair.app.ticketing.payments')
        config.include('altair.app.ticketing.payments.plugins')
        config.add_view(self._set_cart, route_name='set_cart')
        config.add_route('set_cart', self.SET_CART_URL)
        config.add_route('payment.checkout.login', self.LOGIN_URL)
        self.cart = Cart(
            id=10,
            cart_setting=self.cart_setting,
            performance=self.sales_segment.performance,
            sales_segment=self.sales_segment,
            payment_delivery_pair=self.payment_delivery_method_pair,
            _order_no='XX0000000000',
            created_at=datetime.now()
            )
        self.session.add(self.cart)
        self.patch_sqla_select()
        self.test_app = TestApp(config.make_wsgi_app())
        resp = self.test_app.get(self.SET_CART_URL)

    def tearDown(self):
        self.unpatch_sqla_select()
        _teardown_db()
        import os
        os.unlink(self.tmp_db_file)

    def _set_cart(self, context, request):
        from altair.app.ticketing.cart.api import set_cart
        from pyramid.httpexceptions import HTTPOk
        from altair.app.ticketing.cart.models import Cart
        cart = Cart.query.filter_by(id=10).first()
        set_cart(request, cart)
        self.callback_success_url = request.route_url('payment.checkout.callback.success')
        self.callback_error_url = request.route_url('payment.checkout.callback.error')
        return HTTPOk()

    def test_login(self):
        resps = set()
        def entrypoint():
            resp = self.test_app.post(self.LOGIN_URL, {})
            resps.add(resp.body)
        import transaction
        transaction.commit()
        threads = [threading.Thread(target=entrypoint) for _ in range(100)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        self.assertEqual(len(resps), 1)
        from altair.app.ticketing.checkout.models import Checkout
        checkout_objects = self.session.query(Checkout).filter_by(orderCartId='XX0000000000').all()
        self.assertEqual(len(checkout_objects), 1)
