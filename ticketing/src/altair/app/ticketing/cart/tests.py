# -*- coding:utf-8 -*-

import unittest
from pyramid import testing
from altair.multicheckout.testing import DummySecure3D
from ..testing import _setup_db as _setup_db_, _teardown_db, DummyRequest
import mock

def _setup_db(echo=False):
    return _setup_db_(
        modules=[
            'altair.app.ticketing.orders.models',
            'altair.app.ticketing.core.models',
            'altair.app.ticketing.cart.models',
            'altair.app.ticketing.users.models',
            'altair.multicheckout.models',
            ],
        echo=echo
        )

class TestIt(unittest.TestCase):
    _settings = {
                 'altair.cart.completion_page.temporary_store.cookie_name': '',
                 'altair.cart.completion_page.temporary_store.secret': '',
                 }

    def setUp(self):
        self.config = testing.setUp(settings=self._settings)
        self.config.include('altair.app.ticketing.cart')
        self.session = _setup_db()

    def tearDown(self):
        testing.tearDown()
        _teardown_db()

    def _set_payment_url(self):
        from . import api as a
        self.config.add_route('test.payment', 'payment/3d')
        request = DummyRequest()
        payment_method_manager = a.get_payment_method_manager(request)
        payment_method_manager.add_route_name('3', 'test.payment')

    def test_payment_method_url_multicheckout(self):
        from . import api as a
        self._set_payment_url()
        request = DummyRequest()
        result = a.get_payment_method_url(request, "3")

        self.assertEqual(result, "http://example.com/payment/3d")


class CartTests(unittest.TestCase):
    def setUp(self):
        self.session = _setup_db()
        self.request = DummyRequest()

    def tearDown(self):
        _teardown_db()
        import sqlahelper
        sqlahelper.get_base().metadata.drop_all()

    def _getTarget(self):
        from . import models
        return models.Cart

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def _add_cart(self, cart_session_id, performance, created_at=None):
        from datetime import datetime
        from . import models
        if created_at is None:
            created_at = datetime.now()
        cart = models.Cart(cart_session_id=cart_session_id, created_at=created_at, performance=performance, cart_setting=models.CartSetting(type='standard'))
        self.session.add(cart)
        return cart

    def test_total_amount_empty(self):
        from altair.app.ticketing.core.models import (
            PaymentDeliveryMethodPair,
            PaymentMethod,
            DeliveryMethod,
            Product,
            ProductItem,
            SalesSegment,
            SalesSegmentSetting,
            )
        target = self._makeOne(
            payment_delivery_pair=PaymentDeliveryMethodPair(
                transaction_fee=0,
                delivery_fee_per_order=0,
                delivery_fee_per_principal_ticket=0,
                delivery_fee_per_subticket=0,
                system_fee=0,
                payment_method=PaymentMethod(fee_type=0, fee=0),
                delivery_method=DeliveryMethod(fee_per_order=0, fee_per_principal_ticket=0, fee_per_subticket=0),
                discount=0
                ),
            sales_segment=SalesSegment(setting=SalesSegmentSetting())
            )
        self.assertEqual(target.total_amount, 0)

    def test_total_amount(self):
        from . import models
        from altair.app.ticketing.core.models import (
            PaymentDeliveryMethodPair,
            PaymentMethod,
            DeliveryMethod,
            Product,
            ProductItem,
            SalesSegment,
            SalesSegmentSetting,
            )
        target = self._makeOne(
            payment_delivery_pair=PaymentDeliveryMethodPair(
                transaction_fee=0,
                delivery_fee_per_order=0,
                delivery_fee_per_principal_ticket=0,
                delivery_fee_per_subticket=0,
                system_fee=0,
                payment_method=PaymentMethod(fee_type=0, fee=0),
                delivery_method=DeliveryMethod(fee_per_order=0, fee_per_principal_ticket=0, fee_per_subticket=0),
                discount=0
                ),
            sales_segment=SalesSegment(),
            products = [
                models.CartedProduct(quantity=10, product=Product(price=10)),
                models.CartedProduct(quantity=10, product=Product(price=20)),
                ]
            )
        self.assertEqual(target.total_amount, 300)

    def test_is_existing_cart_session_id_not_exsiting(self):
        target = self._getTarget()

        result = target.is_existing_cart_session_id(u"x")

        self.assertFalse(result)

    def test_is_existing_cart_session_id_existing(self):
        from altair.app.ticketing.core.models import Performance, Event, Organization
        performance = Performance(event=Event(organization=Organization(id=1, code='XX', short_name='XX')))
        self._add_cart(u"x", performance=performance)
        target = self._getTarget()

        result = target.is_existing_cart_session_id(u"x")

        self.assertTrue(result)

    def test_is_expired_instance_expired(self):
        from datetime import datetime, timedelta
        now = datetime.now()
        created = now - timedelta(minutes=16)
        target = self._makeOne(created_at=created)
        result = target.is_expired(15, now)
        self.assertTrue(result)

    def test_is_expired_instance(self):
        from datetime import datetime, timedelta
        now = datetime.now()
        created = now - timedelta(minutes=14)
        target = self._makeOne(created_at=created)
        result = target.is_expired(15, now)
        self.assertFalse(result, now)

    def test_is_expired_class(self):
        from datetime import datetime, timedelta
        from altair.app.ticketing.core.models import Performance, Event, Organization

        now = datetime.now()
        performance = Performance(event=Event(organization=Organization(id=1, code='XX', short_name='XX')))
        valid_created = now - timedelta(minutes=14)
        expired_created = now - timedelta(minutes=16)
        self._add_cart(u"valid", performance, created_at=valid_created)
        self._add_cart(u"expired", performance, created_at=expired_created)

        target = self._getTarget()
        result = target.query.filter(~target.is_expired(expire_span_minutes=15, now=now)).all()

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].cart_session_id, u'valid')

    def test_add_seats(self):
        from altair.app.ticketing.core.models import Product, ProductItem
        ordered_products = [
            (
                Product(
                    id=i,
                    items=[
                        ProductItem(stock_id=1, performance_id=1, quantity=1),
                        ]
                    ),
                1
                )
            for i in range(10)
            ]
        seats = [testing.DummyResource(id=i, stock_id=1) for i in range(10)]
        target = self._makeOne(performance_id=1)
        target.add_seat(seats, ordered_products)

        self.assertEqual(target.items[0].product.id, 0)
        self.assertEqual(target.items[0].quantity, 1)
        self.assertEqual(len(target.items[0].elements), 1)

    def test_add_products(self):
        from altair.app.ticketing.core.models import Product, ProductItem
        ordered_products = [
            (
                Product(
                    id=i,
                    items=[
                        ProductItem(stock_id=1, performance_id=1, quantity=1),
                        ]
                    ),
                1
                ) for i in range(10)
            ]
        target = self._makeOne(performance_id=1)
        target.add_products(ordered_products)

        self.assertEqual(target.items[0].product.id, 0)
        self.assertEqual(target.items[0].quantity, 1)
        self.assertEqual(len(target.items[0].elements), 1)


