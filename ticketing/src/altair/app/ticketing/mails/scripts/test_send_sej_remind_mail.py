import unittest
import mock
from pyramid.testing import setUp, tearDown
from altair.app.ticketing.testing import _setup_db, _teardown_db, DummyRequest
from altair.app.ticketing.core.testing import CoreTestMixin
from altair.app.ticketing.mails.testing import MailTestMixin

class TestGetTargetOrderNos(unittest.TestCase, CoreTestMixin):
    def setUp(self):
        self.session = _setup_db([
            'altair.app.ticketing.orders.models',
            'altair.app.ticketing.core.models',
            'altair.app.ticketing.sej.models'
            ])
        from altair.app.ticketing.sej.models import _session
        _session.remove()
        _session.configure(bind=self.session.bind)
        CoreTestMixin.setUp(self)
        from altair.app.ticketing.core.models import SalesSegment, SalesSegmentGroup
        self.sales_segment_group = SalesSegmentGroup(event=self.event)
        self.payment_delivery_method_pairs = self._create_payment_delivery_method_pairs(self.sales_segment_group)
        self.sales_segment = SalesSegment(performance=self.performance, sales_segment_group=self.sales_segment_group)
        self.stock_types = self._create_stock_types(1)
        self.stocks = self._create_stocks(self.stock_types)
        self.seats = self._create_seats(self.stocks)
        self.products = self._create_products(self.stocks, sales_segment=self.sales_segment)

    def tearDown(self):
        _teardown_db()

    def _getTarget(self):
        from .send_payment_remind_mail import get_sej_target_order_nos
        return get_sej_target_order_nos

    def _callFUT(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_it(self):
        from datetime import date, datetime
        from altair.app.ticketing.sej.models import SejOrder
        from altair.app.ticketing.payments.plugins import SEJ_PAYMENT_PLUGIN_ID
        from altair.app.ticketing.core.models import OrganizationSetting
        from altair.app.ticketing.orders.models import Order, OrderNotification
        self.organization.settings = [OrganizationSetting(notify_remind_mail=True)]
        order_0 = self._create_order([(self.products[0], 1)], pdmp=[pdmp for pdmp in self.payment_delivery_method_pairs if pdmp.payment_method.payment_plugin_id == SEJ_PAYMENT_PLUGIN_ID][0])
        self.session.add(order_0)
        self.session.add(SejOrder(order_no=order_0.order_no, payment_due_at=datetime(2014, 1, 1, 0, 0, 0)))
        order_1 = self._create_order([(self.products[0], 1)], pdmp=[pdmp for pdmp in self.payment_delivery_method_pairs if pdmp.payment_method.payment_plugin_id == SEJ_PAYMENT_PLUGIN_ID][0])
        self.session.add(order_1)
        self.session.add(SejOrder(order_no=order_1.order_no, payment_due_at=datetime(2014, 1, 2, 0, 0, 0)))
        order_2 = self._create_order([(self.products[0], 1)], pdmp=[pdmp for pdmp in self.payment_delivery_method_pairs if pdmp.payment_method.payment_plugin_id == SEJ_PAYMENT_PLUGIN_ID][0])
        self.session.add(order_2)
        self.session.add(SejOrder(order_no=order_2.order_no, payment_due_at=datetime(2014, 1, 3, 0, 0, 0)))
        order_3 = self._create_order([(self.products[0], 1)], pdmp=[pdmp for pdmp in self.payment_delivery_method_pairs if pdmp.payment_method.payment_plugin_id == SEJ_PAYMENT_PLUGIN_ID][0])
        self.session.add(order_3)
        self.session.add(SejOrder(order_no=order_3.order_no, payment_due_at=datetime(2014, 1, 3, 0, 0, 1)))
        self.session.flush()
        order_nos = self._callFUT(date(2014, 1, 1))
        self.assertEqual({order_1.order_no, order_2.order_no}, set(order_nos))

    def test_paid(self):
        from datetime import date, datetime
        from altair.app.ticketing.sej.models import SejOrder
        from altair.app.ticketing.payments.plugins import SEJ_PAYMENT_PLUGIN_ID
        from altair.app.ticketing.core.models import OrganizationSetting
        from altair.app.ticketing.orders.models import Order, OrderNotification
        self.organization.settings = [OrganizationSetting(notify_remind_mail=True)]
        order_0 = self._create_order([(self.products[0], 1)], pdmp=[pdmp for pdmp in self.payment_delivery_method_pairs if pdmp.payment_method.payment_plugin_id == SEJ_PAYMENT_PLUGIN_ID][0])
        self.session.add(order_0)
        self.session.add(SejOrder(order_no=order_0.order_no, payment_due_at=datetime(2014, 1, 2, 0, 0, 0)))
        order_1 = self._create_order([(self.products[0], 1)], pdmp=[pdmp for pdmp in self.payment_delivery_method_pairs if pdmp.payment_method.payment_plugin_id == SEJ_PAYMENT_PLUGIN_ID][0])
        self.session.add(order_1)
        self.session.add(SejOrder(order_no=order_1.order_no, payment_due_at=datetime(2014, 1, 3, 0, 0, 0)))
        order_2 = self._create_order([(self.products[0], 1)], pdmp=[pdmp for pdmp in self.payment_delivery_method_pairs if pdmp.payment_method.payment_plugin_id == SEJ_PAYMENT_PLUGIN_ID][0])
        order_2.paid_at = datetime(2014, 1, 1, 10, 0, 0)
        self.session.add(order_2)
        self.session.add(SejOrder(order_no=order_2.order_no, payment_due_at=datetime(2014, 1, 3, 0, 0, 0)))
        self.session.flush()
        order_nos = self._callFUT(date(2014, 1, 1))
        self.assertEqual({order_0.order_no, order_1.order_no, order_2.order_no}, set(order_nos))
        order_nos = self._callFUT(date(2014, 1, 2))
        self.assertEqual({order_1.order_no}, set(order_nos))


    def test_disabled_by_organization_setting(self):
        from datetime import date, datetime
        from altair.app.ticketing.sej.models import SejOrder
        from altair.app.ticketing.payments.plugins import SEJ_PAYMENT_PLUGIN_ID
        from altair.app.ticketing.core.models import OrganizationSetting
        from altair.app.ticketing.orders.models import Order, OrderNotification
        self.organization.settings = [OrganizationSetting(notify_remind_mail=False)]
        order = self._create_order([(self.products[0], 1)], pdmp=[pdmp for pdmp in self.payment_delivery_method_pairs if pdmp.payment_method.payment_plugin_id == SEJ_PAYMENT_PLUGIN_ID][0])
        self.session.add(order)
        self.session.add(SejOrder(order_no=order.order_no, payment_due_at=datetime(2014, 1, 2, 0, 0, 0)))
        self.session.flush()
        order_nos = self._callFUT(date(2014, 1, 1))
        self.assertEqual([], order_nos)

class TestScript(unittest.TestCase, CoreTestMixin, MailTestMixin):
    def setUp(self):
        self.session = _setup_db([
            'altair.app.ticketing.orders.models',
            'altair.app.ticketing.core.models',
            'altair.app.ticketing.sej.models'
            ])
        from altair.app.ticketing.sej.models import _session
        _session.remove()
        _session.configure(bind=self.session.bind)
        CoreTestMixin.setUp(self)
        from altair.app.ticketing.core.models import SalesSegment, SalesSegmentGroup, SalesSegmentSetting
        self.sales_segment_group = SalesSegmentGroup(event=self.event)
        self.payment_delivery_method_pairs = self._create_payment_delivery_method_pairs(self.sales_segment_group)
        self.sales_segment = SalesSegment(performance=self.performance, sales_segment_group=self.sales_segment_group, setting=SalesSegmentSetting(display_seat_no=True))
        self.stock_types = self._create_stock_types(1)
        self.stocks = self._create_stocks(self.stock_types)
        self.seats = self._create_seats(self.stocks)
        self.products = self._create_products(self.stocks, sales_segment=self.sales_segment)
        self.request = DummyRequest()
        self.config = setUp(settings={}, request=self.request)
        self.config.include('pyramid_mailer')
        self.config.include('pyramid_mako')
        self.config.include('altair.app.ticketing.mails')
        self.config.add_mako_renderer('.txt')
        self.registerDummyMailer()

    def tearDown(self):
        _teardown_db()
        tearDown()

    def _getTarget(self):
        from .send_payment_remind_mail import send_sej_payment_remind_mail
        return send_sej_payment_remind_mail

    def _callFUT(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    @mock.patch('altair.app.ticketing.mails.scripts.send_payment_remind_mail.datetime')
    def test_it(self, _datetime):
        from datetime import date, time, datetime, timedelta
        from altair.app.ticketing.sej.models import SejOrder
        from altair.app.ticketing.payments.plugins import SEJ_PAYMENT_PLUGIN_ID
        from altair.app.ticketing.core.models import OrganizationSetting
        from altair.app.ticketing.orders.models import Order, OrderNotification
        _datetime.datetime = datetime
        _datetime.time = time
        _datetime.timedelta = timedelta
        _datetime.date.today.return_value = date(2014, 1, 1)
        self.organization.settings = [OrganizationSetting(notify_remind_mail=True)]
        order_0 = self._create_order([(self.products[0], 1)], pdmp=[pdmp for pdmp in self.payment_delivery_method_pairs if pdmp.payment_method.payment_plugin_id == SEJ_PAYMENT_PLUGIN_ID][0])
        self.session.add(order_0)
        self.session.add(SejOrder(order_no=order_0.order_no, payment_due_at=datetime(2014, 1, 1, 0, 0, 0), order_at=datetime(2013, 12, 1, 0, 0, 0)))
        order_1 = self._create_order([(self.products[0], 1)], pdmp=[pdmp for pdmp in self.payment_delivery_method_pairs if pdmp.payment_method.payment_plugin_id == SEJ_PAYMENT_PLUGIN_ID][0])
        self.session.add(order_1)
        self.session.add(SejOrder(order_no=order_1.order_no, payment_due_at=datetime(2014, 1, 2, 0, 0, 0), order_at=datetime(2013, 12, 2, 0, 0, 0)))
        order_2 = self._create_order([(self.products[0], 1)], pdmp=[pdmp for pdmp in self.payment_delivery_method_pairs if pdmp.payment_method.payment_plugin_id == SEJ_PAYMENT_PLUGIN_ID][0])
        self.session.add(order_2)
        self.session.add(SejOrder(order_no=order_2.order_no, payment_due_at=datetime(2014, 1, 3, 0, 0, 0), order_at=datetime(2013, 12, 3, 0, 0, 0)))
        order_3 = self._create_order([(self.products[0], 1)], pdmp=[pdmp for pdmp in self.payment_delivery_method_pairs if pdmp.payment_method.payment_plugin_id == SEJ_PAYMENT_PLUGIN_ID][0])
        self.session.add(order_3)
        self.session.add(SejOrder(order_no=order_3.order_no, payment_due_at=datetime(2014, 1, 3, 0, 0, 1), order_at=datetime(2013, 12, 4, 0, 0, 0)))
        self.session.flush()
        self._callFUT(self.config.registry.settings)
        from pyramid_mailer import get_mailer
        mailer = get_mailer(self.request)
        self.assertEqual(len(mailer.outbox), 2)