class CartedProductTests(unittest.TestCase):
    def setUp(self):
        self.session = _setup_db()

    def tearDown(self):
        _teardown_db()
        import sqlahelper
        sqlahelper.get_base().metadata.drop_all()


    def _getTarget(self):
        from . import models
        return models.CartedProduct

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_pop_seats(self):
        from altair.app.ticketing.core.models import Product, ProductItem, Seat
        product = Product(
            items=[
                ProductItem(stock_id=2, performance_id=1),
                ProductItem(stock_id=3, performance_id=1)
                ]
            )
        target = self._makeOne(id=1, product=product, quantity=1)
        result = target.pop_seats(
            [
                Seat(stock_id=1),
                Seat(stock_id=2),
                Seat(stock_id=3)
                ],
            performance_id=1
            )

        self.assertEqual(len(target.elements), 2)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].stock_id, 1)

    def test_amount(self):
        product = testing.DummyResource(price=150)
        target = self._makeOne(id=1, product=product, quantity=3)

        self.assertEqual(target.amount, 450)

class CartedProductItemTests(unittest.TestCase):
    def setUp(self):
        self.session = _setup_db()

    def tearDown(self):
        _teardown_db()
        import sqlahelper
        sqlahelper.get_base().metadata.drop_all()


    def _getTarget(self):
        from . import models
        return models.CartedProductItem

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_pop_seats(self):
        from altair.app.ticketing.core.models import ProductItem, Seat
        product_item = ProductItem(stock_id=2)
        target = self._makeOne(id=1, product_item=product_item, quantity=2)
        result = target.pop_seats([Seat(stock_id=1),
                                   Seat(stock_id=2),
                                   Seat(stock_id=2),
                                   Seat(stock_id=3),
                                   Seat(stock_id=2)])

        self.assertEqual(len(target.seats), 2)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0].stock_id, 1)
        self.assertEqual(result[1].stock_id, 3)
        self.assertEqual(result[2].stock_id, 2)

    def _add_seat(self, carted_product_item, quantity):
        from ..core import models as c_models

        seat_statuses = []
        organization = c_models.Organization(id=532, short_name='testing')
        site = c_models.Site(id=899)
        venue = c_models.Venue(id=100, site=site, organization=organization)
        for i in range(quantity):
            seat = c_models.Seat(id=i, venue=venue)
            status = c_models.SeatStatus(seat=seat, status=int(c_models.SeatStatusEnum.InCart))
            carted_product_item.seats.append(seat)
            seat_statuses.append(status)
            self.session.add(seat)
        return seat_statuses

    def test_finish(self):
        target = self._makeOne(id=1)
        statuses = self._add_seat(target, 10)
        target.finish()

        self._assertAllOrdered(statuses)

    def _assertAllOrdered(self, statuses):
        from ..core.models import SeatStatusEnum
        for s in statuses:
            self.assertEqual(s.status, int(SeatStatusEnum.Ordered))


class TicketingCartResourceTestBase(object):
    _settings = {'altair.cart.completion_page.temporary_store.cookie_name': '',
                 'altair.cart.completion_page.temporary_store.secret': '',
                 }
    def setUp(self):
        self.config = testing.setUp(settings=self._settings)
        self.config.include('altair.app.ticketing.cart')
        self.config.registry.settings['altair_cart.expire_time'] = '10'
        from altair.sqlahelper import register_sessionmaker_with_engine
        self.session = _setup_db()
        register_sessionmaker_with_engine(
            self.config.registry,
            'slave',
            self.session.bind
            )
        from .models import CartSetting
        self.cart_setting = CartSetting(type='standard')
        self.organization = self._add_organization(1)
        self.session.add(self.organization)
        self.session.flush()

    def tearDown(self):
        testing.tearDown()
        _teardown_db()
        import sqlahelper
        sqlahelper.get_base().metadata.drop_all()

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def _add_organization(self, organization_id):
        from ..core import models
        organization = models.Organization(
            id=organization_id,
            name='example',
            short_name='XX',
            hosts=[
                models.Host(
                    organization_id=organization_id,
                    host_name='example.com:80'
                    )
                ],
            settings=[
                models.OrganizationSetting(
                    cart_setting=self.cart_setting
                    )
                ]
            )
        return organization

    def _add_stock_status(self, quantity=100):
        from ..products import models
        product_item = models.ProductItem(id=1, price=0, quantity=0)
        stock = models.Stock(id=1, product_items=[product_item])
        stock_status = models.StockStatus(stock=stock, quantity=quantity)
        self.session.add(stock_status)
        return product_item

    def _add_event(self, event_id):
        from ..core import models
        event = models.Event(id=event_id, organization_id=self.organization.id)
        self.session.add(event)
        return event

    def _add_sales_segment(self, performance, start_at, end_at):
        from ..core import models
        sales_segment = models.SalesSegment(
            performance=performance,
            sales_segment_group=performance.event.sales_segment_groups[0],
            start_at=start_at,
            end_at=end_at,
            public=True,
            payment_delivery_method_pairs=[
                models.PaymentDeliveryMethodPair(
                    transaction_fee=0,
                    delivery_fee_per_order=0,
                    delivery_fee_per_principal_ticket=0,
                    delivery_fee_per_subticket=0,
                    system_fee=0,
                    payment_method=models.PaymentMethod(fee_type=0, fee=0),
                    delivery_method=models.DeliveryMethod(fee_per_order=0, fee_per_principal_ticket=0, fee_per_subticket=0),
                    discount=0
                    ),
                ]
            )
        self.session.add(sales_segment)
        return sales_segment

    @mock.patch("altair.app.ticketing.cart.api.get_organization")
    def test_membership_none(self, get_organization):
        from altair.app.ticketing.core.models import Performance, Event, Organization, SalesSegmentGroup, SalesSegmentKindEnum
        from datetime import datetime
        now = datetime(2012, 6, 20)
        organization = get_organization.return_value = Organization(code='XX', short_name='XX')

        event_id = 20L
        performance_id = 99L
        performance = Performance(
            id=performance_id,
            event=Event(
                id=event_id,
                organization=organization,
                sales_segment_groups=[SalesSegmentGroup(kind=SalesSegmentKindEnum.normal.k, public=True)]
                )
            )
        ss1 = self._add_sales_segment(performance=performance, start_at=datetime(2012, 6, 1), end_at=datetime(2012, 6, 30))
        ss2 = self._add_sales_segment(performance=performance, start_at=datetime(2012, 6, 21), end_at=datetime(2012, 6, 30))
        ss3 = self._add_sales_segment(performance=performance, start_at=datetime(2012, 6, 1), end_at=datetime(2012, 6, 19))
        self.session.flush()

        request = DummyRequest(matchdict={'event_id': event_id, 'sales_segment_id': ss1.id})
        target = self._makeOne(request)
        target.now = now
        result = target.memberships

        self.assertEqual(result, [])

    @mock.patch("altair.app.ticketing.cart.api.get_organization")
    def test_membership(self, get_organization):
        from altair.app.ticketing.users.models import Membership, MemberGroup
        from altair.app.ticketing.core.models import Event, Performance, Organization, SalesSegmentGroup, SalesSegmentKindEnum
        from datetime import datetime
        now = datetime(2012, 6, 20)
        organization = get_organization.return_value = Organization(short_name='XX', code='XX')

        event_id = 20L
        performance_id = 99L
        performance = Performance(
            id=performance_id,
            event=Event(
                id=event_id,
                organization=organization,
                sales_segment_groups=[
                    SalesSegmentGroup(public=True, kind=SalesSegmentKindEnum.normal.k)
                    ]
                ),
            public=True
            )
        ss1 = self._add_sales_segment(performance=performance, start_at=datetime(2012, 6, 1), end_at=datetime(2012, 6, 30))
        ss2 = self._add_sales_segment(performance=performance, start_at=datetime(2012, 6, 21), end_at=datetime(2012, 6, 30))
        ss3 = self._add_sales_segment(performance=performance, start_at=datetime(2012, 6, 1), end_at=datetime(2012, 6, 19))
        ms = Membership(organization=organization)
        mg = MemberGroup(membership=ms)
        ss1.membergroups.append(mg)
        self.session.flush()

        request = DummyRequest(matchdict={'event_id': event_id})
        request.registry.settings = { 'altair_cart.expire_time': '15' }
        target = self._makeOne(request)
        target.now = now
        result = target.memberships

        self.assertEqual(result, [ms])

    @mock.patch("altair.app.ticketing.cart.api.get_organization")
    def test_event_id(self, get_organization):
        from altair.app.ticketing.core.models import Organization
        organization = get_organization.return_value = self.organization
        event = self._add_event(12345L)
        self.session.flush()
        request = DummyRequest(matchdict={"event_id": str(event.id)})
        target = self._makeOne(request)
        result = target.event.id
        self.assertEqual(result, event.id)

    @mock.patch("altair.app.ticketing.cart.api.get_organization")
    def test_get_sales_segment(self, get_organization):
        from altair.app.ticketing.core.models import Event, Performance, Organization, SalesSegmentGroup, SalesSegmentKindEnum
        from datetime import datetime
        now = datetime(2012, 6, 20)
        organization = get_organization.return_value = Organization(short_name='XX', code='XX')

        event_id = 20L
        performance_id = 99L
        performance = Performance(
            id=performance_id,
            event=Event(
                id=event_id,
                organization=organization,
                sales_segment_groups=[SalesSegmentGroup(public=True, kind=SalesSegmentKindEnum.normal.k)]
                ),
            public=True
            )
        ss1 = self._add_sales_segment(performance=performance, start_at=datetime(2012, 6, 1), end_at=datetime(2012, 6, 30))
        ss2 = self._add_sales_segment(performance=performance, start_at=datetime(2012, 6, 21), end_at=datetime(2012, 6, 30))
        ss3 = self._add_sales_segment(performance=performance, start_at=datetime(2012, 6, 1), end_at=datetime(2012, 6, 19))
        self.session.flush()

        request = DummyRequest(matchdict={'event_id': event_id, 'sales_segment_id': ss1.id})
        request.registry.settings = { 'altair_cart.expire_time': "15" }
        target = self._makeOne(request)
        target.now = now
        result = target.get_sales_segment()

        self.assertIsNotNone(result)
        self.assertEqual(result.id, ss1.id)

    def _add_venue(self, organization_id, site_id, venue_id):
        from altair.app.ticketing.core.models import Venue, Site
        from ..core.models import Organization
        organization = Organization(id=organization_id, short_name='testing')
        site = Site(id=site_id)
        venue = Venue(id=venue_id, site=site, organization_id=organization.id)
        return venue

    def _add_orders_user(self, order_limit=None, max_quantity_per_user=None):
        from altair.app.ticketing.core.models import (
            SalesSegment,
            SalesSegmentSetting,
            Performance,
            PerformanceSetting,
            Event,
            EventSetting,
            )
        from altair.app.ticketing.orders.models import Order
        from altair.app.ticketing.cart.models import Cart
        from altair.app.ticketing.users.models import User
        from datetime import datetime
        performance = Performance(
            setting=PerformanceSetting(),
            event=Event(setting=EventSetting())
            )
        self.session.add(performance)
        sales_segment = SalesSegment(
            event=performance.event,
            performance=performance,
            setting=SalesSegmentSetting(
                order_limit=order_limit,
                max_quantity_per_user=max_quantity_per_user
                )
            )
        self.session.add(sales_segment)
        user = User()
        self.session.add(user)
        other = User()
        self.session.add(other)
        orders = []
        for i in range(2):
            cart = Cart(sales_segment=sales_segment, cart_setting=self.cart_setting)
            order = Order(
                user=user, cart=cart,
                sales_segment=sales_segment,
                total_amount=0,
                system_fee=0, transaction_fee=0, delivery_fee=0,
                issuing_start_at=datetime(1970, 1, 1),
                issuing_end_at=datetime(1970, 1, 1),
                payment_start_at=datetime(1970, 1, 1),
                payment_due_at=datetime(1970, 1, 1)
                )
            self.session.add(order)
            orders.append(order)

        cancels = []
        for i in range(2):
            cart = Cart(sales_segment=sales_segment, cart_setting=self.cart_setting)
            order = Order(
                user=user, cart=cart,
                sales_segment=sales_segment,
                total_amount=0, canceled_at=datetime.now(),
                system_fee=0, transaction_fee=0, delivery_fee=0,
                issuing_start_at=datetime(1970, 1, 1),
                issuing_end_at=datetime(1970, 1, 1),
                payment_start_at=datetime(1970, 1, 1),
                payment_due_at=datetime(1970, 1, 1)
                )
            self.session.add(order)
            cancels.append(order)

        others = []
        for i in range(2):
            cart = Cart(sales_segment=sales_segment, cart_setting=self.cart_setting)
            order = Order(
                user=other, cart=cart,
                sales_segment=sales_segment,
                total_amount=0,
                system_fee=0, transaction_fee=0, delivery_fee=0,
                issuing_start_at=datetime(1970, 1, 1),
                issuing_end_at=datetime(1970, 1, 1),
                payment_start_at=datetime(1970, 1, 1),
                payment_due_at=datetime(1970, 1, 1)
                )
            self.session.add(order)
            others.append(order)

        self.session.add(sales_segment)
        self.session.flush()
        return sales_segment, user

    @mock.patch('altair.app.ticketing.cart.api.get_user')
    @mock.patch('altair.app.ticketing.cart.api.get_cart_safe')
    def test_check_order_limit_noset(self, get_cart_safe, get_user):
        from .models import Cart
        from altair.app.ticketing.core.models import ShippingAddress
        sales_segment, user = self._add_orders_user()
        get_user.return_value = user
        get_cart_safe.return_value = Cart(
            sales_segment=sales_segment,
            cart_setting=self.cart_setting,
            shipping_address=ShippingAddress(
                user=user,
                email_1="testing@example.com"
                )
            )

        request = DummyRequest()
        target = self._makeOne(request)
        result = target.check_order_limit()
        self.assert_(True)

    @mock.patch('altair.app.ticketing.cart.api.get_user')
    @mock.patch('altair.app.ticketing.cart.api.get_cart_safe')
    def test_check_order_limit_user_over(self, get_cart_safe, get_user):
        from .models import Cart
        from .exceptions import OverOrderLimitException
        from altair.app.ticketing.core.models import ShippingAddress
        sales_segment, user = self._add_orders_user(order_limit=1)
        get_user.return_value = user
        get_cart_safe.return_value = Cart(
            sales_segment=sales_segment,
            cart_setting=self.cart_setting,
            shipping_address=ShippingAddress(
                user=user,
                email_1="testing@example.com"
                )
            )

        request = DummyRequest()
        target = self._makeOne(request)

        with self.assertRaises(OverOrderLimitException):
            target.check_order_limit()

    @mock.patch('altair.app.ticketing.cart.api.get_user')
    @mock.patch('altair.app.ticketing.cart.api.get_cart_safe')
    def test_check_order_limit_user_under(self, get_cart_safe, get_user):
        from .models import Cart
        from altair.app.ticketing.core.models import ShippingAddress
        sales_segment, user = self._add_orders_user(order_limit=3)
        get_user.return_value = user
        get_cart_safe.return_value = Cart(
            sales_segment=sales_segment,
            cart_setting=self.cart_setting,
            shipping_address=ShippingAddress(
                user=user,
                email_1="testing@example.com"
                )
            )

        request = DummyRequest()
        target = self._makeOne(request)

        try:
            target.check_order_limit()
            self.assert_(True)
        except:
            self.fail()

    def _add_orders_email(self, order_limit=None, max_quantity_per_user=None):
        from .models import Cart
        from altair.app.ticketing.core.models import (
            SalesSegment,
            SalesSegmentSetting,
            ShippingAddress,
            Performance,
            PerformanceSetting,
            Event,
            EventSetting,
            )
        from altair.app.ticketing.orders.models import (
            Order,
            )
        from datetime import datetime
        performance = Performance(
            setting=PerformanceSetting(),
            event=Event(setting=EventSetting())
            )
        sales_segment = SalesSegment(
            event=performance.event,
            performance=performance,
            setting=SalesSegmentSetting(
                order_limit=order_limit,
                max_quantity_per_user=max_quantity_per_user
                )
            )
        self.session.add(sales_segment)
        orders = []
        for i in range(2):
            cart = Cart(sales_segment=sales_segment, cart_setting=self.cart_setting)
            order = Order(
                cart=cart,
                sales_segment=sales_segment,
                shipping_address=ShippingAddress(email_1="testing@example.com"),
                total_amount=0,
                system_fee=0, transaction_fee=0, delivery_fee=0,
                issuing_start_at=datetime(1970, 1, 1),
                issuing_end_at=datetime(1970, 1, 1),
                payment_start_at=datetime(1970, 1, 1),
                payment_due_at=datetime(1970, 1, 1)
                )
            self.session.add(order)
            orders.append(order)

        cancel = []
        for i in range(2):
            cart = Cart(sales_segment=sales_segment, cart_setting=self.cart_setting)
            order = Order(
                cart=cart,
                sales_segment=sales_segment,
                shipping_address=ShippingAddress(email_1="testing@example.com"),
                total_amount=0, canceled_at=datetime.now(),
                system_fee=0, transaction_fee=0, delivery_fee=0,
                issuing_start_at=datetime(1970, 1, 1),
                issuing_end_at=datetime(1970, 1, 1),
                payment_start_at=datetime(1970, 1, 1),
                payment_due_at=datetime(1970, 1, 1)
                )
            self.session.add(order)
            orders.append(order)

        others = []
        for i in range(2):
            cart = Cart(sales_segment=sales_segment, cart_setting=self.cart_setting)
            order = Order(
                cart=cart,
                sales_segment=sales_segment,
                shipping_address=ShippingAddress(email_1="other@example.com"),
                total_amount=0,
                system_fee=0, transaction_fee=0, delivery_fee=0,
                issuing_start_at=datetime(1970, 1, 1),
                issuing_end_at=datetime(1970, 1, 1),
                payment_start_at=datetime(1970, 1, 1),
                payment_due_at=datetime(1970, 1, 1)
                )
            self.session.add(order)
            others.append(order)

        self.session.add(sales_segment)
        self.session.flush()
        return sales_segment, None

    @mock.patch('altair.app.ticketing.cart.api.get_cart_safe')
    def test_check_order_limit_email_over(self, get_cart_safe):
        from .models import Cart
        from altair.app.ticketing.core.models import ShippingAddress
        from .exceptions import OverOrderLimitException
        sales_segment, user = self._add_orders_email(order_limit=1)
        get_cart_safe.return_value = Cart(
            sales_segment=sales_segment,
            cart_setting=self.cart_setting,
            shipping_address=ShippingAddress(
                user=user,
                email_1="testing@example.com"
                )
            )
        self.session.add(get_cart_safe.return_value)
        self.session.flush()
        request = DummyRequest()
        target = self._makeOne(request)
        with self.assertRaises(OverOrderLimitException):
            target.check_order_limit()

    @mock.patch('altair.app.ticketing.cart.api.get_cart_safe')
    def test_check_order_limit_email_under(self, get_cart_safe):
        from .models import Cart
        from altair.app.ticketing.core.models import ShippingAddress
        sales_segment, user = self._add_orders_email(order_limit=3)
        get_cart_safe.return_value = Cart(
            sales_segment=sales_segment,
            cart_setting=self.cart_setting,
            shipping_address=ShippingAddress(
                user=user,
                email_1="testing@example.com"
                )
            )
        self.session.add(get_cart_safe.return_value)
        self.session.flush()
        request = DummyRequest()
        target = self._makeOne(request)

        try:
            target.check_order_limit()
            self.assert_(True)
        except:
            self.fail()

class EventOrientedTicketingCartResourceTests(unittest.TestCase, TicketingCartResourceTestBase):
    def setUp(self):
        TicketingCartResourceTestBase.setUp(self)

    def tearDown(self):
        TicketingCartResourceTestBase.tearDown(self)

    def _getTarget(self):
        from . import resources
        return resources.EventOrientedTicketingCartResource

class ReserveViewTests(unittest.TestCase):
    def setUp(self):
        self.session = _setup_db()
        self.config = testing.setUp()

    def tearDown(self):
        _teardown_db()
        import sqlahelper
        sqlahelper.get_base().metadata.drop_all()

    def _getTarget(self):
        from .views import ReserveView
        return ReserveView

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_order_items_empty(self):
        context = mock.Mock()
        request = DummyRequest()
        target = self._makeOne(context, request)
        result = target.ordered_items

        self.assertEqual(list(result), [])

    def test_order_items(self):
        from altair.app.ticketing.core.models import Product
        p1 = Product(id=1, price=100)
        p2 = Product(id=2, price=150)
        self.session.add(p1)
        self.session.add(p2)
        params = {
            "product-1": '10',
            "a": 'aaa',
            "product-a": 'x',
            "product-2": '20',
            }
        context = mock.Mock()
        request = DummyRequest(params=params)
        target = self._makeOne(context, request)
        result = target.iter_ordered_items()

        self.assertEqual(list(result), [("1", 10), ("2", 20)])

    def test_ordered_items(self):
        from altair.app.ticketing.core.models import Product
        p1 = Product(id=1, price=100)
        p2 = Product(id=2, price=150)
        self.session.add(p1)
        self.session.add(p2)
        params = {
            "product-1": '10',
            "a": 'aaa',
            "product-a": 'x',
            "product-2": '20',
            }
        context = mock.Mock()
        request = DummyRequest(params=params)
        target = self._makeOne(context, request)
        result = target.ordered_items

        self.assertEqual(list(result), [(p1, 10), (p2, 20)])


    def _add_venue(self, organization_id, site_id, venue_id):
        from altair.app.ticketing.core.models import Venue, Site
        from ..core.models import Organization
        organization = Organization(id=organization_id, short_name='testing')
        site = Site(id=site_id)
        venue = Venue(id=venue_id, site=site, organization_id=organization.id)
        return venue

    @mock.patch("altair.app.ticketing.cart.request.get_organization")
    def test_it(self, get_organization):
        from altair.app.ticketing.core.models import (
            Seat,
            SeatAdjacency,
            Seat_SeatAdjacency,
            SeatAdjacencySet,
            SeatStatus,
            SeatStatusEnum,
            Stock,
            StockType,
            StockStatus,
            Product,
            ProductItem,
            Performance,
            Event,
            EventSetting,
            SalesSegment,
            SalesSegmentSetting,
            SalesSegmentGroup,
            SalesSegmentKindEnum,
            Organization,
            Host,
            PaymentDeliveryMethodPair,
            SeatIndex,
            SeatIndexType,
            )
        from .models import Cart, CartSetting
        from .resources import EventOrientedTicketingCartResource
        from webob.multidict import MultiDict
        from datetime import datetime, timedelta

        self.config.include('.request')
        self.config.add_route('cart.payment', 'payment')
        # 在庫
        stock_id = 1
        product_item_id = 2
        adjacency_set_id = 3
        adjacency_id = 4
        venue_id = 5
        site_id = 6
        organization_id = 7
        performance_id = 8
        sales_segment_id = 9
        event_id = 10
        sales_segment_group_id = 11

        now = datetime.now()
        get_organization.return_value = organization = Organization(id=organization_id, short_name='XX', code='XX')
        venue = self._add_venue(organization_id, site_id, venue_id)
        venue.performance_id = performance_id
        stock = Stock(id=stock_id, quantity=100, performance_id=performance_id, stock_type=StockType(quantity_only=False))
        stock_status = StockStatus(stock_id=stock.id, quantity=100)
        seats = [Seat(id=i, stock_id=stock.id, venue=venue, l0_id='s%s' % i) for i in range(2)]
        seat_statuses = [SeatStatus(seat_id=i, status=int(SeatStatusEnum.Vacant)) for i in range(2)]
        event = Event(
            id=event_id,
            organization=organization,
            setting=EventSetting(
                cart_setting=CartSetting(type='standard')
                )
            )
        performance = Performance(id=performance_id, event=event, public=True)
        sales_segment_group = SalesSegmentGroup(id=sales_segment_group_id, event=event, kind=SalesSegmentKindEnum.normal.k, public=True)
        sales_segment = SalesSegment(
            id=sales_segment_id, performance=performance, sales_segment_group=sales_segment_group,
            start_at=now - timedelta(days=1), end_at=now + timedelta(days=1), public=True, max_quantity=10,
            payment_delivery_method_pairs=[
                PaymentDeliveryMethodPair(system_fee=0, transaction_fee=0, delivery_fee_per_order=0, delivery_fee_per_principal_ticket=0, delivery_fee_per_subticket=0, discount=0)
                ],
            seat_choice=True,
            setting=SalesSegmentSetting(
                display_seat_no=True
                )
            )
        product_item = ProductItem(id=product_item_id, stock_id=stock.id, price=100, quantity=1, performance=performance)
        product = Product(id=1, price=100, items=[product_item], name=u"S席", sales_segment=sales_segment)
        self.session.add(performance)
        self.session.add(stock)
        self.session.add(product)
        self.session.add(product_item)
        self.session.add(stock_status)
        for seat in seats:
            self.session.add(seat)
        for seat_status in seat_statuses:
            self.session.add(seat_status)

        # SeatIndex
        self.session.add(SeatIndexType(venue=venue, name='',
            seat_indexes=[SeatIndex(seat=seat, index=1) for seat in seats]))

        # 座席隣接状態
        adjacency = SeatAdjacency(id=adjacency_id)
        adjacency_set = SeatAdjacencySet(
            site=venue.site,
            id=adjacency_set_id,
            seat_count=len(seats),
            adjacencies=[adjacency]
            )
        self.session.add(adjacency_set)
        self.session.flush()
        for seat in seats:
            self.session.add(Seat_SeatAdjacency(seat_adjacency_id=adjacency.id, l0_id=seat.l0_id))
        self.assertEqual(adjacency.seats_filter_by_venue(venue.id), seats)

        params = MultiDict({
            "performance_id": performance.id,
            "product-" + str(product.id): '2',
            })

        request = DummyRequest(params=params, matchdict={ 'event_id': str(event_id), 'sales_segment_id': str(sales_segment_id) })
        request.registry.settings = { 'altair_cart.expire_time': "15" }
        from pyramid.interfaces import IRequest
        from .interfaces import IStocker, IReserving, ICartFactory
        from .stocker import Stocker
        from .reserving import Reserving
        from .carting import CartFactory
        request.registry.adapters.register([IRequest], IStocker, "", Stocker)
        request.registry.adapters.register([IRequest], IReserving, "", Reserving)
        request.registry.adapters.register([IRequest], ICartFactory, "", CartFactory)
        context = request.context = EventOrientedTicketingCartResource(request)
        target = self._makeOne(context, request)
        result = target.reserve()

        import transaction
        transaction.commit()

        self.assertEqual(result, {
            'cart': {
                'products': [
                    {
                        'name': u'S席',
                        'price': 100,
                        'quantity': 2,
                        'seats': [{'l0_id': 's0', 'name': u''},
                                  {'l0_id': 's1', 'name': u''}],
                        'unit_template': u'{{num}}枚',
                        }
                    ],
                'total_amount': '200',
                'separate_seats': False,
                },
            'result': 'OK',
            'payment_url': 'http://example.com/payment',
            })
        cart_id = request.session['altair.app.ticketing.cart_id']

        self.session.remove()
        cart = self.session.query(Cart).filter(Cart.id==cart_id).one()

        self.assertIsNotNone(cart)
        self.assertEqual(len(cart.items), 1)
        self.assertEqual(len(cart.items[0].elements), 1)
        self.assertEqual(cart.items[0].elements[0].quantity, 2)

        from sqlalchemy import sql
        stock_statuses = self.session.bind.execute(sql.select([StockStatus.quantity]).where(StockStatus.stock_id==stock_id))
        for stock_status in stock_statuses:
            self.assertEqual(stock_status.quantity, 98)

    @mock.patch("altair.app.ticketing.cart.request.get_organization")
    def test_it_no_stock(self, get_organization):
        from altair.app.ticketing.core.models import (
            Seat,
            SeatAdjacency,
            Seat_SeatAdjacency,
            SeatAdjacencySet,
            SeatStatus,
            SeatStatusEnum,
            Stock,
            StockType,
            StockStatus,
            Product,
            ProductItem,
            Performance,
            Event,
            SalesSegment,
            SalesSegmentSetting,
            SalesSegmentGroup,
            SalesSegmentKindEnum,
            Organization,
            Host,
            PaymentDeliveryMethodPair,
            SeatIndex,
            SeatIndexType,
            )
        from altair.app.ticketing.cart.models import Cart
        from .resources import EventOrientedTicketingCartResource
        from webob.multidict import MultiDict
        from datetime import datetime, timedelta

        self.config.include('.request')

        now = datetime.now()

        # 在庫
        stock_id = 1
        product_item_id = 2
        adjacency_set_id = 3
        adjacency_id = 4
        venue_id = 5
        site_id = 6
        organization_id = 7
        performance_id = 8
        sales_segment_id = 9
        event_id = 10
        sales_segment_group_id = 11

        get_organization.return_value = organization = Organization(id=organization_id, short_name='XX', code='XX')
        venue = self._add_venue(organization_id, site_id, venue_id)
        venue.performance_id = performance_id
        stock = Stock(id=stock_id, quantity=100, performance_id=performance_id, stock_type=StockType(quantity_only=False))
        stock_status = StockStatus(stock_id=stock.id, quantity=0)
        seats = [Seat(id=i, stock_id=stock.id, venue=venue, l0_id='s%s' % i) for i in range(5)]
        seat_statuses = [SeatStatus(seat_id=i, status=int(SeatStatusEnum.InCart)) for i in range(5)]
        event = Event(id=event_id, organization=organization)
        performance = Performance(id=performance_id, event=event, public=True)
        sales_segment_group = SalesSegmentGroup(id=sales_segment_group_id, event=event, kind=SalesSegmentKindEnum.normal.k)
        sales_segment = SalesSegment(
            id=sales_segment_id, performance_id=performance_id, sales_segment_group=sales_segment_group,
            start_at=now - timedelta(days=1), end_at=now + timedelta(days=1), public=True, max_quantity=10,
            payment_delivery_method_pairs=[
                PaymentDeliveryMethodPair(system_fee=0, transaction_fee=0, delivery_fee_per_order=0, delivery_fee_per_principal_ticket=0, delivery_fee_per_subticket=0, discount=0)
                ],
            setting=SalesSegmentSetting(
                display_seat_no=True
                )
            )
        product_item = ProductItem(id=product_item_id, stock_id=stock.id, price=100, quantity=1, performance=performance)
        product = Product(id=1, price=100, items=[product_item], sales_segment=sales_segment)
        self.session.add(performance)
        self.session.add(stock)
        self.session.add(product)
        self.session.add(product_item)
        self.session.add(stock_status)
        [self.session.add(s) for s in seats]
        [self.session.add(s) for s in seat_statuses]

        # 座席隣接状態
        adjacency = SeatAdjacency(id=adjacency_id)
        adjacency_set = SeatAdjacencySet(
            site=venue.site,
            id=adjacency_set_id,
            seat_count=len(seats),
            adjacencies=[adjacency]
            )
        self.session.add(adjacency_set)
        self.session.flush()
        for seat in seats:
            self.session.add(Seat_SeatAdjacency(seat_adjacency_id=adjacency.id, l0_id=seat.l0_id))

        params = MultiDict({
            "performance_id": performance.id,
            "product-" + str(product.id): '2',
            })

        request = DummyRequest(params=params, matchdict={ 'event_id': str(event_id), 'sales_segment_id': str(sales_segment_id) })
        request.registry.settings = { 'altair_cart.expire_time': "15" }
        from pyramid.interfaces import IRequest
        from .interfaces import IStocker, IReserving, ICartFactory
        from .stocker import Stocker
        from .reserving import Reserving
        from .carting import CartFactory
        request.registry.adapters.register([IRequest], IStocker, "", Stocker)
        request.registry.adapters.register([IRequest], IReserving, "", Reserving)
        request.registry.adapters.register([IRequest], ICartFactory, "", CartFactory)
        context = request.context = EventOrientedTicketingCartResource(request)
        target = self._makeOne(context, request)
        result = target.reserve()

        self.assertEqual(result, dict(reason='stock', result='NG'))
        cart_id = request.session.get('altair.app.ticketing.cart_id')
        self.assertIsNone(cart_id)

    def test_iter_ordered_items(self):
        params = [
            ("product-10", '2'),
            ("product-11", '0'),
            ("product-12", '10'),
            ]

        class DummyParams(object):
            def __init__(self, params):
                self.params = params

            def iteritems(self):
                for k, v in self.params:
                    yield k, v

        context = mock.Mock()
        request = DummyRequest(params=DummyParams(params))
        target = self._makeOne(context, request)
        result = list(target.iter_ordered_items())

        self.assertEqual(len(result), 3)
        self.assertEqual(result[0], ('10', 2))
        self.assertEqual(result[1], ('11', 0))
        self.assertEqual(result[2], ('12', 10))


class PaymentViewTests(unittest.TestCase):

    def _add_cart(self, cart_session_id, performance, created_at=None):
        from datetime import datetime
        from . import models
        if created_at is None:
            created_at = datetime.now()
        cart = models.Cart(cart_session_id=cart_session_id, created_at=created_at, performance=performance, cart_setting=models.CartSetting(type='standard'))
        self.session.add(cart)
        return cart


    def _getTarget(self):
        from . import views
        return views.PaymentView

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def setUp(self):
        self.config = testing.setUp()
        self.session = _setup_db()

    def tearDown(self):
        testing.tearDown()
        _teardown_db()

    def _register_starndard_payment_methods(self):
        from ..core import models
        self.session.add(models.PaymentMethod(id=1, name=u"セブン-イレブン", fee=100))
        self.session.add(models.PaymentMethod(id=2, name=u"楽天ID決済", fee=100))
        self.session.add(models.PaymentMethod(id=3, name=u"クレジットカード", fee=100))
        self.config.add_route('route.1', 'sej')
        self.config.add_route('route.2', 'checkout')
        self.config.add_route('route.3', 'multi')
        from . import interfaces
        class DummyMethodManager(object):
            def get_route_name(self, id):
                return 'route.%s' % id
        dummy_method_manager = DummyMethodManager()
        self.config.registry.utilities.register([], interfaces.IPaymentMethodManager, "", dummy_method_manager)

    def test_it_no_cart(self):
        from .exceptions import NoCartError
        from .resources import EventOrientedTicketingCartResource
        request = DummyRequest()
        context = request.context = EventOrientedTicketingCartResource(request)
        request.registry.settings = { 'altair_cart.expire_time': "15" }
        target = self._makeOne(context, request)
        with self.assertRaises(NoCartError):
            target.get()

    @mock.patch('altair.app.ticketing.cart.api.check_if_payment_delivery_method_pair_is_applicable')
    def test_it(self, check_if_payment_delivery_method_pair_is_applicable):
        check_if_payment_delivery_method_pair_is_applicable.return_value = True
        from datetime import datetime, timedelta
        from altair.app.ticketing.core.models import Performance, Event, Organization, PaymentDeliveryMethodPair
        self._register_starndard_payment_methods()
        request = DummyRequest()
        request.registry.settings = {'altair_cart.expire_time': "15"}

        payment_method = testing.DummyModel(payment_plugin_id=1)
        delivery_method = testing.DummyModel(delivery_plugin_id=1)
        payment_method.public = True

        payment_delivery_method_pair = testing.DummyModel()
        payment_delivery_method_pair.payment_method = payment_method
        payment_delivery_method_pair.delivery_method = delivery_method

        performance = Performance(event=Event(organization=Organization(id=1, code='XX', short_name='XX')))
        cart = self._add_cart(u'x', performance=performance)

        cart_setting = testing.DummyModel(type='standard', flavors={}, default_prefecture=u'沖縄県')
        context = request.context = testing.DummyResource(
            request=request,
            read_only_cart=cart,
            cart_setting=cart_setting,
            cart=testing.DummyModel(
                cart_setting=cart_setting,
                performance=testing.DummyModel(
                    event=testing.DummyModel(
                        id="this-is-event-id",
                        ),
                    start_on=datetime(2013, 1, 1, 0, 0, 0)
                    ),
                is_expired=lambda minutes, now: False,
                finished_at=None,
                ),
            available_payment_delivery_method_pairs = lambda sales_segment: [payment_delivery_method_pair],
            authenticated_user = lambda: {
                'membership_source': 'rakuten',
                'claimed_id': 'http://ticketstar.example.com/user/1',
                'auth_identifier': 'http://ticketstar.example.com/user/1',
                'membership': 'membership',
                'organization_id': 1
                },
            get_payment_delivery_method_pair = lambda: payment_delivery_method_pair,
            sales_segment = testing.DummyModel()
            )
        target = self._makeOne(context, request)
        result = target.get()
        self.assertEqual(result['payment_delivery_methods'], [payment_delivery_method_pair])


class PaymentContext(testing.DummyResource):
    pass


class DummyViewFactory(object):
    def __init__(self, response_text):
        self.response_text = response_text

    def __call__(self, request):
        request.response.text = self.response_text
        return request.response

class FormRendererTests(unittest.TestCase):

    def _getTarget(self):
        from formrenderer import FormRenderer
        return FormRenderer

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_errors(self):
        from wtforms.form import Form
        from wtforms.fields import TextField
        from wtforms.validators import Required
        from webob.multidict import MultiDict

        class DummyForm(Form):
            req_text = TextField(validators=[Required()])

        data = MultiDict()
        f = DummyForm(data)
        f.validate()

        target = self._makeOne(f)
        result = target.errors("req_text")

        self.assertEqual(result, "<ul>\n<li>This field is required.</li>\n</ul>")

